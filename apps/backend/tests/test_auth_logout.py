"""Unit tests for server-side logout and session invalidation."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException


def _make_conn(rowcount: int = 1):
    cursor = MagicMock()
    cursor.rowcount = rowcount

    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    conn.cursor.return_value.__exit__.return_value = False

    return conn, cursor


class TestInvalidateUserSessions:
    def test_executes_update_on_active_sessions_for_user(self):
        from src.repositories.user_repository import invalidate_user_sessions

        conn, cursor = _make_conn()

        invalidate_user_sessions(conn, "user-123")

        cursor.execute.assert_called_once()
        sql, params = cursor.execute.call_args.args

        assert "UPDATE TB_SESSION" in sql
        assert "INVALIDATED_AT = NOW()" in sql
        assert "WHERE USER_ID = %s" in sql
        assert params == ("user-123",)

    def test_create_user_session_keeps_single_active_session_per_user(self):
        from src.repositories.user_repository import create_user_session

        with patch("src.repositories.user_repository.invalidate_user_sessions") as mock_invalidate:
            conn, cursor = _make_conn()
            fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
            cursor.fetchone.return_value = (fake_uuid,)

            session_id = create_user_session(
                conn,
                user_id="user-123",
                source_ip="127.0.0.1",
                user_agent="test-agent",
                expires_at=None,
                refresh_token_hash="hash",
                refresh_expires_at=None,
            )

        mock_invalidate.assert_called_once_with(conn, "user-123")
        assert session_id == fake_uuid


class TestInvalidateSingleSession:
    def test_invalidates_current_non_deleted_session(self):
        from src.repositories.user_repository import invalidate_session

        conn, cursor = _make_conn(rowcount=1)
        session_id = "11111111-1111-1111-1111-111111111111"

        result = invalidate_session(conn, session_id)

        assert result is True
        cursor.execute.assert_called_once()
        sql, params = cursor.execute.call_args.args

        assert "UPDATE TB_SESSION" in sql
        assert "INVALIDATED_AT = NOW()" in sql
        assert "WHERE SESSION_UUID = %s" in sql
        assert "INVALIDATED_AT IS NULL" in sql
        assert "DELETED_AT IS NULL" in sql
        assert params == (session_id,)

    def test_returns_false_for_invalid_uuid_without_query(self):
        from src.repositories.user_repository import invalidate_session

        conn, cursor = _make_conn()

        result = invalidate_session(conn, "not-a-valid-uuid")

        assert result is False
        cursor.execute.assert_not_called()

    def test_returns_false_when_no_session_was_updated(self):
        from src.repositories.user_repository import invalidate_session

        conn, _cursor = _make_conn(rowcount=0)

        result = invalidate_session(conn, "11111111-1111-1111-1111-111111111111")

        assert result is False


class TestLogoutService:
    def test_logout_sets_current_user_and_invalidates_current_session(self):
        from src.services.auth_service import logout

        conn, _cursor = _make_conn()

        with patch("src.services.auth_service.set_current_user") as mock_set_current_user, patch(
            "src.services.auth_service.invalidate_session", return_value=True
        ) as mock_invalidate:
            logout(
                conn,
                user_id="user-abc",
                session_id="11111111-1111-1111-1111-111111111111",
            )

        mock_set_current_user.assert_called_once_with(conn, "user-abc")
        mock_invalidate.assert_called_once_with(
            conn, "11111111-1111-1111-1111-111111111111"
        )

    def test_logout_raises_401_when_session_cannot_be_invalidated(self):
        from src.services.auth_service import logout

        conn, _cursor = _make_conn()

        with patch("src.services.auth_service.set_current_user"), patch(
            "src.services.auth_service.invalidate_session", return_value=False
        ):
            with pytest.raises(HTTPException) as exc_info:
                logout(
                    conn,
                    user_id="user-abc",
                    session_id="11111111-1111-1111-1111-111111111111",
                )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "invalid_or_expired_session"


class TestGetActiveSessionAfterInvalidation:
    def test_invalidated_session_returns_none(self):
        from src.repositories.user_repository import get_active_session_user

        conn, cursor = _make_conn()

        cursor.fetchone.return_value = (
            "session-uuid",
            "user-uuid",
            True,
            True,
            "OPERATOR",
            "2024-01-01",  # INVALIDATED_AT is not None.
            None,
            None,
            None,
        )

        result = get_active_session_user(conn, "session-uuid")

        assert result is None