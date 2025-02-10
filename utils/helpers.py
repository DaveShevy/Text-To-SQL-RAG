
import logging
from sqlalchemy import select, distinct

logger = logging.getLogger(__name__)

def get_distinct_values(engine, table, columns):
    """
    Retrieve distinct values from a partial-reflected table's columns.
    """
    distinct_vals = {}
    with engine.connect() as conn:
        for col in columns:
            try:
                query = select(distinct(table.c[col]))
                rows = conn.execute(query).fetchall()
                vals = [r[0] for r in rows if r[0] is not None]
                distinct_vals[col] = vals
            except Exception as e:
                logger.warning(f"Cannot retrieve distinct for column '{col}': {e}")
                distinct_vals[col] = []
    return distinct_vals
