from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from psycopg2.errors import UniqueViolation
from psycopg2.extensions import connection as PgConnection

from src.config.auth_security import is_valid_uuid


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
    profile_name: str
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
    profile_name: str
    active: bool
    created_at: datetime
    updated_at: datetime


def create_user(conn: PgConnection, data: dict) -> UserCreateResult:
    query = """
        INSERT INTO TB_USER (
            USERNAME,
            EMAIL_ENC,
            PROFILE_NAME,
            KEYCLOAK_SUB
        )
        VALUES (%s, %s, %s, %s)
        RETURNING USER_UUID, USERNAME, PROFILE_NAME, ACTIVE, CREATED_AT
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    data["username"],
                    data["email_enc"],
                    data["profile_name"],
                    data.get("keycloak_sub"),
                ),
            )
            row = cursor.fetchone()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Nome de usuário já cadastrado.") from exc
    except Exception as exc:
        raise UserPersistenceError("Falha ao salvar o usuário no PostgreSQL.") from exc

    if row is None:
        raise UserPersistenceError("O PostgreSQL não retornou os dados do usuário criado.")

    return UserCreateResult(
        user_uuid=row[0],
        username=row[1],
        profile_name=row[2],
        active=row[3],
        created_at=row[4],
    )


def get_user_by_id(conn: PgConnection, user_uuid: UUID) -> Optional[UserResult]:
    query = """
        SELECT USER_UUID, USERNAME, PROFILE_NAME, ACTIVE, CREATED_AT, UPDATED_AT
        FROM TB_USER
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_uuid),))
        row = cursor.fetchone()

    if row is None:
        return None

    return UserResult(
        user_uuid=row[0],
        username=row[1],
        profile_name=row[2],
        active=row[3],
        created_at=row[4],
        updated_at=row[5],
    )


def list_users(conn: PgConnection) -> List[UserResult]:
    query = """
        SELECT USER_UUID, USERNAME, PROFILE_NAME, ACTIVE, CREATED_AT, UPDATED_AT
        FROM TB_USER
        WHERE DELETED_AT IS NULL
        ORDER BY CREATED_AT DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return [
        UserResult(
            user_uuid=row[0],
            username=row[1],
            profile_name=row[2],
            active=row[3],
            created_at=row[4],
            updated_at=row[5],
        )
        for row in rows
    ]


def exists_by_username(conn: PgConnection, username: str) -> bool:
    query = """
        SELECT 1
        FROM TB_USER
        WHERE UPPER(USERNAME) = UPPER(%s)
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone() is not None


def get_current_user_profile(conn: PgConnection, user_uuid: str) -> dict | None:
    query = """
        SELECT
            USER_UUID,
            USERNAME,
            EMAIL_ENC,
            PROFILE_NAME,
            ACTIVE,
            CREATED_AT,
            UPDATED_AT
        FROM TB_USER
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
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
        "email_enc": row[2],
        "profile_name": row[3],
        "active": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }


def update_current_user_profile(
    conn: PgConnection,
    user_uuid: str,
    data: dict,
) -> dict | None:
    # Email uniqueness is now enforced by Keycloak; we only update EMAIL_ENC
    # (LGPD export copy) and USERNAME.
    query = """
        UPDATE TB_USER
        SET USERNAME = %s,
            EMAIL_ENC = %s,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
        RETURNING USER_UUID
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    data["username"],
                    data["email_enc"],
                    str(user_uuid),
                ),
            )
            row = cursor.fetchone()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Nome de usuário já cadastrado.") from exc

    if row is None:
        return None

    return get_current_user_profile(conn, user_uuid)


def update_user(conn: PgConnection, user_uuid: UUID, data: dict) -> Optional[UserResult]:
    query = """
        UPDATE TB_USER
        SET USERNAME = %s,
            PROFILE_NAME = %s,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
        RETURNING USER_UUID, USERNAME, PROFILE_NAME, ACTIVE, CREATED_AT, UPDATED_AT
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    data["username"],
                    data["profile_name"],
                    str(user_uuid),
                ),
            )
            row = cursor.fetchone()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Nome de usuário já cadastrado.") from exc

    if row is None:
        return None

    return UserResult(
        user_uuid=row[0],
        username=row[1],
        profile_name=row[2],
        active=row[3],
        created_at=row[4],
        updated_at=row[5],
    )


def set_user_active(
    conn: PgConnection,
    user_uuid: UUID,
    active: bool,
) -> Optional[UserResult]:
    query = """
        UPDATE TB_USER
        SET ACTIVE = %s,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
        RETURNING USER_UUID, USERNAME, PROFILE_NAME, ACTIVE, CREATED_AT, UPDATED_AT
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (active, str(user_uuid)))
        row = cursor.fetchone()

    if row is None:
        return None

    return UserResult(
        user_uuid=row[0],
        username=row[1],
        profile_name=row[2],
        active=row[3],
        created_at=row[4],
        updated_at=row[5],
    )


def delete_user(conn: PgConnection, user_uuid: UUID) -> bool:
    query = """
        UPDATE TB_USER
        SET DELETED_AT = NOW(),
            ACTIVE = FALSE,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
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
        ProfileResult(
            profile_uuid=row[0],
            profile_name=row[1],
        )
        for row in rows
    ]


def exists_by_profile_name(conn: PgConnection, profile_name: str) -> bool:
    query = """
        SELECT 1
        FROM TB_PROFILE
        WHERE UPPER(PROFILE_NAME) = UPPER(%s)
          AND DELETED_AT IS NULL
        LIMIT 1
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (profile_name,))
        return cursor.fetchone() is not None


def get_user_by_keycloak_sub(conn: PgConnection, keycloak_sub: str) -> Optional[dict]:
    query = """
        SELECT USER_UUID, ACTIVE
        FROM TB_USER
        WHERE KEYCLOAK_SUB = %s
          AND DELETED_AT IS NULL
        LIMIT 1
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (keycloak_sub,))
        row = cursor.fetchone()
    if row is None:
        return None
    return {
        "user_uuid": row[0],
        "active": row[1],
    }


def get_keycloak_sub(conn: PgConnection, user_uuid: UUID) -> Optional[str]:
    query = """
        SELECT KEYCLOAK_SUB
        FROM TB_USER
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
        LIMIT 1
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_uuid),))
        row = cursor.fetchone()
    return str(row[0]) if row and row[0] else None


def log_auth_attempt(
    conn: PgConnection,
    *,
    email_hash: str,
    source_ip: str,
    success: bool,
    blocked: bool,
) -> None:
    query = """
        INSERT INTO TB_AUTH_ATTEMPT (
            EMAIL_HASH,
            SOURCE_IP,
            SUCCESS,
            BLOCKED
        )
        VALUES (%s, %s, %s, %s)
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (
                email_hash,
                source_ip[:255],
                success,
                blocked,
            ),
        )


def invalidate_session(conn: PgConnection, session_id: str) -> bool:
    if not is_valid_uuid(session_id):
        return False

    query = """
        UPDATE TB_SESSION
        SET INVALIDATED_AT = NOW(),
            UPDATED_AT = NOW()
        WHERE SESSION_UUID = %s
          AND INVALIDATED_AT IS NULL
          AND DELETED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(session_id),))
        return cursor.rowcount > 0


def create_user_session(
    conn: PgConnection,
    *,
    user_id: str,
    source_ip: str,
    user_agent: str,
    expires_at,
    refresh_token_hash: str,
    refresh_expires_at,
) -> str:
    invalidate_user_sessions(conn, user_id)

    insert_query = """
        INSERT INTO TB_SESSION (
            USER_ID,
            SOURCE_IP,
            USER_AGENT,
            EXPIRES_AT,
            REFRESH_TOKEN_HASH,
            REFRESH_EXPIRES_AT,
            INVALIDATED_AT
        )
        VALUES (%s, %s, %s, %s, %s, %s, NULL)
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
                refresh_token_hash,
                refresh_expires_at,
            ),
        )
        row = cursor.fetchone()

    if row is None or row[0] is None:
        raise ValueError("Failed to create session: no UUID returned")

    session_uuid = str(row[0])

    if not is_valid_uuid(session_uuid):
        raise ValueError(f"Invalid session UUID format: {session_uuid}")

    return session_uuid


def rotate_refresh_token(
    conn: PgConnection,
    refresh_token_hash: str,
    new_refresh_token_hash: str,
    refresh_expires_at,
):
    query = """
        UPDATE TB_SESSION s
        SET REFRESH_TOKEN_HASH = %s,
            REFRESH_EXPIRES_AT = %s,
            EXPIRES_AT = %s,
            UPDATED_AT = NOW()
        FROM TB_USER u
        WHERE s.USER_ID = u.USER_UUID
          AND s.REFRESH_TOKEN_HASH = %s
          AND s.REFRESH_EXPIRES_AT > NOW()
          AND s.INVALIDATED_AT IS NULL
          AND s.DELETED_AT IS NULL
          AND u.DELETED_AT IS NULL
        RETURNING
            s.SESSION_UUID,
            u.USER_UUID,
            u.ACTIVE,
            u.PROFILE_NAME,
            u.USERNAME
    """

    with conn.cursor() as cursor:
        cursor.execute(
            query,
            (
                new_refresh_token_hash,
                refresh_expires_at,
                refresh_expires_at,
                refresh_token_hash,
            ),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "session_uuid": row[0],
        "user_uuid": row[1],
        "active": row[2],
        "profile_name": row[3],
        "username": row[4],
    }


def get_active_session_user(conn: PgConnection, session_uuid: str):
    query = """
        SELECT
            s.SESSION_UUID,
            u.USER_UUID,
            u.ACTIVE,
            u.PROFILE_NAME,
            u.USERNAME,
            s.INVALIDATED_AT,
            s.EXPIRES_AT,
            s.DELETED_AT,
            u.DELETED_AT as user_deleted_at
        FROM TB_SESSION s
        JOIN TB_USER u ON u.USER_UUID = s.USER_ID
        WHERE s.SESSION_UUID = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(session_uuid),))
        row = cursor.fetchone()

    if row is None:
        return None

    if row[5] is not None:  # INVALIDATED_AT
        return None

    if row[6] is not None:  # EXPIRES_AT
        now = datetime.now(timezone.utc)
        if row[6] <= now:
            return None

    if row[7] is not None:  # session DELETED_AT
        return None

    if row[8] is not None:  # user DELETED_AT
        return None

    return {
        "session_uuid": row[0],
        "user_uuid": row[1],
        "active": row[2],
        "profile_name": row[3],
        "username": row[4],
    }


def invalidate_user_sessions(conn: PgConnection, user_id: str) -> list[str]:
    query = """
        UPDATE TB_SESSION
        SET INVALIDATED_AT = NOW(),
            UPDATED_AT = NOW()
        WHERE USER_ID = %s
          AND INVALIDATED_AT IS NULL
        RETURNING SESSION_UUID::TEXT
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_user_sessions(conn: PgConnection, user_id: str) -> list[dict]:
    query = """
        SELECT
            SESSION_UUID,
            CREATED_AT,
            SOURCE_IP,
            USER_AGENT,
            EXPIRES_AT
        FROM TB_SESSION
        WHERE USER_ID = %s
          AND INVALIDATED_AT IS NULL
          AND DELETED_AT IS NULL
          AND EXPIRES_AT > NOW()
        ORDER BY CREATED_AT DESC
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
    return [
        {
            "session_uuid": row[0],
            "created_at": row[1],
            "source_ip": row[2],
            "user_agent": row[3],
            "expires_at": row[4],
        }
        for row in rows
    ]


def invalidate_single_session(
    conn: PgConnection, *, session_uuid: str, user_id: str
) -> bool:
    query = """
        UPDATE TB_SESSION
        SET INVALIDATED_AT = NOW(),
            UPDATED_AT = NOW()
        WHERE SESSION_UUID = %s
          AND USER_ID = %s
          AND INVALIDATED_AT IS NULL
        RETURNING SESSION_UUID
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (session_uuid, user_id))
        row = cursor.fetchone()
    return row is not None


def get_user_for_export(conn: PgConnection, user_id: str) -> dict | None:
    query = """
        SELECT
            USER_UUID,
            USERNAME,
            EMAIL_ENC,
            ACTIVE,
            CREATED_AT,
            UPDATED_AT,
            ANONYMIZED_AT,
            PROFILE_NAME
        FROM TB_USER
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_id),))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "user_uuid": row[0],
        "username": row[1],
        "email_enc": row[2],
        "active": row[3],
        "created_at": row[4],
        "updated_at": row[5],
        "anonymized_at": row[6],
        "profile_name": row[7],
    }


def get_sessions_for_export(conn: PgConnection, user_id: str) -> list[dict]:
    query = """
        SELECT
            SESSION_UUID,
            SOURCE_IP,
            USER_AGENT,
            CREATED_AT,
            UPDATED_AT,
            EXPIRES_AT,
            INVALIDATED_AT
        FROM TB_SESSION
        WHERE USER_ID = %s
          AND DELETED_AT IS NULL
        ORDER BY CREATED_AT DESC, SESSION_UUID DESC
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_id),))
        rows = cursor.fetchall()

    return [
        {
            "session_uuid": row[0],
            "source_ip": row[1],
            "user_agent": row[2],
            "created_at": row[3],
            "updated_at": row[4],
            "expires_at": row[5],
            "invalidated_at": row[6],
        }
        for row in rows
    ]
