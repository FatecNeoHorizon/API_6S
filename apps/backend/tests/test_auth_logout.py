"""
Unit tests for server-side logout.

After logout, the same access token must be rejected because the session
is marked INVALIDATED_AT = NOW() in TB_SESSION.
"""

from unittest.mock import MagicMock, patch, call
import pytest


def _make_conn():
    conn = MagicMock()
    conn.cursor.return_value.__enter__ = lambda s: s
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn


class TestInvalidateUserSessions:
    def test_executes_update_on_active_sessions(self):
        from src.repositories.user_repository import invalidate_user_sessions

        conn = _make_conn()
        cursor = conn.cursor.return_value

        invalidate_user_sessions(conn, "user-123")

        cursor.execute.assert_called_once()
        sql, params = cursor.execute.call_args.args
        assert "INVALIDATED_AT" in sql
        assert params == ("user-123",)

    def test_create_user_session_calls_invalidate_first(self):
        from src.repositories.user_repository import create_user_session, invalidate_user_sessions

        with patch(
            "src.repositories.user_repository.invalidate_user_sessions"
        ) as mock_invalidate:
            conn = _make_conn()
            cursor = conn.cursor.return_value
            fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
            cursor.fetchone.return_value = (fake_uuid,)

            create_user_session(
                conn,
                user_id="user-123",
                source_ip="127.0.0.1",
                user_agent="test-agent",
                expires_at=None,
                refresh_token_hash="hash",
                refresh_expires_at=None,
            )

        mock_invalidate.assert_called_once_with(conn, "user-123")


class TestLogoutService:
    def test_logout_invalidates_sessions(self):
        from src.services.auth_service import logout

        with patch(
            "src.services.auth_service.invalidate_user_sessions"
        ) as mock_invalidate:
            conn = _make_conn()
            logout(conn, user_id="user-abc")

        mock_invalidate.assert_called_once_with(conn, "user-abc")


class TestGetActiveSessionAfterInvalidation:
    def test_invalidated_session_returns_none(self):
        from src.repositories.user_repository import get_active_session_user

        conn = _make_conn()
        cursor = conn.cursor.return_value

        # Row with INVALIDATED_AT set (index 5 is not None)
        cursor.fetchone.return_value = (
            "session-uuid",   # SESSION_UUID
            "user-uuid",      # USER_UUID
            True,             # ACTIVE
            True,             # FIRST_ACCESS_COMPLETED
            "OPERATOR",       # PROFILE_NAME
            "2024-01-01",     # INVALIDATED_AT — not None → session is invalid
            None,             # EXPIRES_AT
            None,             # DELETED_AT
            None,             # user_deleted_at
        )

        result = get_active_session_user(conn, "session-uuid")

        assert result is None
