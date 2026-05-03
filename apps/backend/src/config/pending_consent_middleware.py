from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.config.auth_security import decode_token
from src.database.postgres import get_pg_connection, set_current_user
from src.services.consent_service import get_pending_consent
from src.repositories.user_repository import get_active_session_user


EXEMPT_PREFIXES = (
    "/consent",
    "/terms",
    "/auth/login",
    "/auth/logout",
    "/auth/first-access",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/docs",
    "/redoc",
    "/openapi.json",
)


class PendingConsentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path

        if path.startswith(EXEMPT_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")

        if not auth_header.lower().startswith("bearer "):
            return await call_next(request)

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = decode_token(token)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        session_id = payload.get("sid")
        token_user_id = payload.get("sub")

        if not session_id or not token_user_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "invalid_token"},
            )

        with get_pg_connection() as conn:
            session_user = get_active_session_user(conn, session_id)

            if not session_user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "invalid_or_expired_session"},
                )

            if str(session_user["user_uuid"]) != str(token_user_id):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "invalid_token"},
                )

            if not session_user["active"]:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "inactive_user"},
                )

            user_id = str(session_user["user_uuid"])

            set_current_user(conn, user_id)

            pending_clauses = get_pending_consent(conn, user_id)

        if pending_clauses:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "pending_consent",
                    "pending_clauses": pending_clauses,
                },
            )

        return await call_next(request)