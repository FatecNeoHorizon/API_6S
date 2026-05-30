from contextlib import contextmanager

from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from src.config.settings import Settings


settings = Settings()

_blacklist_pool: SimpleConnectionPool | None = None


def init_blacklist_pool() -> None:
    """
    Initializes the PostgreSQL connection pool for the blacklist database.
    """
    global _blacklist_pool

    if _blacklist_pool is None:
        _blacklist_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.blacklist_postgres_dsn,
        )


def close_blacklist_pool() -> None:
    """
    Closes all blacklist PostgreSQL connections.
    """
    global _blacklist_pool

    if _blacklist_pool is not None:
        _blacklist_pool.closeall()
        _blacklist_pool = None


def acquire_blacklist_connection():
    if _blacklist_pool is None:
        raise RuntimeError("Blacklist PostgreSQL pool not initialized.")

    return _blacklist_pool.getconn()


def release_blacklist_connection(conn) -> None:
    if _blacklist_pool is None:
        raise RuntimeError("Blacklist PostgreSQL pool not initialized.")

    _blacklist_pool.putconn(conn)


@contextmanager
def get_blacklist_connection():
    """
    Provides a PostgreSQL connection from the blacklist pool.

    The transaction is committed on success and rolled back on error.
    """
    conn = acquire_blacklist_connection()

    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        release_blacklist_connection(conn)


def dict_cursor(conn):
    """
    Returns a RealDictCursor so SQL rows are represented as dictionaries.
    """
    return conn.cursor(cursor_factory=RealDictCursor)
