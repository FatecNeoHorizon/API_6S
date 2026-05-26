from unittest.mock import MagicMock

from src.services.consent_service import format_consent_history


def _make_conn_with_cursor():
    cursor = MagicMock()
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    conn.cursor.return_value.__exit__.return_value = False
    return conn, cursor


def test_list_user_consent_history_selects_consent_hash():
    from src.repositories.consent_repository import list_user_consent_history

    conn, cursor = _make_conn_with_cursor()
    cursor.fetchall.return_value = []

    list_user_consent_history(conn, "11111111-1111-1111-1111-111111111111")

    query, params = cursor.execute.call_args.args

    assert "cl.CONSENT_HASH" in query
    assert params == ("11111111-1111-1111-1111-111111111111",)


def test_format_consent_history_includes_consent_hash():
    rows = [
        {
            "log_uuid": "log-uuid",
            "action": "CONSENT_ACCEPTED",
            "registered_at": "2026-05-01T10:00:00Z",
            "channel": "WEB",
            "consent_hash": "a" * 64,
            "policy_version_id": "policy-version-uuid",
            "policy_type": "PRIVACY_POLICY",
            "policy_version": "1.0",
            "clause_uuid": "clause-uuid",
            "clause_code": "DATA_COLLECTION",
            "clause_title": "Data Collection",
            "mandatory": True,
        }
    ]

    result = format_consent_history(rows)

    assert result[0]["consent_hash"] == "a" * 64