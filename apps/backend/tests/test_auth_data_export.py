from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException


def _make_conn():
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = lambda s: s
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn


def test_export_user_data_returns_complete_portability_package():
    from src.services.auth_service import export_user_data

    conn = _make_conn()
    now = datetime(2026, 5, 21, 12, 0, tzinfo=timezone.utc)
    user_id = "550e8400-e29b-41d4-a716-446655440000"

    with (
        patch("src.services.auth_service.set_current_user") as mock_set_current_user,
        patch("src.services.auth_service._decrypt_email", return_value="user@example.com"),
        patch(
            "src.services.auth_service.get_user_for_export",
            return_value={
                "user_uuid": UUID(user_id),
                "username": "analyst_active",
                "email_enc": "encrypted-email",
                "active": True,
                "first_access_completed": True,
                "created_at": now,
                "updated_at": now,
                "anonymized_at": None,
                "profile_name": "ANALYST",
            },
        ),
        patch(
            "src.services.auth_service.list_user_consent_history",
            return_value=[
                {
                    "log_uuid": UUID("11111111-1111-4111-8111-111111111111"),
                    "clause_uuid": UUID("22222222-2222-4222-8222-222222222222"),
                    "clause_code": "DATA_COLLECTION",
                    "clause_title": "Data collection",
                    "policy_version_id": UUID("33333333-3333-4333-8333-333333333333"),
                    "policy_type": "PRIVACY_POLICY",
                    "policy_version": "1.0",
                    "action": "CONSENT_ACCEPTED",
                    "registered_at": now,
                    "source_ip": "127.0.0.1",
                    "user_agent": "pytest",
                    "channel": "WEB",
                }
            ],
        ),
        patch(
            "src.services.auth_service.get_sessions_for_export",
            return_value=[
                {
                    "session_uuid": UUID("44444444-4444-4444-8444-444444444444"),
                    "source_ip": "127.0.0.1",
                    "user_agent": "pytest",
                    "created_at": now,
                    "updated_at": now,
                    "expires_at": now,
                    "invalidated_at": None,
                }
            ],
        ),
    ):
        result = export_user_data(conn, user_id=user_id)

    mock_set_current_user.assert_called_once_with(conn, user_id)
    assert result.identity.email == "user@example.com"
    assert result.identity.profile == "ANALYST"
    assert result.consent_history[0].clause_code == "DATA_COLLECTION"
    assert result.consent_history[0].channel == "WEB"
    assert result.session_history[0].created_at == now


def test_export_user_data_rejects_anonymized_user():
    from src.services.auth_service import export_user_data

    conn = _make_conn()
    user_id = "550e8400-e29b-41d4-a716-446655440000"

    with patch(
        "src.services.auth_service.get_user_for_export",
        return_value={"anonymized_at": datetime.now(timezone.utc)},
    ):
        with pytest.raises(HTTPException) as exc_info:
            export_user_data(conn, user_id=user_id)

    assert exc_info.value.status_code == 410
    assert exc_info.value.detail == "user_data_no_longer_exists"
