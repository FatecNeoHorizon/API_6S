from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.database.postgres import dict_cursor, get_pg_connection


security = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    user_id: str
    session_id: str
    profile_name: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthenticatedUser:
    """
    Resolves the authenticated user based on Authorization: Bearer <SESSION_UUID>.

    This project already has TB_SESSION in PostgreSQL. Therefore, the minimal
    implementation uses SESSION_UUID as the bearer token.

    If the project later adopts JWT, only this dependency should be replaced.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="missing_authentication")

    try:
        session_uuid = str(UUID(credentials.credentials))
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid_session_token")

    with get_pg_connection() as conn:
        with dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT
                    s.SESSION_UUID,
                    u.USER_UUID,
                    p.PROFILE_NAME
                FROM TB_SESSION s
                JOIN TB_USER u
                  ON u.USER_UUID = s.USER_ID
                JOIN TB_PROFILE p
                  ON p.PROFILE_UUID = u.PROFILE_ID
                WHERE s.SESSION_UUID = %s
                  AND s.INVALIDATED_AT IS NULL
                  AND s.EXPIRES_AT > NOW()
                  AND s.DELETED_AT IS NULL
                  AND u.ACTIVE = TRUE
                  AND u.DELETED_AT IS NULL
                """,
                (session_uuid,),
            )

            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="invalid_or_expired_session")

    return AuthenticatedUser(
        user_id=str(row["user_uuid"]),
        session_id=str(row["session_uuid"]),
        profile_name=row["profile_name"],
    )


def require_admin(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """
    Allows access only to ADMIN users.
    """
    if current_user.profile_name != "ADMIN":
        raise HTTPException(status_code=403, detail="admin_required")

    return current_user