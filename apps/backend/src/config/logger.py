import gzip
import logging
import shutil
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import structlog


def gz_rotator(source: str, dest: str) -> None:
    with open(source, "rb") as f_in:
        with gzip.open(f"{dest}.gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    Path(source).unlink()


def gz_namer(name: str) -> str:
    return name

def configure_logging() -> None:
    Path("/app/logs").mkdir(exist_ok=True)

    handler = TimedRotatingFileHandler(
        filename="/app/logs/app.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    handler.rotator = gz_rotator
    handler.namer = gz_namer
    handler.setFormatter(logging.Formatter("%(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,  # novo — injeta request_id, method, path, user_id
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)