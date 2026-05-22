from typing import List

from psycopg2.extensions import connection as PgConnection


def list_active_user_email_enc(conn: PgConnection) -> List[str]:
    """Returns EMAIL_ENC of active users who completed first access."""
    query = """
        SELECT EMAIL_ENC
        FROM TB_USER
        WHERE ACTIVE = TRUE
          AND DELETED_AT IS NULL
          AND FIRST_ACCESS_COMPLETED = TRUE
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return [row[0] for row in rows]
