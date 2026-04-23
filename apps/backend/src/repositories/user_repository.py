from uuid import UUID
from psycopg2.extras import RealDictCursor


class ProfileNotFoundError(Exception):
    pass


def create_user(conn, data: dict) -> dict:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if data.get('profile_id') is None:
            cur.execute("SELECT PROFILE_UUID FROM TB_PROFILE WHERE PROFILE_NAME = 'ANALYST'")
            profile = cur.fetchone()
            if profile is None:
                raise ProfileNotFoundError("Perfil padrão 'ANALYST' não encontrado.")
            data['profile_id'] = str(profile['profile_uuid'])
        else:
            cur.execute("SELECT 1 FROM TB_PROFILE WHERE PROFILE_UUID = %s", (str(data['profile_id']),))
            if cur.fetchone() is None:
                raise ProfileNotFoundError(f"Perfil com ID '{data['profile_id']}' não encontrado.")
            data['profile_id'] = str(data['profile_id'])

        query = """
            INSERT INTO TB_USER (username, email_hash, email_enc, password_hash, profile_id)
            VALUES (%(username)s, %(email_hash)s, %(email_enc)s, %(password_hash)s, %(profile_id)s)
            RETURNING user_uuid, username, profile_id, active, created_at;
        """
        cur.execute(query, data)
        new_user = cur.fetchone()
        conn.commit()
        return new_user


def exists_by_username(conn, username: str, exclude_user_id: UUID = None) -> bool:
    with conn.cursor() as cur:
        if exclude_user_id:
            cur.execute(
                "SELECT 1 FROM TB_USER WHERE username = %s AND user_uuid != %s",
                (username, str(exclude_user_id))
            )
        else:
            cur.execute("SELECT 1 FROM TB_USER WHERE username = %s", (username,))
        return cur.fetchone() is not None


def exists_by_email_hash(conn, email_hash: str, exclude_user_id: UUID = None) -> bool:
    with conn.cursor() as cur:
        if exclude_user_id:
            cur.execute(
                "SELECT 1 FROM TB_USER WHERE email_hash = %s AND user_uuid != %s",
                (email_hash, str(exclude_user_id))
            )
        else:
            cur.execute("SELECT 1 FROM TB_USER WHERE email_hash = %s", (email_hash,))
        return cur.fetchone() is not None


def get_all_users(conn) -> list[dict]:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT user_uuid, username, profile_id, active, created_at 
            FROM TB_USER 
            WHERE deleted_at IS NULL
            ORDER BY created_at DESC;
        """
        cur.execute(query)
        return cur.fetchall()


def get_user_by_id(conn, user_id: UUID) -> dict | None:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        query = """
            SELECT user_uuid, username, profile_id, active, created_at 
            FROM TB_USER 
            WHERE user_uuid = %s AND deleted_at IS NULL;
        """
        cur.execute(query, (str(user_id),))
        return cur.fetchone()


def update_user(conn, user_id: UUID, fields: dict) -> dict | None:
    set_clauses = ", ".join(f"{key} = %({key})s" for key in fields)
    query = f"""
        UPDATE TB_USER
        SET {set_clauses}, updated_at = NOW()
        WHERE user_uuid = %(user_id)s AND deleted_at IS NULL
        RETURNING user_uuid, username, profile_id, active, created_at;
    """
    params = {**fields, "user_id": str(user_id)}

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        updated_user = cur.fetchone()
        conn.commit()
        return updated_user


def delete_user(conn, user_id: UUID) -> bool:
    query = """
        UPDATE TB_USER
        SET deleted_at = NOW()
        WHERE user_uuid = %s AND deleted_at IS NULL;
    """
    with conn.cursor() as cur:
        cur.execute(query, (str(user_id),))
        affected = cur.rowcount
        conn.commit()
        return affected > 0


def reactivate_user(conn, user_id: UUID) -> bool:
    query = """
        UPDATE TB_USER
        SET deleted_at = NULL
        WHERE user_uuid = %s AND deleted_at IS NOT NULL;
    """
    with conn.cursor() as cur:
        cur.execute(query, (str(user_id),))
        affected = cur.rowcount
        conn.commit()
        return affected > 0