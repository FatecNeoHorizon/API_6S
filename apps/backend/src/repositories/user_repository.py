from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from psycopg2.errors import  UniqueViolation
from psycopg2.extensions import connection as PgConnection

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

def exists_by_username(conn: PgConnection, username: str) -> bool:
    query = "SELECT 1 FROM TB_USER WHERE USERNAME = %s LIMIT 1"
    with conn.cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone() is not None

def _exists_by_profile_id(conn: PgConnection, profile_id: UUID) -> bool:
    query = "SELECT 1 FROM TB_PROFILE WHERE PROFILE_UUID = %s AND DELETED_AT IS NULL LIMIT 1"
    with conn.cursor() as cursor:
        cursor.execute(query, (str(profile_id),))
        return cursor.fetchone() is not None

def exists_by_email_hash(conn: PgConnection, email_hash: str) -> bool:
    query = "SELECT 1 FROM TB_USER WHERE EMAIL_HASH = %s LIMIT 1"
    with conn.cursor() as cursor:
        cursor.execute(query, (email_hash,))
        return cursor.fetchone() is not None

def create_user(conn: PgConnection, data: dict) -> UserCreateResult:
    if not _exists_by_profile_id(conn, data["profile_id"]):
        raise UserProfileNotFoundError("Profile not found for the provided profile_id.")

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
        raise UserAlreadyExistsError("Username or email already registered.") from exc
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
        raise ProfilePersistenceError("Failed to fetch profiles from PostgreSQL.") from exc

    return [
        ProfileResult(profile_uuid=row[0], profile_name=row[1])
        for row in rows
    ]