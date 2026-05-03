import json
import logging
import structlog
import pytest

from structlog.testing import capture_logs


def test_log_entry_contains_required_fields():
    with capture_logs() as logs:
        log = structlog.get_logger()
        log.info("test.event", user_id="abc-123", count=5)

    assert len(logs) == 1
    entry = logs[0]
    assert entry["event"] == "test.event"
    assert entry["user_id"] == "abc-123"
    assert entry["count"] == 5


def test_log_entry_does_not_contain_forbidden_fields():
    forbidden = {"email", "cpf", "password", "name", "nome", "senha"}

    with capture_logs() as logs:
        log = structlog.get_logger()
        log.info("user.created", user_id="abc-123", profile_id="xyz-456")

    assert len(logs) == 1
    entry = logs[0]
    found = forbidden & set(entry.keys())
    assert not found, f"Forbidden fields found in log entry: {found}"


def test_log_levels_are_correct():
    with capture_logs() as logs:
        log = structlog.get_logger()
        log.info("info.event")
        log.warning("warning.event")
        log.error("error.event")

    levels = [e["log_level"] for e in logs]
    assert levels == ["info", "warning", "error"]


def test_log_entry_is_json_serializable():
    with capture_logs() as logs:
        log = structlog.get_logger()
        log.info("serializable.event", user_id="abc-123", status_code=200)

    entry = logs[0]
    entry.pop("log_level", None)
    try:
        json.dumps(entry)
    except (TypeError, ValueError) as exc:
        pytest.fail(f"Log entry is not JSON serializable: {exc}")