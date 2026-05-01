from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from psycopg2.errors import  UniqueViolation
from psycopg2.extensions import connection as PgConnection

class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class UserProfileNotFoundError(Exception):
    pass

class UserPersistenceError(Exception):
    pass

class ProfilePersistenceError(Exception):
    pass

@dataclass
class UserCreateResult:
    user_uuid: UUID
    username: str
    profile_id: UUID
    active: bool
    created_at: datetime


@dataclass
class ProfileResult:
    profile_uuid: UUID
    profile_name: str

@dataclass
class UserResult:
    user_uuid: UUID
    username: str
    profile_id: UUID
    active: bool
    created_at: datetime
    updated_at: datetime


def create_user(conn: PgConnection, data: dict) -> UserCreateResult:
    query = """
        INSERT INTO TB_USER (
            USERNAME,
            EMAIL_HASH,
            EMAIL_ENC,
            PASSWORD_HASH,
            PROFILE_ID
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    data["username"],
                    data["email_hash"],
                    data["email_enc"],
                    data["password_hash"],
                    str(data["profile_id"]),
                ),
            )
            row = cursor.fetchone()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Nome de usuário ou e-mail já cadastrado.") from exc
    except Exception as exc:
        raise UserPersistenceError("Falha ao salvar o usuário no PostgreSQL.") from exc

    if row is None:
        raise UserPersistenceError("O PostgreSQL não retornou os dados do usuário criado.")

    return UserCreateResult(
        user_uuid=row[0],
        username=row[1],
        profile_id=row[2],
        active=row[3],
        created_at=row[4],
    )

def get_user_by_id(conn: PgConnection, user_uuid: UUID) -> Optional[UserResult]:
    query = """
        SELECT USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT, UPDATED_AT
        FROM TB_USER
        WHERE USER_UUID = %s AND DELETED_AT IS NULL
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_uuid),))
        row = cursor.fetchone()
    if row is None:
        return None
    return UserResult(user_uuid=row[0], username=row[1], profile_id=row[2], active=row[3], created_at=row[4], updated_at=row[5])

def list_users(conn: PgConnection) -> List[UserResult]:
    query = """
        SELECT USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT, UPDATED_AT
        FROM TB_USER WHERE DELETED_AT IS NULL ORDER BY CREATED_AT DESC
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return [UserResult(user_uuid=r[0], username=r[1], profile_id=r[2], active=r[3], created_at=r[4], updated_at=r[5]) for r in rows]

def exists_by_username(conn: PgConnection, username: str) -> bool:
    query = "SELECT 1 FROM TB_USER WHERE UPPER(USERNAME) = UPPER(%s) LIMIT 1"
    with conn.cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone() is not None

def exists_by_profile_id(conn: PgConnection, profile_id: UUID) -> bool:
    query = "SELECT 1 FROM TB_PROFILE WHERE PROFILE_UUID = %s AND DELETED_AT IS NULL LIMIT 1"
    with conn.cursor() as cursor:
        cursor.execute(query, (str(profile_id),))
        return cursor.fetchone() is not None

def exists_by_email_hash(conn: PgConnection, email_hash: str) -> bool:
    query = "SELECT 1 FROM TB_USER WHERE EMAIL_HASH = %s LIMIT 1"
    with conn.cursor() as cursor:
        cursor.execute(query, (email_hash,))
        return cursor.fetchone() is not None

def update_user(conn: PgConnection, user_uuid: UUID, data: dict) -> Optional[UserResult]:
    query = """
        UPDATE TB_USER SET USERNAME = %s, PROFILE_ID = %s, UPDATED_AT = NOW()
        WHERE USER_UUID = %s AND DELETED_AT IS NULL
        RETURNING USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT, UPDATED_AT
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (data["username"], str(data["profile_id"]), str(user_uuid)))
            row = cursor.fetchone()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Nome de usuário já cadastrado.") from exc
    if row is None:
        return None
    return UserResult(user_uuid=row[0], username=row[1], profile_id=row[2], active=row[3], created_at=row[4], updated_at=row[5])


def set_user_active(conn: PgConnection, user_uuid: UUID, active: bool) -> Optional[UserResult]:
    query = """
        UPDATE TB_USER SET ACTIVE = %s, UPDATED_AT = NOW()
        WHERE USER_UUID = %s AND DELETED_AT IS NULL
        RETURNING USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT, UPDATED_AT
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (active, str(user_uuid)))
        row = cursor.fetchone()
    if row is None:
        return None
    return UserResult(user_uuid=row[0], username=row[1], profile_id=row[2], active=row[3], created_at=row[4], updated_at=row[5])


def delete_user(conn: PgConnection, user_uuid: UUID) -> bool:
    query = """
        UPDATE TB_USER SET DELETED_AT = NOW(), UPDATED_AT = NOW()
        WHERE USER_UUID = %s AND DELETED_AT IS NULL
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_uuid),))
        return cursor.rowcount > 0

def list_profiles(conn: PgConnection) -> List[ProfileResult]:
    query = """
        SELECT PROFILE_UUID, PROFILE_NAME
        FROM TB_PROFILE
        WHERE DELETED_AT IS NULL
        ORDER BY PROFILE_NAME ASC
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except Exception as exc:
        raise ProfilePersistenceError("Falha ao buscar os perfis no PostgreSQL.") from exc

    return [
        ProfileResult(profile_uuid=row[0], profile_name=row[1])
        for row in rows
    ]

def get_user_auth_by_email_hash(conn: PgConnection, email_hash: str):
    query = """
        SELECT
            u.USER_UUID,
            u.USERNAME,
            u.EMAIL_HASH,
            u.PASSWORD_HASH,
            u.ACTIVE,
            u.FIRST_ACCESS_COMPLETED,
            p.PROFILE_NAME
        FROM TB_USER u
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = u.PROFILE_ID
        WHERE u.EMAIL_HASH = %s
          AND u.DELETED_AT IS NULL
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (email_hash,))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "user_uuid": row[0],
        "username": row[1],
        "email_hash": row[2],
        "password_hash": row[3],
        "active": row[4],
        "first_access_completed": row[5],
        "profile_name": row[6],
    }


def get_user_auth_by_id(conn: PgConnection, user_uuid: str):
    query = """
        SELECT
            u.USER_UUID,
            u.USERNAME,
            u.ACTIVE,
            u.FIRST_ACCESS_COMPLETED,
            p.PROFILE_NAME
        FROM TB_USER u
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = u.PROFILE_ID
        WHERE u.USER_UUID = %s
          AND u.DELETED_AT IS NULL
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_uuid),))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "user_uuid": row[0],
        "username": row[1],
        "active": row[2],
        "first_access_completed": row[3],
        "profile_name": row[4],
    }


def create_user_session(
    conn: PgConnection,
    *,
    user_id: str,
    source_ip: str,
    user_agent: str,
    expires_at,
):
    invalidate_query = """
        UPDATE TB_SESSION
        SET INVALIDATED_AT = NOW(),
            UPDATED_AT = NOW()
        WHERE USER_ID = %s
          AND INVALIDATED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(invalidate_query, (user_id,))

    insert_query = """
        INSERT INTO TB_SESSION (
            USER_ID,
            SOURCE_IP,
            USER_AGENT,
            EXPIRES_AT,
            INVALIDATED_AT
        )
        VALUES (%s, %s, %s, %s, NULL)
        RETURNING SESSION_UUID
    """

    with conn.cursor() as cursor:
        cursor.execute(
            insert_query,
            (
                user_id,
                source_ip,
                user_agent[:255],
                expires_at,
            ),
        )
        row = cursor.fetchone()

    return str(row[0])


def get_active_session_user(conn: PgConnection, session_uuid: str):
    query = """
        SELECT
            s.SESSION_UUID,
            u.USER_UUID,
            u.ACTIVE,
            u.FIRST_ACCESS_COMPLETED,
            p.PROFILE_NAME
        FROM TB_SESSION s
        JOIN TB_USER u
          ON u.USER_UUID = s.USER_ID
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = u.PROFILE_ID
        WHERE s.SESSION_UUID = %s
          AND s.INVALIDATED_AT IS NULL
          AND s.EXPIRES_AT > NOW()
          AND s.DELETED_AT IS NULL
          AND u.DELETED_AT IS NULL
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(session_uuid),))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "session_uuid": row[0],
        "user_uuid": row[1],
        "active": row[2],
        "first_access_completed": row[3],
        "profile_name": row[4],
    }