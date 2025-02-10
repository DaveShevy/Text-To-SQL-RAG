import logging
from sqlalchemy import create_engine, MetaData, Table
from llama_index.core import SQLDatabase
import config

logger = logging.getLogger(__name__)

def remove_unwanted_columns(table, keep_columns):
    for col in list(table.c):
        if col.name not in keep_columns:
            table.c._collection.remove(col.key)
            logger.info(f"Removed column '{col.name}' from reflection.")

def initialize_sql_database(db_path: str, table_name: str):
    """
    Creates a SQLAlchemy engine, partially reflects only config.INCLUDED_COLUMNS,
    then wraps it in a LlamaIndex SQLDatabase (though we won't do much with it now).
    """
    from sqlalchemy import MetaData, Table

    engine = create_engine(db_path)
    metadata_obj = MetaData()

    table = Table(
        table_name,
        metadata_obj,
        autoload_with=engine,
        include_columns=config.INCLUDED_COLUMNS
    )

    remove_unwanted_columns(table, set(config.INCLUDED_COLUMNS))

    sql_db = SQLDatabase(
        engine=engine,
        metadata=metadata_obj,
        include_tables=[table_name]
    )

    logger.info(
        f"Connected to DB at {db_path}, table '{table_name}' "
        f"partially reflected with columns: {config.INCLUDED_COLUMNS}"
    )

    return engine, table, sql_db

def run_local_sql(engine, query: str):
    """
    A helper if you want to run local SQL outside of function-calling.
    """
    from sqlalchemy.sql import text
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchall()
        return result
