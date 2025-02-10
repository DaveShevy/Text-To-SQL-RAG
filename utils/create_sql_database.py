import os
import logging
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

logger = logging.getLogger(__name__)

DATA_FOLDER_NAME = "data"
DB_FILE_NAME = ""
EXCEL_FILE_NAME = ""
TABLE_NAME = ""

def ensure_db_created():
    """
    If the DB file doesn't exist, we create it from the Excel.
    If it exists, do nothing.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, "..", DATA_FOLDER_NAME)
    db_file_path = os.path.join(folder_path, DB_FILE_NAME)
    excel_file_path = os.path.join(folder_path, EXCEL_FILE_NAME)

    if os.path.exists(db_file_path):
        logger.info(f"DB file '{db_file_path}' exists. Skipping creation.")
        return

    logger.info("DB file not found. Creating from Excel.")
    create_survey_database()

def map_dtype_to_sqlalchemy(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return Integer
    elif pd.api.types.is_float_dtype(dtype):
        return Float
    else:
        return String

def create_survey_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(base_dir, "..", DATA_FOLDER_NAME)
    db_file_path = os.path.join(folder_path, DB_FILE_NAME)
    excel_file_path = os.path.join(folder_path, EXCEL_FILE_NAME)

    if not os.path.exists(excel_file_path):
        logger.error(f"Excel file not found at {excel_file_path}.")
        return

    df = pd.read_excel(excel_file_path)
    if df.empty:
        logger.error("Excel file is empty.")
        return

    engine = create_engine(f"sqlite:///{db_file_path}")
    metadata_obj = MetaData()

    columns = [
        Column(col, map_dtype_to_sqlalchemy(dtype))
        for col, dtype in zip(df.columns, df.dtypes)
    ]
    if not columns:
        logger.error("No valid columns found in Excel.")
        return

    table = Table(TABLE_NAME, metadata_obj, *columns)

    try:
        metadata_obj.create_all(engine)
        df.to_sql(TABLE_NAME, con=engine, index=False, if_exists='replace')
        logger.info(f"Database created at: {db_file_path}")
    except Exception as e:
        logger.error(f"Error creating DB: {e}")
    finally:
        engine.dispose()
