from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.schemas.user_schemas import LoginRequest
from src.repositories.user_repository import log_auth_attempt
from src.services.auth_service import login


def test_log_auth_attempt_inserts_expected_fields_only():
    cursor = MagicMock()
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor

    log_auth_attempt(
        conn,
        email_hash="a" * 64,
        source_ip="192.168.1.0",
        success=True,
        blocked=False,
    )

    cursor.execute.assert_called_once()
    query, params = cursor.execute.call_args.args

    assert "INSERT INTO TB_AUTH_ATTEMPT" in query
    assert "EMAIL_HASH" in query
    assert "SOURCE_IP" in query
    assert "SUCCESS" in query
    assert "BLOCKED" in query
    assert params == ("a" * 64, "192.168.1.0", True, False)