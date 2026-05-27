from contextlib import contextmanager
from dataclasses import fields
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.dependencies.auth import AuthenticatedUser, require_admin
from src.api.routes import admin_terms
from src.services import policy_update_notification_service as service


ADMIN_USER_ID = "11111111-1111-1111-1111-111111111111"
SESSION_ID = "22222222-2222-2222-2222-222222222222"


class FakeConnection:
    pass


@contextmanager
def fake_pg_connection():
    yield FakeConnection()


def make_authenticated_admin() -> AuthenticatedUser:
    values = {
        "user_id": ADMIN_USER_ID,
        "session_id": SESSION_ID,
        "username": "admin",
        "profile_name": "ADMIN",
        "first_access_completed": True,
        "active": True,
    }
    payload = {
        field.name: values[field.name]
        for field in fields(AuthenticatedUser)
        if field.name in values
    }
    return AuthenticatedUser(**payload)


def test_create_policy_version_automatically_schedules_user_notification(monkeypatch):
    app = FastAPI()
    app.include_router(admin_terms.router)
    app.dependency_overrides[require_admin] = make_authenticated_admin
    client = TestClient(app)
    dispatch_mock = MagicMock()
    created_version = {
        "policy_version_id": "33333333-3333-4333-8333-333333333333",
        "version": "2.0.0",
        "policy_type": "TERMS_OF_USE",
        "effective_from": "2030-01-01T00:00:00+00:00",
    }

    monkeypatch.setattr(admin_terms, "get_pg_connection", fake_pg_connection)
    monkeypatch.setattr(admin_terms, "set_current_user", lambda conn, user_id: None)
    monkeypatch.setattr(admin_terms, "create_policy_version", lambda **kwargs: created_version)
    monkeypatch.setattr(
        admin_terms,
        "prepare_policy_update_notification",
        lambda conn, version: (["user@example.com"], "subject", "<p>body</p>", "body", 1),
    )
    monkeypatch.setattr(admin_terms, "dispatch_policy_update_emails_task", dispatch_mock)

    response = client.post(
        "/admin/terms/versions",
        json={
            "version": "2.0.0",
            "policy_type": "TERMS_OF_USE",
            "content": "Updated terms content",
            "effective_from": "2030-01-01T00:00:00Z",
        },
    )

    assert response.status_code == 201
    dispatch_mock.assert_called_once_with(["user@example.com"], "subject", "<p>body</p>", "body")


def test_notification_informs_users_before_policy_becomes_effective(monkeypatch):
    monkeypatch.setattr(service, "Settings", lambda: object())
    monkeypatch.setattr(service, "list_active_user_email_enc", lambda conn: ["encrypted-user"])
    monkeypatch.setattr(service, "_decrypt_email", lambda encrypted_email, settings: "user@example.com")

    emails, subject, body_html, body_text, recipient_count = service.prepare_policy_update_notification(
        object(),
        {
            "version": "2.0.0",
            "policy_type": "PRIVACY_POLICY",
            "effective_from": "2030-01-01T00:00:00+00:00",
        },
    )

    assert emails == ["user@example.com"]
    assert recipient_count == 1
    assert "Pol\u00edtica de Privacidade" in subject
    assert "2030-01-01T00:00:00+00:00" in body_text
    assert "revogar seu consentimento" in body_text
    assert "Art. 8" in body_text
    assert "Pol\u00edtica de Privacidade" in body_html
