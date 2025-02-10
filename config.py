import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

def get_env_variable(var_name):
    val = os.getenv(var_name)
    if not val:
        logger.error(f"Env var '{var_name}' is not set.")
        raise EnvironmentError(f"Env var '{var_name}' is not set.")
    return val

# --------------------------
# Azure OpenAI Credentials
# --------------------------
AZURE_OPENAI_API_KEY = get_env_variable('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = get_env_variable('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_DEPLOYMENT_NAME = get_env_variable('AZURE_OPENAI_DEPLOYMENT_NAME')
AZURE_OPENAI_MODEL_VERSION = "2023-07-01-preview"

# -------------------------
# SQLite Database Config
# -------------------------
DB_FILE_NAME = ""
DATA_FOLDER_NAME = ""
TABLE_NAME = ""

# Only columns we want to reflect
INCLUDED_COLUMNS = [

]

# Columns for which we want distinct values
DISTINCT_VALUE_COLUMNS = [
]

# Optional for descriptive prompts (Currently tailored to DUMMY DATA)
COLUMN_METADATA = {

}

def create_shared_state(engine, table, sql_database, distinct_values: dict):
    """
    Create a dictionary with references to the engine, table, etc., for reuse.
    """
    state = {
        "engine": engine,
        "table": table,
        "sql_database": sql_database,
        "columns": INCLUDED_COLUMNS,
        "column_metadata": COLUMN_METADATA,
        "distinct_values": distinct_values
    }
    return state

AGENT_MAX_DEPTH = 3
