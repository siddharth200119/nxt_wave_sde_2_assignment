import os
import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
from contextlib import contextmanager
from src.utils import logger

# Register UUID adapter for psycopg2
register_uuid()

import time


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASS", "postgres"),
        "dbname": os.getenv("DB_NAME", "test"),
    }


def check_db_health():
    """Check database connection status and measure latency"""
    start_time = time.perf_counter()
    try:
        with get_db_connection() as conn:
            # Simple query to verify connection
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "status": "connected",
                "latency_ms": round(latency_ms, 2)
            }
    except Exception as e:
        latency_ms = (time.perf_counter() - start_time) * 1000
        return {
            "status": "failed",
            "error": str(e),
            "latency_ms": round(latency_ms, 2)
        }


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    config = get_db_config()
    try:
        logger.debug(f"Connecting to database: {config['host']}:{config['port']}/{config['dbname']}")
        conn = psycopg2.connect(**config)
        logger.info(f"Database connection established")
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


class LoggingCursor:
    """Wrapper around RealDictCursor that logs queries and results"""

    def __init__(self, cursor):
        self._cursor = cursor
        self._last_query = None
        self._last_params = None

    def execute(self, query, params=None):
        self._last_query = query
        self._last_params = params
        
        # Clean up query for logging (remove extra whitespace)
        clean_query = " ".join(query.split())
        logger.info(f"Executing query: {clean_query}")
        if params:
            logger.debug(f"Query params: {params}")
        
        result = self._cursor.execute(query, params)
        
        rowcount = self._cursor.rowcount
        if rowcount >= 0:
            logger.info(f"Rows affected: {rowcount}")
        
        return result

    def fetchone(self):
        result = self._cursor.fetchone()
        if result:
            logger.debug(f"Fetched 1 row")
        else:
            logger.debug(f"No rows returned")
        return result

    def fetchall(self):
        results = self._cursor.fetchall()
        logger.info(f"Fetched {len(results)} rows")
        return results

    def fetchmany(self, size=None):
        results = self._cursor.fetchmany(size)
        logger.info(f"Fetched {len(results)} rows")
        return results

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def close(self):
        self._cursor.close()

    def __getattr__(self, name):
        return getattr(self._cursor, name)


@contextmanager
def get_db_cursor(commit=True):
    """Context manager for database cursor with auto-commit and logging"""
    with get_db_connection() as conn:
        raw_cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor = LoggingCursor(raw_cursor)
        try:
            yield cursor
            if commit:
                conn.commit()
                logger.debug("Transaction committed")
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error, transaction rolled back: {e}")
            raise
        finally:
            cursor.close()
