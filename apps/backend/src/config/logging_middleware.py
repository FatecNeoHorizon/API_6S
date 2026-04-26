import time
import uuid
import structlog

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from structlog.contextvars import bind_contextvars, clear_contextvars

log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()

        bind_contextvars(
            request_id=str(uuid.uuid4()),
            method=request.method,
            path=request.url.path,
            user_id=None,  # JWT not implemented yet
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