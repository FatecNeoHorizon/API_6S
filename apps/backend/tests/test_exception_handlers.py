from pymongo.errors import ExecutionTimeout, ServerSelectionTimeoutError
from psycopg2 import OperationalError

from src.config.exception_handlers import _classify_unhandled_exception


def test_classify_mongo_execution_timeout():
    assert _classify_unhandled_exception(ExecutionTimeout("slow query")) == (
        504,
        "mongo_query_timeout",
        "timeout",
    )


def test_classify_database_unavailable_errors():
    assert _classify_unhandled_exception(ServerSelectionTimeoutError("no server")) == (
        503,
        "database_unavailable",
        "database",
    )
    assert _classify_unhandled_exception(OperationalError("connection failed")) == (
        503,
        "database_unavailable",
        "database",
    )


def test_classify_unknown_error_as_internal():
    assert _classify_unhandled_exception(RuntimeError("boom")) == (
        500,
        "internal_server_error",
        "internal",
    )
