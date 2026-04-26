from contextlib import contextmanager

from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from src.config.settings import Settings


settings = Settings()

_pool: SimpleConnectionPool | None = None


def init_postgres_pool() -> None:
    """
    Initializes the PostgreSQL connection pool.
    Called during FastAPI lifespan startup.
    """
    global _pool

    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=settings.postgres_dsn,
        )


def close_postgres_pool() -> None:
    """
    Closes all PostgreSQL connections.
    Called during FastAPI lifespan shutdown.
    """
    global _pool

    if _pool is not None:
        _pool.closeall()
        _pool = None


@contextmanager
def get_pg_connection():
    """
    Provides a PostgreSQL connection from the pool.

    The transaction is committed on success and rolled back on error.
    """
    if _pool is None:
        raise RuntimeError("PostgreSQL pool not initialized.")

    conn = _pool.getconn()

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


def dict_cursor(conn):
    """
    Returns a RealDictCursor so SQL rows are represented as dictionaries.
    """
    return conn.cursor(cursor_factory=RealDictCursor)


def set_current_user(conn, user_id: str) -> None:
    """
    Sets the authenticated user in the PostgreSQL session.

    This is important for RLS policies that depend on:
    current_setting('app.current_user_id')
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.current_user_id', %s, true)",
            (user_id,),
        )