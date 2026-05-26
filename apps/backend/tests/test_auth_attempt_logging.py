from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.api.schemas.user_schemas import LoginRequest
from src.repositories.user_repository import log_auth_attempt
from src.services import auth_service
from src.services.auth_service import login


def _make_conn():
    cursor = MagicMock()

    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    conn.cursor.return_value.__exit__.return_value = False

    return conn, cursor


def test_log_auth_attempt_inserts_expected_fields_only():
    conn, cursor = _make_conn()

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
    assert "PASSWORD" not in query.upper()
    assert "EMAIL_ENC" not in query.upper()
    assert params == ("a" * 64, "192.168.1.0", True, False)


@pytest.mark.parametrize(
    ("raw_ip", "expected"),
    [
        ("192.168.1.123", "192.168.1.0"),
        ("10.0.0.45", "10.0.0.0"),
        ("unknown", "unknown"),
        ("", "unknown"),
        (None, "unknown"),
        ("not-an-ip", "unknown"),
        ("2001:db8:85a3::8a2e:370:7334", "2001:0db8:85a3:0000::"),
    ],
)
def test_mask_source_ip(raw_ip, expected):
    assert auth_service._mask_source_ip(raw_ip) == expected


def test_login_success_records_successful_attempt():
    conn, _cursor = _make_conn()
    user_id = uuid4()

    with patch(
        "src.services.auth_service.get_user_auth_by_email_hash",
        return_value={
            "user_uuid": user_id,
            "username": "admin",
            "password_hash": "stored-hash",
            "active": True,
            "first_access_completed": True,
            "profile_name": "ADMIN",
        },
    ), patch("src.services.auth_service.verify_password", return_value=True), patch(
        "src.services.auth_service._create_session_and_token",
        return_value={
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
            "pending_consent": False,
            "pending_clauses": [],
        },
    ), patch("src.services.auth_service.log_auth_attempt") as mock_log:
        response = login(
            conn,
            payload=LoginRequest(email="admin@example.com", password="Password@123"),
            source_ip="192.168.1.123",
            user_agent="pytest",
        )

    assert response["access_token"] == "access"
    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["source_ip"] == "192.168.1.0"
    assert kwargs["success"] is True
    assert kwargs["blocked"] is False


def test_login_unknown_user_records_failed_attempt_and_commits():
    conn, _cursor = _make_conn()

    with patch("src.services.auth_service.get_user_auth_by_email_hash", return_value=None), patch(
        "src.services.auth_service.log_auth_attempt"
    ) as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            login(
                conn,
                payload=LoginRequest(email="missing@example.com", password="wrong"),
                source_ip="10.0.0.45",
                user_agent="pytest",
            )

    assert exc_info.value.status_code == 401
    mock_log.assert_called_once()
    kwargs = mock_log.call_args.kwargs
    assert kwargs["source_ip"] == "10.0.0.0"
    assert kwargs["success"] is False
    assert kwargs["blocked"] is False
    conn.commit.assert_called_once()


def test_login_inactive_user_records_blocked_attempt_and_commits():
    conn, _cursor = _make_conn()

    with patch(
        "src.services.auth_service.get_user_auth_by_email_hash",
        return_value={
            "user_uuid": uuid4(),
            "username": "inactive",
            "password_hash": "stored-hash",
            "active": False,
            "first_access_completed": True,
            "profile_name": "USER",
        },
    ), patch("src.services.auth_service.log_auth_attempt") as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            login(
                conn,
                payload=LoginRequest(email="inactive@example.com", password="Password@123"),
                source_ip="192.168.1.123",
                user_agent="pytest",
            )

    assert exc_info.value.status_code == 401
    kwargs = mock_log.call_args.kwargs
    assert kwargs["success"] is False
    assert kwargs["blocked"] is True
    conn.commit.assert_called_once()


def test_login_first_access_pending_records_blocked_attempt_and_commits():
    conn, _cursor = _make_conn()

    with patch(
        "src.services.auth_service.get_user_auth_by_email_hash",
        return_value={
            "user_uuid": uuid4(),
            "username": "pending",
            "password_hash": "stored-hash",
            "active": True,
            "first_access_completed": False,
            "profile_name": "USER",
        },
    ), patch("src.services.auth_service.log_auth_attempt") as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            login(
                conn,
                payload=LoginRequest(email="pending@example.com", password="Password@123"),
                source_ip="192.168.1.123",
                user_agent="pytest",
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "first_access_required"
    kwargs = mock_log.call_args.kwargs
    assert kwargs["success"] is False
    assert kwargs["blocked"] is True
    conn.commit.assert_called_once()


def test_login_wrong_password_records_failed_attempt_and_commits():
    conn, _cursor = _make_conn()

    with patch(
        "src.services.auth_service.get_user_auth_by_email_hash",
        return_value={
            "user_uuid": uuid4(),
            "username": "admin",
            "password_hash": "stored-hash",
            "active": True,
            "first_access_completed": True,
            "profile_name": "ADMIN",
        },
    ), patch("src.services.auth_service.verify_password", return_value=False), patch(
        "src.services.auth_service.log_auth_attempt"
    ) as mock_log:
        with pytest.raises(HTTPException) as exc_info:
            login(
                conn,
                payload=LoginRequest(email="admin@example.com", password="wrong"),
                source_ip="192.168.1.123",
                user_agent="pytest",
            )

    assert exc_info.value.status_code == 401
    kwargs = mock_log.call_args.kwargs
    assert kwargs["success"] is False
    assert kwargs["blocked"] is False
    conn.commit.assert_called_once()