from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.api.dependencies.auth import AuthenticatedUser, get_current_user_no_consent_check
from src.api.routes import users
from src.services.consent_service import update_user_consent_preferences


class ConsentUpdateItem:
    def __init__(self, clause_id, accepted):
        self.clause_id = clause_id
        self.accepted = accepted


def test_optional_consent_revocation_only_logs_event():
    conn = MagicMock()
    user_id = str(uuid4())
    clause_id = str(uuid4())
    policy_version_id = str(uuid4())

    with patch(
        "src.services.consent_service.consent_repository.get_current_clause_for_consent_update",
        return_value={
            "clause_uuid": clause_id,
            "policy_version_id": policy_version_id,
            "mandatory": False,
        },
    ), patch(
        "src.services.consent_service.consent_repository.insert_consent_event",
        return_value=True,
    ) as mock_insert, patch(
        "src.services.consent_service.delete_user"
    ) as mock_delete, patch(
        "src.services.consent_service.invalidate_user_sessions"
    ) as mock_invalidate, patch(
        "src.services.consent_service.get_user_consent_preferences",
        return_value=[],
    ):
        result = update_user_consent_preferences(
            conn,
            user_id=user_id,
            updates=[ConsentUpdateItem(clause_id, False)],
            source_ip="127.0.0.1",
            user_agent="pytest",
        )

    assert result == {
        "account_deleted": False,
        "updated_count": 1,
        "consents": [],
    }
    mock_insert.assert_called_once()
    assert mock_insert.call_args.kwargs["event_action"] == "CONSENT_REVOKED"
    mock_delete.assert_not_called()
    mock_invalidate.assert_not_called()


def test_optional_consent_acceptance_only_logs_event():
    conn = MagicMock()
    user_id = str(uuid4())
    clause_id = str(uuid4())
    policy_version_id = str(uuid4())

    with patch(
        "src.services.consent_service.consent_repository.get_current_clause_for_consent_update",
        return_value={
            "clause_uuid": clause_id,
            "policy_version_id": policy_version_id,
            "mandatory": False,
        },
    ), patch(
        "src.services.consent_service.consent_repository.insert_consent_event",
        return_value=True,
    ) as mock_insert, patch(
        "src.services.consent_service.delete_user"
    ) as mock_delete, patch(
        "src.services.consent_service.invalidate_user_sessions"
    ) as mock_invalidate, patch(
        "src.services.consent_service.get_user_consent_preferences",
        return_value=[],
    ):
        result = update_user_consent_preferences(
            conn,
            user_id=user_id,
            updates=[ConsentUpdateItem(clause_id, True)],
            source_ip="127.0.0.1",
            user_agent="pytest",
        )

    assert result["account_deleted"] is False
    assert result["updated_count"] == 1
    assert result["consents"] == []
    assert mock_insert.call_args.kwargs["event_action"] == "CONSENT_ACCEPTED"
    mock_delete.assert_not_called()
    mock_invalidate.assert_not_called()


def test_mandatory_consent_revocation_deletes_and_invalidates_sessions():
    conn = MagicMock()
    user_id = str(uuid4())
    clause_id = str(uuid4())
    policy_version_id = str(uuid4())

    with patch(
        "src.services.consent_service.consent_repository.get_current_clause_for_consent_update",
        return_value={
            "clause_uuid": clause_id,
            "policy_version_id": policy_version_id,
            "mandatory": True,
        },
    ), patch(
        "src.services.consent_service.consent_repository.insert_consent_event",
        return_value=True,
    ) as mock_insert, patch(
        "src.services.consent_service.delete_user",
        return_value=True,
    ) as mock_delete, patch(
        "src.services.consent_service.invalidate_user_sessions",
        return_value=True,
    ) as mock_invalidate:
        result = update_user_consent_preferences(
            conn,
            user_id=user_id,
            updates=[ConsentUpdateItem(clause_id, False)],
            source_ip="127.0.0.1",
            user_agent="pytest",
        )

    assert result == {
        "account_deleted": True,
        "updated_count": 1,
        "consents": None,
    }
    assert mock_insert.call_args.kwargs["event_action"] == "CONSENT_REVOKED"
    mock_delete.assert_called_once_with(conn, user_id)
    mock_invalidate.assert_called_once_with(conn, user_id)


def test_mandatory_consent_acceptance_does_not_delete_account():
    conn = MagicMock()
    user_id = str(uuid4())
    clause_id = str(uuid4())
    policy_version_id = str(uuid4())

    with patch(
        "src.services.consent_service.consent_repository.get_current_clause_for_consent_update",
        return_value={
            "clause_uuid": clause_id,
            "policy_version_id": policy_version_id,
            "mandatory": True,
        },
    ), patch(
        "src.services.consent_service.consent_repository.insert_consent_event",
        return_value=True,
    ), patch(
        "src.services.consent_service.delete_user"
    ) as mock_delete, patch(
        "src.services.consent_service.invalidate_user_sessions"
    ) as mock_invalidate, patch(
        "src.services.consent_service.get_user_consent_preferences",
        return_value=[],
    ):
        result = update_user_consent_preferences(
            conn,
            user_id=user_id,
            updates=[ConsentUpdateItem(clause_id, True)],
            source_ip="127.0.0.1",
            user_agent="pytest",
        )

    assert result["account_deleted"] is False
    assert result["updated_count"] == 1
    mock_delete.assert_not_called()
    mock_invalidate.assert_not_called()


def test_invalid_clause_returns_422():
    conn = MagicMock()

    with patch(
        "src.services.consent_service.consent_repository.get_current_clause_for_consent_update",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc:
            update_user_consent_preferences(
                conn,
                user_id=str(uuid4()),
                updates=[ConsentUpdateItem(str(uuid4()), True)],
                source_ip="127.0.0.1",
                user_agent="pytest",
            )

    assert exc.value.status_code == 422
    assert exc.value.detail["code"] == "invalid_clause_id"


def test_duplicate_clause_id_returns_422():
    conn = MagicMock()
    clause_id = str(uuid4())

    with patch(
        "src.services.consent_service.consent_repository.get_current_clause_for_consent_update",
        return_value={
            "clause_uuid": clause_id,
            "policy_version_id": str(uuid4()),
            "mandatory": False,
        },
    ), patch(
        "src.services.consent_service.consent_repository.insert_consent_event",
        return_value=True,
    ):
        with pytest.raises(HTTPException) as exc:
            update_user_consent_preferences(
                conn,
                user_id=str(uuid4()),
                updates=[
                    ConsentUpdateItem(clause_id, True),
                    ConsentUpdateItem(clause_id, False),
                ],
                source_ip="127.0.0.1",
                user_agent="pytest",
            )

    assert exc.value.status_code == 422
    assert exc.value.detail["code"] == "duplicate_clause_id"


def test_user_cannot_update_another_users_consents():
    current_user_id = str(uuid4())
    other_user_id = str(uuid4())

    app = FastAPI()
    app.include_router(users.router)
    app.dependency_overrides[get_current_user_no_consent_check] = lambda: AuthenticatedUser(
        user_id=current_user_id,
        session_id=str(uuid4()),
        username="regular_user",
        profile_name="USER",
        first_access_completed=True,
        active=True,
    )

    client = TestClient(app)

    response = client.patch(
        f"/users/{other_user_id}/consents",
        json={
            "consents": [
                {
                    "clause_id": str(uuid4()),
                    "accepted": True,
                }
            ]
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "cannot_manage_other_user_consents"
