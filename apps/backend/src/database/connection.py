import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from pymongo import MongoClient
from src.config.settings import Settings

settings = Settings()

_pg_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=settings.postgres_dsn
)

@contextmanager
def get_postgres_connection():
    conn = _pg_pool.getconn()
    try:
        yield conn
    finally:
        _pg_pool.putconn(conn)


_client: MongoClient | None = None

def get_client() -> MongoClient:
    if _client is None:
        raise RuntimeError("MongoDB client not initialized. Check lifespan setup.")
    return _client

def get_db():
    return get_client()[settings.mongo_db_name]