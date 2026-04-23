from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from src.database.postgres_connection import get_postgres_connection


class UserAlreadyExistsError(Exception):
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


def create_user(
    username: str,
    email_hash: str,
    email_enc: str,
    password_hash: str,
    profile_id: UUID,
) -> UserCreateResult:
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
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (username, email_hash, email_enc, password_hash, str(profile_id)),
                )
                row = cursor.fetchone()
            conn.commit()
    except UniqueViolation as exc:
        raise UserAlreadyExistsError("Username or email already registered.") from exc
    except ForeignKeyViolation as exc:
        raise UserProfileNotFoundError("Profile not found for the provided profile_id.") from exc
    except Exception as exc:
        raise UserPersistenceError("Failed to persist user into PostgreSQL.") from exc

    if row is None:
        raise UserPersistenceError("PostgreSQL did not return created user data.")

    return UserCreateResult(
        user_uuid=row[0],
        username=row[1],
        profile_id=row[2],
        active=row[3],
        created_at=row[4],
    )


def list_profiles() -> List[ProfileResult]:
    query = """
        SELECT PROFILE_UUID, PROFILE_NAME
        FROM TB_PROFILE
        WHERE DELETED_AT IS NULL
        ORDER BY PROFILE_NAME ASC
    """

    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
    except Exception as exc:
        raise ProfilePersistenceError("Failed to fetch profiles from PostgreSQL.") from exc

    return [
        ProfileResult(profile_uuid=row[0], profile_name=row[1])
        for row in rows
    ]
