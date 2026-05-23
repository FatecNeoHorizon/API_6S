from datetime import datetime, timedelta, timezone
import secrets

import structlog
from fastapi import HTTPException, status

from src.api.schemas.user_schemas import (
    ConsentExportItem,
    DataExportResponse,
    FirstAccessRequest,
    ForgotPasswordResponse,
    IdentityExport,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    SessionExportItem,
)
from src.config.log_events import SESSION_INVALIDATED_ALL, SESSION_LISTED, SESSION_REVOKED
from src.config.auth_security import (
    create_access_token,
    hash_password,
    hash_token,
    is_valid_uuid,
    verify_password,
)
from src.config.email_hasher import EmailHasher
from src.config.log_events import DATA_EXPORT_REQUESTED
from src.config.settings import Settings
from src.database.postgres import get_pg_connection, set_current_user
from src.repositories.consent_repository import list_user_consent_history
from src.services.user_service import _decrypt_email
from src.services.consent_service import get_pending_consent
from src.repositories.user_repository import (
    complete_first_access,
    consume_valid_first_access_token,
    create_password_reset_token,
    create_user_session,
    get_sessions_for_export,
    get_user_auth_by_email_hash,
    get_user_for_export,
    get_user_sessions,
    get_valid_password_reset_token,
    invalidate_single_session,
    invalidate_user_sessions,
    mark_password_reset_token_used,
    rotate_refresh_token,
    update_user_password,
)


settings = Settings()
log = structlog.get_logger()


def _build_email_hash(email: str) -> str:
    return EmailHasher.hash(email)


def _generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def _create_session_and_token(
    conn,
    *,
    user_id: str,
    profile_name: str,
    source_ip: str,
    user_agent: str,
    username: str | None = None,
):
    set_current_user(conn, user_id)

    refresh_token = _generate_refresh_token()
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )

    session_id = create_user_session(
        conn,
        user_id=user_id,
        source_ip=source_ip,
        user_agent=user_agent,
        expires_at=refresh_expires_at,
        refresh_token_hash=hash_token(refresh_token),
        refresh_expires_at=refresh_expires_at,
    )

    # Ensure session_id is a valid UUID string
    if not is_valid_uuid(session_id):
        raise HTTPException(
            status_code=500,
            detail="invalid_session_id_generated",
        )

    access_token = create_access_token(
        user_id=user_id,
        session_id=session_id,
        profile_name=profile_name,
        username=username,
    )

    pending_clauses = get_pending_consent(conn, user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "pending_consent": len(pending_clauses) > 0,
        "pending_clauses": pending_clauses,
    }


def refresh_access_token(conn, *, payload: RefreshTokenRequest) -> dict:
    new_refresh_token = _generate_refresh_token()
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )

    session_data = rotate_refresh_token(
        conn,
        refresh_token_hash=hash_token(payload.refresh_token),
        new_refresh_token_hash=hash_token(new_refresh_token),
        refresh_expires_at=refresh_expires_at,
    )

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_or_expired_refresh_token",
        )

    if not session_data["active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="inactive_user",
        )

    user_id = str(session_data["user_uuid"])
    set_current_user(conn, user_id)

    access_token = create_access_token(
        user_id=user_id,
        session_id=str(session_data["session_uuid"]),
        profile_name=session_data["profile_name"],
        username=session_data["username"],
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def first_access(
    conn,
    *,
    payload: FirstAccessRequest,
    source_ip: str,
    user_agent: str,
):
    token_hash = hash_token(payload.token)
    token_data = consume_valid_first_access_token(conn, token_hash)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_or_expired_first_access_token",
        )

    if not token_data["active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="inactive_user",
        )

    user_id = str(token_data["user_id"])

    set_current_user(conn, user_id)

    complete_first_access(
        conn,
        user_id=user_id,
        password_hash=hash_password(payload.new_password),
    )

    return _create_session_and_token(
        conn,
        user_id=user_id,
        profile_name=token_data["profile_name"],
        source_ip=source_ip,
        user_agent=user_agent,
        username=token_data["username"],
    )


def login(
    conn,
    *,
    payload: LoginRequest,
    source_ip: str,
    user_agent: str,
):
    email_hash = _build_email_hash(payload.email)
    user = get_user_auth_by_email_hash(conn, email_hash)

    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid_credentials",
    )

    if not user:
        raise generic_error

    if not user["active"]:
        raise generic_error

    if not user["first_access_completed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="first_access_required",
        )

    if not verify_password(payload.password, user["password_hash"]):
        raise generic_error

    return _create_session_and_token(
        conn,
        user_id=str(user["user_uuid"]),
        profile_name=user["profile_name"],
        source_ip=source_ip,
        user_agent=user_agent,
        username=user["username"],
    )


def logout(conn, *, user_id: str) -> None:
    invalidate_user_sessions(conn, user_id)


def forgot_password(conn, *, email: str) -> ForgotPasswordResponse:
    email_hash = _build_email_hash(email)
    user = get_user_auth_by_email_hash(conn, email_hash)

    generic_response = ForgotPasswordResponse(
        detail="If the email is registered, a password recovery link will be sent."
    )

    if not user or not user["active"]:
        return generic_response

    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    create_password_reset_token(
        conn,
        user_id=str(user["user_uuid"]),
        token_hash=token_hash,
        expires_at=expires_at,
    )

    if settings.app_env != "prod":
        generic_response.dev_reset_token = raw_token
        frontend_base_url = (settings.frontend_url or "http://localhost:5173").rstrip("/")
        generic_response.dev_reset_url = f"{frontend_base_url}/reset-password?token={raw_token}"

    return generic_response


def reset_password(conn, *, payload: ResetPasswordRequest) -> dict:
    token_hash = hash_token(payload.token)
    reset_data = get_valid_password_reset_token(conn, token_hash)

    if not reset_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_or_expired_reset_token",
        )

    if not reset_data["active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="inactive_user",
        )

    user_id = str(reset_data["user_uuid"])

    set_current_user(conn, user_id)

    update_user_password(
        conn,
        user_id=user_id,
        password_hash=hash_password(payload.new_password),
    )

    mark_password_reset_token_used(conn, str(reset_data["reset_uuid"]))

    invalidated = invalidate_user_sessions(conn, user_id)
    for session_uuid in invalidated:
        log.info(
            SESSION_INVALIDATED_ALL,
            acting_user_id=user_id,
            target_session_uuid=session_uuid,
            reason="PASSWORD_CHANGE",
        )

    return {"detail": "password_reset_successfully"}


def export_user_data(conn, *, user_id: str) -> DataExportResponse:
    set_current_user(conn, user_id)

    user = get_user_for_export(conn, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user_not_found",
        )

    if user["anonymized_at"] is not None:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="user_data_no_longer_exists",
        )

    identity = IdentityExport(
        user_id=user["user_uuid"],
        username=user["username"],
        email=_decrypt_email(user["email_enc"], settings),
        profile=user["profile_name"],
        active=user["active"],
        first_access_completed=user["first_access_completed"],
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )

    consent_history = [
        ConsentExportItem(
            consent_log_id=row["log_uuid"],
            clause_id=row["clause_uuid"],
            clause_code=row["clause_code"],
            clause_title=row["clause_title"],
            policy_version_id=row["policy_version_id"],
            policy_type=row["policy_type"],
            policy_version=row["policy_version"],
            action=row["action"],
            timestamp=row["registered_at"],
            source_ip=row["source_ip"],
            user_agent=row["user_agent"],
            channel=row["channel"],
        )
        for row in list_user_consent_history(conn, user_id)
    ]

    session_history = [
        SessionExportItem(
            session_id=row["session_uuid"],
            source_ip=row["source_ip"],
            user_agent=row["user_agent"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            expires_at=row["expires_at"],
            invalidated_at=row["invalidated_at"],
        )
        for row in get_sessions_for_export(conn, user_id)
    ]

    log.info(DATA_EXPORT_REQUESTED, user_id=user_id)

    return DataExportResponse(
        exported_at=datetime.now(timezone.utc),
        identity=identity,
        consent_history=consent_history,
        session_history=session_history,
    )


def list_sessions_service(conn, *, user_id: str) -> list[dict]:
    sessions = get_user_sessions(conn, user_id)
    log.info(SESSION_LISTED, acting_user_id=user_id, count=len(sessions))
    return sessions


def revoke_session_service(
    conn, *, session_uuid: str, current_session_id: str, acting_user_id: str
) -> None:
    if session_uuid == current_session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot_revoke_current_session",
        )

    revoked = invalidate_single_session(
        conn, session_uuid=session_uuid, user_id=acting_user_id
    )
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="session_not_found",
        )

    log.info(
        SESSION_REVOKED,
        acting_user_id=acting_user_id,
        target_session_uuid=session_uuid,
        reason="USER_REVOCATION",
    )


def admin_invalidate_user_sessions_service(*, target_user_id: str, acting_user_id: str) -> None:
    with get_pg_connection() as conn:
        invalidated = invalidate_user_sessions(conn, target_user_id)
    for session_uuid in invalidated:
        log.info(
            SESSION_INVALIDATED_ALL,
            acting_user_id=acting_user_id,
            target_session_uuid=session_uuid,
            reason="ADMIN_DEACTIVATION",
        )
