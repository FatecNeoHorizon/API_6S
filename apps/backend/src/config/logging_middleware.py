import time
import uuid
import structlog

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from structlog.contextvars import bind_contextvars, clear_contextvars

from src.config.auth_security import decode_token

log = structlog.get_logger()


def _extract_user_id(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload = decode_token(auth[7:])
        return payload.get("sub")
    except Exception:
        return None


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()

        bind_contextvars(
            request_id=str(uuid.uuid4()),
            method=request.method,
            path=request.url.path,
            user_id=_extract_user_id(request),
        )

        log.info("request_started")

        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        level = "error" if response.status_code >= 500 else "info"
        getattr(log, level)(
            "request_finished",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        clear_contextvars()

        return response