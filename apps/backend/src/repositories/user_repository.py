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

def create_password_reset_token(
    conn: PgConnection,
    *,
    user_id: str,
    token_hash: str,
    expires_at,
) -> None:
    query = """
        INSERT INTO TB_PASSWORD_RESET (
            USER_UUID,
            TOKEN_HASH,
            EXPIRES_AT,
            USED_AT
        )
        VALUES (%s, %s, %s, NULL)
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (user_id, token_hash, expires_at))


def get_valid_password_reset_token(conn: PgConnection, token_hash: str):
    query = """
        SELECT
            pr.RESET_UUID,
            pr.USER_UUID,
            u.ACTIVE
        FROM TB_PASSWORD_RESET pr
        JOIN TB_USER u
          ON u.USER_UUID = pr.USER_UUID
        WHERE pr.TOKEN_HASH = %s
          AND pr.USED_AT IS NULL
          AND pr.EXPIRES_AT > NOW()
          AND u.DELETED_AT IS NULL
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (token_hash,))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "reset_uuid": row[0],
        "user_uuid": row[1],
        "active": row[2],
    }


def mark_password_reset_token_used(conn: PgConnection, reset_uuid: str) -> None:
    query = """
        UPDATE TB_PASSWORD_RESET
        SET USED_AT = NOW()
        WHERE RESET_UUID = %s
          AND USED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(reset_uuid),))


def update_user_password(conn: PgConnection, *, user_id: str, password_hash: str) -> None:
    query = """
        UPDATE TB_USER
        SET PASSWORD_HASH = %s,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (password_hash, str(user_id)))