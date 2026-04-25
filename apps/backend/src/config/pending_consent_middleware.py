from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.database.postgres import dict_cursor, get_pg_connection, set_current_user
from src.repositories.consent_repository import list_pending_clauses


EXEMPT_PREFIXES = (
    "/consent",
    "/terms",
    "/auth/login",
    "/auth/logout",
    "/docs",
    "/redoc",
    "/openapi.json",
)


def format_pending_clauses(rows: list[dict]) -> list[dict]:
    return [
        {
            "clause_uuid": str(row["clause_uuid"]),
            "policy_version_id": str(row["policy_version_id"]),
            "policy_type": row["policy_type"],
            "version": row["version"],
            "code": row["clause_code"],
            "title": row["clause_title"],
            "description": row["clause_description"],
            "mandatory": row["mandatory"],
            "display_order": row["display_order"],
        }
        for row in rows
    ]


class PendingConsentMiddleware(BaseHTTPMiddleware):
    """
    Blocks authenticated requests when the authenticated user has pending
    mandatory clauses.

    This centralizes consent enforcement and avoids relying only on frontend checks.
    """

    async def dispatch(self, request, call_next):
        path = request.url.path

        if path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")

        if not auth_header.lower().startswith("bearer "):
            return await call_next(request)

        token = auth_header.split(" ", 1)[1].strip()

        try:
            session_uuid = str(UUID(token))
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"detail": "invalid_session_token"},
            )

        with get_pg_connection() as conn:
            with dict_cursor(conn) as cur:
                cur.execute(
                    """
                    SELECT
                        u.USER_UUID
                    FROM TB_SESSION s
                    JOIN TB_USER u
                      ON u.USER_UUID = s.USER_ID
                    WHERE s.SESSION_UUID = %s
                      AND s.INVALIDATED_AT IS NULL
                      AND s.EXPIRES_AT > NOW()
                      AND s.DELETED_AT IS NULL
                      AND u.ACTIVE = TRUE
                      AND u.DELETED_AT IS NULL
                    """,
                    (session_uuid,),
                )

                user = cur.fetchone()

            if not user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "invalid_or_expired_session"},
                )

            user_id = str(user["user_uuid"])

            set_current_user(conn, user_id)

            pending = list_pending_clauses(conn, user_id)

        if pending:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "pending_consent",
                    "pending_clauses": format_pending_clauses(pending),
                },
            )

        return await call_next(request)