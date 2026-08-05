import os
import sys
import psycopg2
import logging
from contextlib import contextmanager
from src.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

logger = logging.getLogger(__name__)

def get_db_connection_raw():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
    except Exception as e:
        # Handle connection failures and terminate if DB is unreachable
        print(f"Database connection initialization failed: {e}")
        sys.exit(1)

@contextmanager
def get_db_connection():
    """Context manager wrapper around database connections for safe cleanup."""
    conn = None
    try:
        conn = get_db_connection_raw()
        yield conn
    except Exception as e:
        if conn:
            # Revert all changes if any part of the transaction fails
            conn.rollback()
            print(f"Transaction failed. Database state reverted. Error: {e}")
        raise
    finally:
        if conn:
            # Ensure database connection is closed regardless of outcome
            conn.close()