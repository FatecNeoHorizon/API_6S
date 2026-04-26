import base64
import hashlib

import bcrypt
from cryptography.fernet import Fernet

from src.api.schemas.user_schemas import UserCreateRequest, UserCreateResponse
from src.config.settings import Settings
from src.database.postgres_connection import get_postgres_connection
from src.repositories.user_repository import ProfileResult
from typing import List
from uuid import UUID
from src.repositories.user_repository import (
    UserProfileNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserResult,
    create_user,
    exists_by_username,
    exists_by_email_hash,
    get_user_by_id,
    list_users,
    update_user,
    set_user_active,
    delete_user,
    list_profiles,
    exists_by_profile_id,
)

def create_user_service(payload: UserCreateRequest) -> UserCreateResponse:
    settings = Settings()
    normalized_email = str(payload.email).strip().lower()
    email_hash = _build_email_hash(normalized_email, settings.email_hash_salt)

    with get_postgres_connection() as conn:
        if not exists_by_profile_id(conn, payload.profile_id):
            raise UserProfileNotFoundError("Perfil não encontrado para o profile_id informado.")
        if exists_by_username(conn, payload.username.strip().upper()):
            raise UserAlreadyExistsError("Nome de usuário já cadastrado.")
        if exists_by_email_hash(conn, email_hash):
            raise UserAlreadyExistsError("E-mail já cadastrado.")

        data = {
            "username": payload.username.strip().upper(),
            "email_hash": email_hash,
            "email_enc": _encrypt_email(normalized_email, settings),
            "password_hash": _hash_password(payload.password),
            "profile_id": payload.profile_id,
        }

        result = create_user(conn, data)
        conn.commit()

    return UserCreateResponse(
        user_uuid=result.user_uuid,
        username=result.username,
        profile_id=result.profile_id,
        active=result.active,
        created_at=result.created_at,
    )

def get_user_by_id_service(user_uuid: UUID) -> UserResult:
    with get_postgres_connection() as conn:
        user = get_user_by_id(conn, user_uuid)
    if user is None:
        raise UserNotFoundError("Usuário não encontrado.")
    return user


def list_users_service() -> List[UserResult]:
    with get_postgres_connection() as conn:
        return list_users(conn)


def update_user_service(user_uuid: UUID, data: dict) -> UserResult:
    with get_postgres_connection() as conn:
        if not exists_by_profile_id(conn, data["profile_id"]):
            raise UserProfileNotFoundError("Perfil não encontrado para o profile_id informado.")
        result = update_user(conn, user_uuid, data)
        conn.commit()
    if result is None:
        raise UserNotFoundError("Usuário não encontrado.")
    return result


def set_user_active_service(user_uuid: UUID, active: bool) -> UserResult:
    with get_postgres_connection() as conn:
        result = set_user_active(conn, user_uuid, active)
        conn.commit()
    if result is None:
        raise UserNotFoundError("Usuário não encontrado.")
    return result


def delete_user_service(user_uuid: UUID) -> None:
    with get_postgres_connection() as conn:
        deleted = delete_user(conn, user_uuid)
        conn.commit()
    if not deleted:
        raise UserNotFoundError("Usuário não encontrado.")

def _build_email_hash(email: str, salt: str) -> str:
    payload = f"{email}:{salt}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sanitize_fernet_key(raw_key: str) -> str:
    key = raw_key.strip().strip('"').strip("'")

    if key.startswith("b'") and key.endswith("'"):
        return key[2:-1]
    if key.startswith('b"') and key.endswith('"'):
        return key[2:-1]

    return key


def _resolve_email_encryption_key(settings: Settings) -> bytes:
    if settings.email_encryption_key:
        return _sanitize_fernet_key(settings.email_encryption_key).encode("utf-8")

    digest = hashlib.sha256(settings.email_hash_salt.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def _encrypt_email(email: str, settings: Settings) -> str:
    key = _resolve_email_encryption_key(settings)
    try:
        return Fernet(key).encrypt(email.encode("utf-8")).decode("utf-8")
    except ValueError as exc:
        raise RuntimeError(
            "A EMAIL_ENCRYPTION_KEY é inválida. Use uma chave Fernet gerada por cryptography.fernet.Fernet.generate_key()."
        ) from exc

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def list_profiles_service() -> List[ProfileResult]:
    with get_postgres_connection() as conn:
        return list_profiles(conn)