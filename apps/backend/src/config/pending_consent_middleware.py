from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.database.postgres import get_pg_connection, set_current_user
from src.services.consent_service import get_pending_consent, resolve_session


EXEMPT_PREFIXES = (
    "/consent",
    "/terms",
    "/auth/login",
    "/auth/logout",
    "/docs",
    "/redoc",
    "/openapi.json",
)


class PendingConsentMiddleware(BaseHTTPMiddleware):
    """
    Blocks authenticated requests when the authenticated user has pending
    mandatory clauses.
    """

    async def dispatch(self, request, call_next):
        path = request.url.path

        if path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")

        if not auth_header.lower().startswith("bearer "):
            return await call_next(request)

        token = auth_header.split(" ", 1)[1].strip()

        with get_pg_connection() as conn:
            current_user = resolve_session(conn, token)

            if not current_user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "invalid_or_expired_session"},
                )

            set_current_user(conn, current_user.user_id)

            pending_clauses = get_pending_consent(conn, current_user.user_id)

        if pending_clauses:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "pending_consent",
                    "pending_clauses": pending_clauses,
                },
            )

        return await call_next(request)