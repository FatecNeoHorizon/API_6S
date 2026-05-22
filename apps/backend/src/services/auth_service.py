from datetime import datetime, timedelta, timezone
import secrets

from fastapi import HTTPException, status

from src.api.schemas.user_schemas import (
    FirstAccessRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
)
from src.config.auth_security import (
    create_access_token,
    hash_password,
    hash_token,
    is_valid_uuid,
    verify_password,
)
from src.config.email_hasher import EmailHasher
from src.config.settings import Settings
from src.database.postgres import set_current_user
from src.services.consent_service import get_pending_consent
from src.repositories.user_repository import (
    complete_first_access,
    consume_valid_first_access_token,
    create_password_reset_token,
    create_user_session,
    get_user_auth_by_email_hash,
    get_valid_password_reset_token,
    invalidate_session,
    invalidate_user_sessions,
    mark_password_reset_token_used,
    rotate_refresh_token,
    update_user_password,
)


settings = Settings()


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

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    refresh_token = _generate_refresh_token()
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )

    session_id = create_user_session(
        conn,
        user_id=user_id,
        source_ip=source_ip,
        user_agent=user_agent,
        expires_at=expires_at,
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


def logout(conn, *, user_id: str, session_id: str) -> None:
    set_current_user(conn, user_id)

    was_invalidated = invalidate_session(conn, session_id)

    if not was_invalidated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_or_expired_session",
        )


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

    return {"detail": "password_reset_successfully"}