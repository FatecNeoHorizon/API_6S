import base64
import hashlib
from datetime import datetime
from typing import List
from uuid import UUID, uuid4

import structlog
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from psycopg2 import IntegrityError, OperationalError, extensions

from src.api.schemas.user_schemas import UserCreateRequest, UserCreateResponse
from src.config.exception_handlers import handle_db_integrity_error, handle_db_operational_error
from src.config.keycloak_admin_client import (
    KeycloakAdminError,
    KeycloakUserAlreadyExistsError,
    get_keycloak_admin_client,
)
from src.config.log_events import SESSION_INVALIDATED_ALL
from src.config.settings import Settings
from src.database.postgres import get_pg_connection
from src.database.postgres import set_current_user
from src.database.postgres import acquire_pg_connection, release_pg_connection
from src.database.blacklist_postgres import (
    acquire_blacklist_connection,
    release_blacklist_connection,
)
from src.repositories.blacklist_repository import (
    BlacklistPersistenceError,
    insert_blacklisted_user,
)
from src.repositories.user_repository import (
    ProfileResult,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserPersistenceError,
    UserProfileNotFoundError,
    UserResult,
    create_user,
    delete_user,
    delete_user_sessions,
    exists_by_profile_name,
    exists_by_username,
    get_current_user_profile,
    get_keycloak_sub,
    get_user_by_id,
    invalidate_user_sessions,
    list_profiles,
    list_users,
    remove_user_encryption_material,
    set_user_active,
    update_current_user_profile,
    update_user,
)

_log = structlog.get_logger()


def create_user_service(payload: UserCreateRequest) -> UserCreateResponse:
    settings = Settings()
    normalized_email = str(payload.email).strip().lower()
    keycloak = get_keycloak_admin_client()
    keycloak_sub: str | None = None

    try:
        with get_pg_connection() as conn:
            if not exists_by_profile_name(conn, payload.profile_name):
                raise UserProfileNotFoundError(f"Perfil '{payload.profile_name}' não encontrado.")
            if exists_by_username(conn, payload.username.strip().upper()):
                raise UserAlreadyExistsError("Nome de usuário já cadastrado.")

        try:
            keycloak_sub = keycloak.create_user(
                username=payload.username.strip().upper(),
                email=normalized_email,
                enabled=True,
            )
        except KeycloakUserAlreadyExistsError as exc:
            raise UserAlreadyExistsError("E-mail já cadastrado no servidor de identidade.") from exc
        except KeycloakAdminError as exc:
            raise HTTPException(status_code=502, detail="Falha ao criar usuário no servidor de identidade.") from exc

        try:
            keycloak.assign_realm_role(keycloak_sub, payload.profile_name)
            keycloak.send_required_actions_email(keycloak_sub, ["UPDATE_PASSWORD"])
        except KeycloakAdminError as exc:
            try:
                keycloak.delete_user(keycloak_sub)
            except Exception:
                pass
            raise HTTPException(status_code=502, detail="Falha ao atribuir perfil no servidor de identidade.") from exc

        try:
            with get_pg_connection() as conn:
                data = {
                    "username": payload.username.strip().upper(),
                    "email_enc": _encrypt_email(normalized_email, settings),
                    "profile_name": payload.profile_name,
                    "keycloak_sub": keycloak_sub,
                }
                result = create_user(conn, data)
        except Exception:
            try:
                keycloak.delete_user(keycloak_sub)
            except Exception:
                pass
            raise

        return UserCreateResponse(
            user_uuid=result.user_uuid,
            username=result.username,
            profile_name=result.profile_name,
            active=result.active,
            created_at=result.created_at,
        )

    except (UserProfileNotFoundError, UserAlreadyExistsError):
        raise
    except HTTPException:
        raise
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="create_user_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="create_user_service")
        raise HTTPException(status_code=503, detail="database_unavailable")


def get_user_by_id_service(user_uuid: UUID) -> UserResult:
    try:
        with get_pg_connection() as conn:
            user = get_user_by_id(conn, user_uuid)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="get_user_by_id_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="get_user_by_id_service")
        raise HTTPException(status_code=503, detail="database_unavailable")
    if user is None:
        raise UserNotFoundError("Usuário não encontrado.")
    return user


def list_users_service() -> List[UserResult]:
    try:
        with get_pg_connection() as conn:
            return list_users(conn)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="list_users_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="list_users_service")
        raise HTTPException(status_code=503, detail="database_unavailable")


def update_user_service(user_uuid: UUID, data: dict) -> UserResult:
    try:
        with get_pg_connection() as conn:
            if not exists_by_profile_name(conn, data["profile_name"]):
                raise UserProfileNotFoundError(f"Perfil '{data['profile_name']}' não encontrado.")

            current = get_user_by_id(conn, user_uuid)
            if current is None:
                raise UserNotFoundError("Usuário não encontrado.")

            old_profile_name = current.profile_name
            new_profile_name = data["profile_name"]
            keycloak_sub = get_keycloak_sub(conn, user_uuid)

            result = update_user(conn, user_uuid, data)
    except (UserProfileNotFoundError, UserNotFoundError):
        raise
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="update_user_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="update_user_service")
        raise HTTPException(status_code=503, detail="database_unavailable")
    if result is None:
        raise UserNotFoundError("Usuário não encontrado.")

    if keycloak_sub:
        keycloak = get_keycloak_admin_client()
        new_username = data["username"].strip().upper()

        if old_profile_name != new_profile_name:
            try:
                keycloak.update_user_role(keycloak_sub, old_profile_name, new_profile_name)
            except Exception:
                _log.warning(
                    "keycloak.user.role_update_failed",
                    keycloak_sub=keycloak_sub,
                    old_role=old_profile_name,
                    new_role=new_profile_name,
                )

        if current.username.upper() != new_username:
            try:
                keycloak.update_user(keycloak_sub, username=new_username)
            except Exception:
                _log.warning(
                    "keycloak.user.username_update_failed",
                    keycloak_sub=keycloak_sub,
                    new_username=new_username,
                )

    return result


def set_user_active_service(user_uuid: UUID, active: bool, acting_user_id: str | None = None) -> UserResult:
    try:
        with get_pg_connection() as conn:
            keycloak_sub = get_keycloak_sub(conn, user_uuid)
            result = set_user_active(conn, user_uuid, active)
            if result is not None and not active:
                invalidated = invalidate_user_sessions(conn, str(user_uuid))
                for session_uuid in invalidated:
                    _log.info(
                        SESSION_INVALIDATED_ALL,
                        acting_user_id=acting_user_id or str(user_uuid),
                        target_session_uuid=session_uuid,
                        reason="ADMIN_DEACTIVATION",
                    )
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="set_user_active_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="set_user_active_service")
        raise HTTPException(status_code=503, detail="database_unavailable")
    if result is None:
        raise UserNotFoundError("Usuário não encontrado.")

    if keycloak_sub:
        try:
            get_keycloak_admin_client().set_user_enabled(keycloak_sub, active)
        except Exception:
            _log.warning(
                "keycloak.user.enabled_update_failed",
                keycloak_sub=keycloak_sub,
                active=active,
            )

    return result


def delete_user_service(user_uuid: UUID) -> None:
    main_conn = None
    blacklist_conn = None
    gtrid = str(uuid4())
    main_xid = extensions.Xid(42, gtrid, "main")
    blacklist_xid = extensions.Xid(42, gtrid, "blacklist")

    try:
        main_conn = acquire_pg_connection()
        blacklist_conn = acquire_blacklist_connection()
        main_conn.autocommit = False
        blacklist_conn.autocommit = False
        main_conn.tpc_begin(main_xid)
        blacklist_conn.tpc_begin(blacklist_xid)

        if get_user_by_id(main_conn, user_uuid) is None:
            raise UserNotFoundError("Usuário não encontrado.")

        keycloak_sub = get_keycloak_sub(main_conn, user_uuid)

        remove_user_encryption_material(main_conn, user_uuid)
        insert_blacklisted_user(blacklist_conn, user_uuid)

        invalidated = invalidate_user_sessions(main_conn, str(user_uuid))
        for session_uuid in invalidated:
            _log.info(
                SESSION_INVALIDATED_ALL,
                acting_user_id=str(user_uuid),
                target_session_uuid=session_uuid,
                reason="USER_DELETION",
            )

        delete_user_sessions(main_conn, user_uuid)

        deleted = delete_user(main_conn, user_uuid)
        if not deleted:
            raise UserNotFoundError("Usuário não encontrado.")

        main_conn.tpc_prepare()
        blacklist_conn.tpc_prepare()

        main_conn.tpc_commit()
        blacklist_conn.tpc_commit()
    except (UserNotFoundError, UserAlreadyExistsError, UserProfileNotFoundError):
        if main_conn is not None:
            main_conn.tpc_rollback()
        if blacklist_conn is not None:
            blacklist_conn.tpc_rollback()
        raise
    except BlacklistPersistenceError as exc:
        if main_conn is not None:
            main_conn.tpc_rollback()
        if blacklist_conn is not None:
            blacklist_conn.tpc_rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except IntegrityError as exc:
        if main_conn is not None:
            main_conn.tpc_rollback()
        if blacklist_conn is not None:
            blacklist_conn.tpc_rollback()
        handle_db_integrity_error(exc, context="delete_user_service")
        raise HTTPException(status_code=409, detail="conflict") from exc
    except OperationalError as exc:
        if main_conn is not None:
            main_conn.tpc_rollback()
        if blacklist_conn is not None:
            blacklist_conn.tpc_rollback()
        handle_db_operational_error(exc, context="delete_user_service")
        raise HTTPException(status_code=503, detail="database_unavailable") from exc
    except Exception:
        if main_conn is not None:
            main_conn.tpc_rollback()
        if blacklist_conn is not None:
            blacklist_conn.tpc_rollback()
        raise
    finally:
        if main_conn is not None:
            release_pg_connection(main_conn)
        if blacklist_conn is not None:
            release_blacklist_connection(blacklist_conn)

    if keycloak_sub:
        try:
            get_keycloak_admin_client().delete_user(keycloak_sub)
        except Exception:
            _log.warning("keycloak.user.delete_failed", keycloak_sub=keycloak_sub)


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


def _decrypt_email(email_enc: str, settings: Settings) -> str:
    if email_enc.startswith("ENCRYPTED::"):
        return email_enc.removeprefix("ENCRYPTED::")

    key = _resolve_email_encryption_key(settings)
    try:
        return Fernet(key).decrypt(email_enc.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        # Fallback: plain-text email stored in dev seed (V014 migration)
        return email_enc


def _format_current_user_profile(row: dict) -> dict:
    settings = Settings()
    return {
        "user_uuid": row["user_uuid"],
        "username": row["username"],
        "email": _decrypt_email(row["email_enc"], settings),
        "profile_name": row["profile_name"],
        "active": row["active"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def get_current_user_profile_service(user_id: str) -> dict:
    try:
        with get_pg_connection() as conn:
            set_current_user(conn, user_id)
            user = get_current_user_profile(conn, user_id)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="get_current_user_profile_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="get_current_user_profile_service")
        raise HTTPException(status_code=503, detail="database_unavailable")

    if user is None:
        raise UserNotFoundError("Usuario nao encontrado.")

    return _format_current_user_profile(user)


def update_current_user_profile_service(user_id: str, username: str, email: str) -> dict:
    settings = Settings()
    normalized_username = username.strip().upper()
    normalized_email = str(email).strip().lower()
    keycloak_sub: str | None = None

    try:
        with get_pg_connection() as conn:
            set_current_user(conn, user_id)
            current_user = get_current_user_profile(conn, user_id)

            if current_user is None:
                raise UserNotFoundError("Usuario nao encontrado.")

            if (
                current_user["username"].upper() != normalized_username
                and exists_by_username(conn, normalized_username)
            ):
                raise UserAlreadyExistsError("Nome de usuario ja cadastrado.")

            keycloak_sub = get_keycloak_sub(conn, user_id)
            result = update_current_user_profile(
                conn,
                user_id,
                {
                    "username": normalized_username,
                    "email_enc": _encrypt_email(normalized_email, settings),
                },
            )
    except (UserNotFoundError, UserAlreadyExistsError):
        raise
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="update_current_user_profile_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="update_current_user_profile_service")
        raise HTTPException(status_code=503, detail="database_unavailable")

    if result is None:
        raise UserNotFoundError("Usuario nao encontrado.")

    if keycloak_sub:
        try:
            get_keycloak_admin_client().update_user(
                keycloak_sub,
                username=normalized_username,
                email=normalized_email,
            )
        except Exception:
            _log.warning(
                "keycloak.user.profile_update_failed",
                keycloak_sub=keycloak_sub,
            )

    return _format_current_user_profile(result)


def list_profiles_service() -> List[ProfileResult]:
    try:
        with get_pg_connection() as conn:
            return list_profiles(conn)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="list_profiles_service")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="list_profiles_service")
        raise HTTPException(status_code=503, detail="database_unavailable")
