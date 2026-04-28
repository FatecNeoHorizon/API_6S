from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as PsycopgConnection

from src.config.settings import Settings


@contextmanager
def get_postgres_connection() -> PsycopgConnection:
    settings = Settings()
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        sslmode=settings.postgres_sslmode,
    )
    try:
        yield conn
    finally:
        conn.close()
