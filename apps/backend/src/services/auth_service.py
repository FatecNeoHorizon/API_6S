from datetime import datetime, timedelta, timezone
import secrets

import httpx
import jwt as _jwt
from jwt import PyJWKClient
import structlog
from fastapi import HTTPException, status

from src.api.schemas.user_schemas import (
    ConsentExportItem,
    DataExportResponse,
    IdentityExport,
    RefreshTokenRequest,
    SessionExportItem,
)
from src.config.log_events import SESSION_INVALIDATED_ALL, SESSION_LISTED, SESSION_REVOKED
from src.config.auth_security import (
    create_access_token,
    hash_token,
    is_valid_uuid,
    mask_source_ip,
)
from src.config.log_events import DATA_EXPORT_REQUESTED
from src.config.settings import Settings
from src.database.postgres import get_pg_connection, set_current_user
from src.repositories.consent_repository import list_user_consent_history
from src.services.user_service import _decrypt_email
from src.services.consent_service import get_pending_consent
from src.repositories.user_repository import (
    create_user_session,
    get_sessions_for_export,
    get_user_by_keycloak_sub,
    get_user_for_export,
    get_user_sessions,
    invalidate_single_session,
    invalidate_user_sessions,
    invalidate_session,
    rotate_refresh_token,
)


settings = Settings()
log = structlog.get_logger()

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        jwks_uri = (
            f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
            "/protocol/openid-connect/certs"
        )
        _jwks_client = PyJWKClient(jwks_uri, cache_keys=True)
    return _jwks_client


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
        source_ip=mask_source_ip(source_ip),
        user_agent=user_agent,
        expires_at=refresh_expires_at,
        refresh_token_hash=hash_token(refresh_token),
        refresh_expires_at=refresh_expires_at,
    )

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


def oauth_callback(
    conn,
    *,
    code: str,
    code_verifier: str,
    redirect_uri: str,
    source_ip: str,
    user_agent: str,
) -> dict:
    response = httpx.post(
        f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri,
            "client_id": settings.keycloak_client_id,
        },
        timeout=10,
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_authorization_code",
        )

    kc_tokens = response.json()
    kc_access_token = kc_tokens.get("access_token")
    kc_id_token = kc_tokens.get("id_token", "")
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(kc_access_token)
        kc_payload = _jwt.decode(
            kc_access_token,
            signing_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except (_jwt.InvalidTokenError, Exception) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_keycloak_token",
        ) from exc
    keycloak_sub = kc_payload.get("sub")
    if not keycloak_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_keycloak_token",
        )

    # Keycloak is source of truth: extract identity claims from the token
    kc_roles: list[str] = kc_payload.get("realm_access", {}).get("roles", [])
    profile_name = next(
        (r for r in kc_roles if r in ("ADMIN", "MANAGER", "ANALYST")),
        None,
    )
    if not profile_name:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no_valid_profile_role",
        )

    username: str = kc_payload.get("preferred_username", "")

    user = get_user_by_keycloak_sub(conn, keycloak_sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_not_registered",
        )

    if not user["active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="inactive_user",
        )

    result = _create_session_and_token(
        conn,
        user_id=str(user["user_uuid"]),
        profile_name=profile_name,
        source_ip=source_ip,
        user_agent=user_agent,
        username=username,
    )
    result["kc_id_token"] = kc_id_token
    return result


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



def logout(conn, *, user_id: str, session_id: str) -> None:
    set_current_user(conn, user_id)

    was_invalidated = invalidate_session(conn, session_id)

    if not was_invalidated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_or_expired_session",
        )


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
