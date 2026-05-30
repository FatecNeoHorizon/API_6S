import structlog
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import ExecutionTimeout, NetworkTimeout, PyMongoError, ServerSelectionTimeoutError
from psycopg2 import IntegrityError, OperationalError

from src.api.schemas.response import error_response

log = structlog.get_logger()


def _classify_unhandled_exception(exc: Exception) -> tuple[int, str, str]:
    if isinstance(exc, ExecutionTimeout):
        return 504, "mongo_query_timeout", "timeout"

    if isinstance(exc, (NetworkTimeout, TimeoutError)):
        return 504, "operation_timeout", "timeout"

    if isinstance(exc, (ServerSelectionTimeoutError, OperationalError)):
        return 503, "database_unavailable", "database"

    if isinstance(exc, IntegrityError):
        return 409, "database_integrity_error", "database"

    if isinstance(exc, PyMongoError):
        return 503, "mongo_error", "database"

    if str(exc) in {"db_operational_error", "db_integrity_error"}:
        status_code = 503 if str(exc) == "db_operational_error" else 409
        return status_code, str(exc), "database"

    return 500, "internal_server_error", "internal"


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    status_code, error_code, category = _classify_unhandled_exception(exc)

    log.error(
        "unhandled_exception",
        error_code=error_code,
        category=category,
        status_code=status_code,
        exception_type=type(exc).__name__,
        message=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response(error_code, category=category),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.detail),
        headers=exc.headers,
    )


_SENSITIVE_FIELDS = {"password", "senha", "new_password", "confirm_password", "token"}


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    from src.config.validation import format_validation_errors
    safe_errors = [
        e for e in exc.errors()
        if not any(f in _SENSITIVE_FIELDS for f in e.get("loc", []))
    ]
    log.warning(
        "validation_error",
        path=request.url.path,
        error_count=len(exc.errors()),
        errors=safe_errors,
    )
    return JSONResponse(
        status_code=422,
        content=error_response(format_validation_errors(exc.errors())),
    )


def handle_db_integrity_error(exc: IntegrityError, context: str = "") -> None:
    log.warning(
        "db_integrity_error",
        context=context,
        message=str(exc).splitlines()[0],
    )
    raise Exception("db_integrity_error") from exc


def handle_db_operational_error(exc: OperationalError, context: str = "") -> None:
    log.error(
        "db_operational_error",
        context=context,
        message=str(exc).splitlines()[0],
    )
    raise Exception("db_operational_error") from exc
