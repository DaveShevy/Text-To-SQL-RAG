"""
main.py

We assume 'messages' is a list of dicts like:
[
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."},
]
We do function-calling logic and return an UPDATED list of messages.
"""

import os
import json
import logging
import requests
import config
from utils.connect_sql_database import initialize_sql_database
from utils.helpers import get_distinct_values
from utils.create_sql_database import ensure_db_created

logger = logging.getLogger(__name__)

def initialize_backend():
    logger.info("Initializing backend (DB, Azure OpenAI).")
    ensure_db_created()
    db_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        config.DATA_FOLDER_NAME, config.DB_FILE_NAME
    )
    db_path = f"sqlite:///{db_file_path}"
    engine, table, sql_db = initialize_sql_database(db_path=db_path, table_name=config.TABLE_NAME)

    distinct_vals = get_distinct_values(engine=engine, table=table, columns=config.DISTINCT_VALUE_COLUMNS)
    state = config.create_shared_state(
        engine=engine, table=table, sql_database=sql_db, distinct_values=distinct_vals
    )
    return state

def build_schema_prompt(state):
    lines = []
    for col in state["columns"]:
        desc = state["column_metadata"].get(col, {}).get("description", "No desc")
        distinct_vals = state["distinct_values"].get(col, [])
        sample_vals = ", ".join(str(v) for v in distinct_vals[:15])
        lines.append(f"- **{col}** ({desc}): e.g. {sample_vals}")
    return "\n".join(lines)

def build_function_definition():
    return [
        {
            "name": "run_sql_query",
            "description": "Execute a SQL query on the 'public_scores' table and return rows as JSON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Valid SQL, e.g. SELECT * FROM public_scores WHERE ...;"
                    }
                },
                "required": ["query"]
            }
        }
    ]

def call_azure_chat_completion(messages, functions=None, function_call="auto"):
    url = f"{config.AZURE_OPENAI_ENDPOINT}/openai/deployments/{config.AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version={config.AZURE_OPENAI_MODEL_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": config.AZURE_OPENAI_API_KEY,
    }
    body = {
        "messages": messages,
        "functions": functions or [],
        "function_call": function_call,
    }
    resp = requests.post(url, headers=headers, json=body, timeout=30)
    if resp.status_code != 200:
        raise ValueError(f"Azure OpenAI error {resp.status_code}: {resp.text}")
    return resp.json()

def run_sql_query(query, engine):
    from sqlalchemy.sql import text
    logger.info(f"Running local SQL:\n{query}")
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(query)).fetchall()
            data = [list(r) for r in rows]
        return json.dumps(data)
    except Exception as e:
        logger.exception("SQL error")
        return json.dumps({"error": str(e)})

def process_user_query(conversation, state):
    """
    conversation: entire message history, including the last user message
    state: DB connection, distinct values, etc.

    We return an updated 'conversation' with function calls or final LLM text appended.
    """

    # 1) If there's no system prompt yet, add it at the top
    if not any(msg["role"] == "system" for msg in conversation):
        schema_str = build_schema_prompt(state)
        system_prompt = f"""
        You are an expert data assistant for 'table'.

        Columns and sample distinct values:
        {schema_str}

        If the user asks for the "lowest score" or "highest score" assume they mean the "lowest average score" or "highest average score" across all agencies.

        Your SQL queries should use **AVG(score)** instead of finding a single lowest score.

        For example:
        - If a user asks "Which agency had the lowest score?", interpret it as "Which agency has the lowest average score?"

        If user references a known value (like 'Havas SO Group'),
        check which column has that value, etc.

        NEVER say 'I cannot run queries'; you can call run_sql_query if needed.
        """
        conversation.insert(0, {"role": "system", "content": system_prompt.strip()})

    # 2) Call Azure
    function_list = build_function_definition()
    response_data = call_azure_chat_completion(conversation, functions=function_list, function_call="auto")
    choice = response_data["choices"][0]

    if choice["finish_reason"] == "function_call":
        func_name = choice["message"]["function_call"]["name"]
        args_str = choice["message"]["function_call"]["arguments"]
        logger.info(f"Model called function={func_name} with args={args_str}")

        if func_name == "run_sql_query":
            try:
                args_json = json.loads(args_str)
                sql_query = args_json.get("query", "")
            except:
                sql_query = ""

            # run local
            result_json = run_sql_query(sql_query, state["engine"])

            conversation.append({
                "role": "function",
                "name": func_name,
                "content": result_json
            })

            # Now do a second call with function_call="none" to get final answer
            final_resp = call_azure_chat_completion(conversation, functions=function_list, function_call="none")
            final_choice = final_resp["choices"][0]["message"]
            # This final text from the model:
            final_text = final_choice.get("content", "")
            conversation.append({"role": "assistant", "content": final_text})
            return conversation
        else:
            # unknown function
            conversation.append({"role": "assistant", "content": "Unknown function called."})
            return conversation
    else:
        # No function call => direct text
        assistant_msg = choice["message"].get("content", "")
        conversation.append({"role": "assistant", "content": assistant_msg})
        return conversation
