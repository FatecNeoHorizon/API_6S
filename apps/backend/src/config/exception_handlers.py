import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg2 import IntegrityError, OperationalError

log = structlog.get_logger()


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.error(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        message=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "internal_server_error"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    from src.config.validation import format_validation_errors
    log.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": format_validation_errors(exc.errors())},
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