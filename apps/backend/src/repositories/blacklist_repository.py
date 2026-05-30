from uuid import UUID

from psycopg2.errors import UniqueViolation
from psycopg2.extensions import connection as PgConnection


class BlacklistPersistenceError(Exception):
    pass


def insert_blacklisted_user(conn: PgConnection, user_id: UUID) -> None:
    query = """
        INSERT INTO blacklist (USER_ID)
        VALUES (%s)
        ON CONFLICT (USER_ID) DO NOTHING
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (str(user_id),))
    except UniqueViolation:
        return
    except Exception as exc:
        raise BlacklistPersistenceError("Falha ao inserir usuario na blacklist.") from exc
