from unittest.mock import MagicMock

from src.repositories.user_repository import invalidate_session


def test_invalidate_session_updates_current_non_deleted_session_only():
    cursor = MagicMock()
    cursor.rowcount = 1
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor

    assert invalidate_session(
        conn,
        "11111111-1111-1111-1111-111111111111",
    ) is True

    cursor.execute.assert_called_once()
    query, params = cursor.execute.call_args.args

    assert "UPDATE TB_SESSION" in query
    assert "INVALIDATED_AT = NOW()" in query
    assert "WHERE SESSION_UUID = %s" in query
    assert "INVALIDATED_AT IS NULL" in query
    assert "DELETED_AT IS NULL" in query
    assert params == ("11111111-1111-1111-1111-111111111111",)