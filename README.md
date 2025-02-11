# AI Assistant with SQL Querying and OpenAI Integration

This repository contains a virtual assistant application that integrates an AI chatbot with a SQL database, allowing users to query structured data through natural language input. The assistant leverages Azure OpenAI, SQLAlchemy, and Streamlit for its core functionalities.

## Features
- **Natural Language SQL Queries:** Users can ask questions, and the assistant translates them into SQL queries.
- **Azure OpenAI Integration:** Uses OpenAI's chat model for processing user queries and structuring SQL queries.
- **Streamlit UI:** Provides a web interface for interaction.
- **SQLite Database Support:** Stores and retrieves structured data efficiently.

---

## Project Structure

```
📁 project-root
│-- main.py                  # Core logic for query processing and AI interactions
│-- config.py                # Configuration settings and environment variables
│-- streamlit.py             # Streamlit-based UI for interacting with the assistant
│-- connect_sql_database.py  # Handles database connection and reflection
│-- create_sql_database.py   # Creates and initializes the SQL database from an Excel file
│-- helpers.py               # Utility functions for retrieving distinct database values
```

---

## Installation

### Prerequisites
- Python 3.8+
- Required dependencies listed in `requirements.txt`

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/ai-assistant.git
   cd ai-assistant
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example` for reference) and place them in a `.env` file.
4. Run the Streamlit UI:
   ```sh
   streamlit run streamlit.py
   ```

---

## Configuration
The application requires environment variables set in a `.env` file. The main configurations are in `config.py`:

- **Azure OpenAI Credentials:**
  ```python
  AZURE_OPENAI_API_KEY = get_env_variable('AZURE_OPENAI_API_KEY')
  AZURE_OPENAI_ENDPOINT = get_env_variable('AZURE_OPENAI_ENDPOINT')
  AZURE_OPENAI_DEPLOYMENT_NAME = get_env_variable('AZURE_OPENAI_DEPLOYMENT_NAME')
  ```
- **Database Settings:**
  ```python
  DB_FILE_NAME = "database.db"
  DATA_FOLDER_NAME = "data"
  TABLE_NAME = "public_scores"
  ```

---

## Usage
1. Start the Streamlit interface using `streamlit run streamlit.py`.
2. Type in your question related to the database (e.g., "Which agency had the lowest score?").
3. The assistant will generate an SQL query, execute it, and return the result.

---

## Database Management
- **Creating the Database:** The database is automatically created from an Excel file using `create_sql_database.py`.
- **Connecting to the Database:** `connect_sql_database.py` handles database connections and reflections.
- **Extracting Distinct Values:** `helpers.py` retrieves distinct column values for query optimization.

---

## Logging
The application logs important events in `app.log`. Logging levels can be adjusted in `streamlit.py` and `main.py` using Python's `logging` module.

---

## Future Improvements
- Expand support for additional SQL databases.
- Enhance natural language understanding for complex queries.
- Improve UI/UX with additional filtering options.

---

