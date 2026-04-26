from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.database.postgres import get_pg_connection, set_current_user
from src.services.consent_service import AuthenticatedUser, resolve_session


security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    """
    Resolves the authenticated user based on Authorization: Bearer <SESSION_UUID>.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="missing_authentication")

    with get_pg_connection() as conn:
        current_user = resolve_session(conn, credentials.credentials)

        if not current_user:
            raise HTTPException(status_code=401, detail="invalid_or_expired_session")

        set_current_user(conn, current_user.user_id)

    return current_user


def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Allows access only to ADMIN users.
    """
    if current_user.profile_name != "ADMIN":
        raise HTTPException(status_code=403, detail="admin_required")

    return current_user