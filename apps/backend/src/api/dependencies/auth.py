from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config.auth_security import decode_token
from src.database.postgres import get_pg_connection, set_current_user
from src.services.consent_service import get_pending_consent
from src.repositories.user_repository import get_active_session_user


security = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    user_id: str
    session_id: str
    profile_name: str


def get_current_user_no_consent_check(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="missing_authentication")

    payload = decode_token(credentials.credentials)
    session_id = payload.get("sid")
    token_user_id = payload.get("sub")

    if not session_id or not token_user_id:
        raise HTTPException(status_code=401, detail="invalid_token")

    with get_pg_connection() as conn:
        session_user = get_active_session_user(conn, session_id)

        if not session_user:
            raise HTTPException(status_code=401, detail="invalid_or_expired_session")

        if str(session_user["user_uuid"]) != str(token_user_id):
            raise HTTPException(status_code=401, detail="invalid_token")

        if not session_user["active"]:
            raise HTTPException(status_code=403, detail="inactive_user")

        set_current_user(conn, str(session_user["user_uuid"]))

    return AuthenticatedUser(
        user_id=str(session_user["user_uuid"]),
        session_id=str(session_user["session_uuid"]),
        profile_name=session_user["profile_name"],
    )


def get_current_user(
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
) -> AuthenticatedUser:
    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)
        pending_clauses = get_pending_consent(conn, current_user.user_id)

    if pending_clauses:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "pending_consent",
                "pending_clauses": pending_clauses,
            },
        )

    return current_user


def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if current_user.profile_name != "ADMIN":
        raise HTTPException(status_code=403, detail="admin_required")

    return current_user