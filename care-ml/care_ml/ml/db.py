"""Database."""
from contextlib import contextmanager
import duckdb
from ..env_settings import DB_FILE

@contextmanager
def init_db():
    """Initialize database."""
    try:
        conn = duckdb.connect(database=DB_FILE)
        yield conn
    finally:
        conn.close()
