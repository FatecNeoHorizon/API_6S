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
            PROFILE_ID
        )
        VALUES (%s, %s, %s, %s)
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
        profile_id=row[2],
        active=row[3],
        created_at=row[4],
        updated_at=row[5],
    )


def get_user_profile_by_id(conn: PgConnection, user_uuid: str):
    query = """
        SELECT
            u.USER_UUID,
            u.USERNAME,
            u.EMAIL_ENC,
            u.PROFILE_ID,
            u.ACTIVE,
            u.FIRST_ACCESS_COMPLETED,
            u.CREATED_AT,
            u.UPDATED_AT,
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
        "email_enc": row[2],
        "profile_id": row[3],
        "active": row[4],
        "first_access_completed": row[5],
        "created_at": row[6],
        "updated_at": row[7],
        "profile_name": row[8],
    }


def update_user_profile(conn: PgConnection, user_uuid: str, data: dict):
    query = """
        WITH updated AS (
            UPDATE TB_USER
            SET USERNAME = %s,
                EMAIL_HASH = %s,
                EMAIL_ENC = %s,
                UPDATED_AT = NOW()
            WHERE USER_UUID = %s
              AND DELETED_AT IS NULL
            RETURNING
                USER_UUID,
                USERNAME,
                EMAIL_ENC,
                PROFILE_ID,
                ACTIVE,
                FIRST_ACCESS_COMPLETED,
                CREATED_AT,
                UPDATED_AT
        )
        SELECT
            updated.USER_UUID,
            updated.USERNAME,
            updated.EMAIL_ENC,
            updated.PROFILE_ID,
            updated.ACTIVE,
            updated.FIRST_ACCESS_COMPLETED,
            updated.CREATED_AT,
            updated.UPDATED_AT,
            p.PROFILE_NAME
        FROM updated
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = updated.PROFILE_ID
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    data["username"],
                    data["email_hash"],
                    data["email_enc"],
                    str(user_uuid),
                ),
            )
            row = cursor.fetchone()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Nome de usuÃ¡rio ou e-mail jÃ¡ cadastrado.") from exc
    except Exception as exc:
        raise UserPersistenceError("Falha ao atualizar o perfil do usuÃ¡rio.") from exc

    if row is None:
        return None

    return {
        "user_uuid": row[0],
        "username": row[1],
        "email_enc": row[2],
        "profile_id": row[3],
        "active": row[4],
        "first_access_completed": row[5],
        "created_at": row[6],
        "updated_at": row[7],
        "profile_name": row[8],
    }


def list_users(conn: PgConnection) -> List[UserResult]:
    query = """
        SELECT USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT, UPDATED_AT
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
            profile_id=row[2],
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


def exists_by_profile_id(conn: PgConnection, profile_id: UUID) -> bool:
    query = """
        SELECT 1
        FROM TB_PROFILE
        WHERE PROFILE_UUID = %s
          AND DELETED_AT IS NULL
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(profile_id),))
        return cursor.fetchone() is not None


def exists_by_email_hash(conn: PgConnection, email_hash: str) -> bool:
    query = """
        SELECT 1
        FROM TB_USER
        WHERE EMAIL_HASH = %s
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (email_hash,))
        return cursor.fetchone() is not None


def exists_by_email_hash_for_other_user(conn: PgConnection, email_hash: str, user_uuid: str) -> bool:
    query = """
        SELECT 1
        FROM TB_USER
        WHERE EMAIL_HASH = %s
          AND USER_UUID <> %s
        LIMIT 1
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (email_hash, str(user_uuid)))
        return cursor.fetchone() is not None


def get_current_user_profile(conn: PgConnection, user_uuid: str) -> dict | None:
    query = """
        SELECT
            u.USER_UUID,
            u.USERNAME,
            u.EMAIL_ENC,
            p.PROFILE_NAME,
            u.ACTIVE,
            u.FIRST_ACCESS_COMPLETED,
            u.CREATED_AT,
            u.UPDATED_AT
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
        "email_enc": row[2],
        "profile_name": row[3],
        "active": row[4],
        "first_access_completed": row[5],
        "created_at": row[6],
        "updated_at": row[7],
    }


def update_current_user_profile(conn: PgConnection, user_uuid: str, data: dict) -> dict | None:
    query = """
        UPDATE TB_USER
        SET USERNAME = %s,
            EMAIL_HASH = %s,
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
                    data["email_hash"],
                    data["email_enc"],
                    str(user_uuid),
                ),
            )
            row = cursor.fetchone()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Nome de usuÃ¡rio ou e-mail jÃ¡ cadastrado.") from exc

    if row is None:
        return None

    return get_current_user_profile(conn, user_uuid)


def update_user(conn: PgConnection, user_uuid: UUID, data: dict) -> Optional[UserResult]:
    query = """
        UPDATE TB_USER
        SET USERNAME = %s,
            PROFILE_ID = %s,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
        RETURNING USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT, UPDATED_AT
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    data["username"],
                    str(data["profile_id"]),
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
        profile_id=row[2],
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
        RETURNING USER_UUID, USERNAME, PROFILE_ID, ACTIVE, CREATED_AT, UPDATED_AT
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (active, str(user_uuid)))
        row = cursor.fetchone()

    if row is None:
        return None

    return UserResult(
        user_uuid=row[0],
        username=row[1],
        profile_id=row[2],
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


def create_first_access_token(
    conn: PgConnection,
    *,
    user_id: str,
    token_hash: str,
    expires_at: datetime,
) -> str:
    query = """
        INSERT INTO TB_FIRST_ACCESS_TOKEN (USER_ID, TOKEN_HASH, EXPIRES_AT)
        VALUES (%s, %s, %s)
        RETURNING TOKEN_UUID
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_id), token_hash, expires_at))
        row = cursor.fetchone()

    return str(row[0])


def consume_valid_first_access_token(conn: PgConnection, token_hash: str):
    query = """
        UPDATE TB_FIRST_ACCESS_TOKEN fat
        SET USED_AT = NOW()
        FROM TB_USER u
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = u.PROFILE_ID
        WHERE fat.USER_ID = u.USER_UUID
          AND fat.TOKEN_HASH = %s
          AND fat.USED_AT IS NULL
          AND fat.EXPIRES_AT > NOW()
          AND u.DELETED_AT IS NULL
        RETURNING
            fat.TOKEN_UUID,
            fat.USER_ID,
            u.ACTIVE,
            p.PROFILE_NAME,
            u.USERNAME,
            u.EMAIL_HASH
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (token_hash,))
        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "token_uuid": row[0],
        "user_id": row[1],
        "active": row[2],
        "profile_name": row[3],
        "username": row[4],
        "email_hash": row[5],
    }


def complete_first_access(
    conn: PgConnection,
    *,
    user_id: str,
    password_hash: str,
) -> None:
    query = """
        UPDATE TB_USER
        SET PASSWORD_HASH = %s,
            FIRST_ACCESS_COMPLETED = TRUE,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (password_hash, str(user_id)))


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


def invalidate_user_sessions(conn: PgConnection, user_id: str) -> None:
    query = """
        UPDATE TB_SESSION
        SET INVALIDATED_AT = NOW(),
            UPDATED_AT = NOW()
        WHERE USER_ID = %s
          AND INVALIDATED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (user_id,))


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

    # Ensure we have a valid UUID
    if row is None or row[0] is None:
        raise ValueError("Failed to create session: no UUID returned")

    session_uuid = str(row[0])
    # Validate UUID format.
    if not is_valid_uuid(session_uuid):
        raise ValueError(f"Invalid session UUID format: {session_uuid}")

    return session_uuid


def rotate_refresh_token(conn: PgConnection, refresh_token_hash: str, new_refresh_token_hash: str, refresh_expires_at):
    query = """
        UPDATE TB_SESSION s
        SET REFRESH_TOKEN_HASH = %s,
            REFRESH_EXPIRES_AT = %s,
            EXPIRES_AT = %s,
            UPDATED_AT = NOW()
        FROM TB_USER u
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = u.PROFILE_ID
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
            p.PROFILE_NAME,
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
            u.FIRST_ACCESS_COMPLETED,
            p.PROFILE_NAME,
            u.USERNAME,
            s.INVALIDATED_AT,
            s.EXPIRES_AT,
            s.DELETED_AT,
            u.DELETED_AT as user_deleted_at
        FROM TB_SESSION s
        JOIN TB_USER u
          ON u.USER_UUID = s.USER_ID
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = u.PROFILE_ID
        WHERE s.SESSION_UUID = %s
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(session_uuid),))
        row = cursor.fetchone()

    if row is None:
        return None

    # Check conditions
    if row[6] is not None:  # INVALIDATED_AT is not NULL → session was invalidated
        return None

    if row[7] is not None:  # EXPIRES_AT exists
        now = datetime.now(timezone.utc)
        if row[7] <= now:  # Check if expired
            return None

    if row[8] is not None:  # DELETED_AT is not NULL → session was soft-deleted
        return None

    if row[9] is not None:  # USER DELETED_AT is not NULL → user was soft-deleted
        return None

    return {
        "session_uuid": row[0],
        "user_uuid": row[1],
        "active": row[2],
        "first_access_completed": row[3],
        "profile_name": row[4],
        "username": row[5],
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


def update_user_password(
    conn: PgConnection,
    *,
    user_id: str,
    password_hash: str,
) -> None:
    query = """
        UPDATE TB_USER
        SET PASSWORD_HASH = %s,
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND DELETED_AT IS NULL
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (password_hash, str(user_id)))
