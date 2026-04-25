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
    Path("logs").mkdir(exist_ok=True)

    handler = TimedRotatingFileHandler(
        filename="logs/app.log",
        when="midnight",
        backupCount=30,
        encoding="utf-8",
    )
    handler.rotator = gz_rotator
    handler.namer = gz_namer

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler, logging.StreamHandler()],
        format="%(message)s",
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )