# apps/backend/tests/test_admin_terms.py

from contextlib import contextmanager
from dataclasses import fields
from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.api.dependencies.auth import AuthenticatedUser, require_admin
from src.api.routes import admin_terms


ADMIN_USER_ID = "11111111-1111-1111-1111-111111111111"
SESSION_ID = "22222222-2222-2222-2222-222222222222"


class FakeConnection:
    pass


@contextmanager
def fake_pg_connection():
    yield FakeConnection()


def make_authenticated_admin() -> AuthenticatedUser:
    """
    Builds AuthenticatedUser in a way that remains compatible if the dataclass
    was extended in other auth branches, such as auth/me.
    """
    values = {
        "user_id": ADMIN_USER_ID,
        "session_id": SESSION_ID,
        "username": "admin",
        "profile_name": "ADMIN",
        "active": True,
    }

    constructor_payload = {
        field.name: values[field.name]
        for field in fields(AuthenticatedUser)
        if field.name in values
    }

    return AuthenticatedUser(**constructor_payload)


def create_test_client(admin_user: AuthenticatedUser | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(admin_terms.router)

    if admin_user is not None:
        app.dependency_overrides[require_admin] = lambda: admin_user

    return TestClient(app)


def sample_policy_version(version_id=None, *, status="vigente"):
    return {
        "policy_version_id": str(version_id or uuid4()),
        "version": "1.0.0",
        "policy_type": "TERMS_OF_USE",
        "content": "Terms content",
        "effective_from": datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
        "created_at": datetime(2025, 12, 1, tzinfo=timezone.utc).isoformat(),
        "status": status,
    }


def sample_policy_version_summary(version_id=None, *, status="vigente"):
    return {
        "policy_version_id": str(version_id or uuid4()),
        "version": "1.0.0",
        "policy_type": "TERMS_OF_USE",
        "effective_from": datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
        "created_at": datetime(2025, 12, 1, tzinfo=timezone.utc).isoformat(),
        "clause_count": 3,
        "status": status,
    }


def test_admin_terms_versions_requires_admin_authentication():
    client = create_test_client()

    response = client.get("/admin/terms/versions")

    assert response.status_code in {401, 403}


def test_get_admin_policy_version_detail_returns_200(monkeypatch):
    version_id = uuid4()
    admin_user = make_authenticated_admin()
    client = create_test_client(admin_user)

    set_current_user_mock = MagicMock()

    monkeypatch.setattr(admin_terms, "get_pg_connection", fake_pg_connection)
    monkeypatch.setattr(admin_terms, "set_current_user", set_current_user_mock)
    monkeypatch.setattr(
        admin_terms,
        "get_policy_version",
        lambda conn, requested_version_id: sample_policy_version(
            version_id=requested_version_id,
            status="vigente",
        ),
    )

    response = client.get(f"/admin/terms/versions/{version_id}")

    assert response.status_code == 200

    body = response.json()

    assert body["policy_version_id"] == str(version_id)
    assert body["version"] == "1.0.0"
    assert body["policy_type"] == "TERMS_OF_USE"
    assert body["content"] == "Terms content"
    assert body["status"] == "vigente"
    assert "effective_from" in body
    assert "created_at" in body

    set_current_user_mock.assert_called_once_with(
        set_current_user_mock.call_args.args[0],
        ADMIN_USER_ID,
    )


def test_get_admin_policy_version_detail_returns_404_when_not_found(monkeypatch):
    version_id = uuid4()
    admin_user = make_authenticated_admin()
    client = create_test_client(admin_user)

    monkeypatch.setattr(admin_terms, "get_pg_connection", fake_pg_connection)
    monkeypatch.setattr(admin_terms, "set_current_user", lambda conn, user_id: None)

    def raise_not_found(conn, requested_version_id):
        raise HTTPException(
            status_code=404,
            detail="policy_version_not_found",
        )

    monkeypatch.setattr(admin_terms, "get_policy_version", raise_not_found)

    response = client.get(f"/admin/terms/versions/{version_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "policy_version_not_found"


def test_list_admin_policy_versions_returns_backend_status(monkeypatch):
    version_id = uuid4()
    admin_user = make_authenticated_admin()
    client = create_test_client(admin_user)

    monkeypatch.setattr(admin_terms, "get_pg_connection", fake_pg_connection)
    monkeypatch.setattr(admin_terms, "set_current_user", lambda conn, user_id: None)
    monkeypatch.setattr(
        admin_terms,
        "list_policy_versions",
        lambda conn: {
            "versions": [
                sample_policy_version_summary(
                    version_id=version_id,
                    status="agendado",
                )
            ]
        },
    )

    response = client.get("/admin/terms/versions")

    assert response.status_code == 200

    body = response.json()

    assert "versions" in body
    assert len(body["versions"]) == 1

    version = body["versions"][0]

    assert version["policy_version_id"] == str(version_id)
    assert version["status"] == "agendado"
    assert version["clause_count"] == 3


def test_create_policy_version_still_requires_admin_authentication():
    client = create_test_client()

    response = client.post(
        "/admin/terms/versions",
        json={
            "version": "2.0.0",
            "policy_type": "TERMS_OF_USE",
            "content": "Updated terms content",
            "effective_from": "2026-01-01T00:00:00Z",
        },
    )

    assert response.status_code in {401, 403}


def test_get_admin_policy_version_detail_does_not_return_404_when_route_exists(monkeypatch):
    """
    Regression test for issue #426.

    The frontend calls /admin/terms/versions/{id}. This route must exist.
    If the route is missing, FastAPI returns 404 before reaching the service.
    """
    version_id = uuid4()
    admin_user = make_authenticated_admin()
    client = create_test_client(admin_user)

    monkeypatch.setattr(admin_terms, "get_pg_connection", fake_pg_connection)
    monkeypatch.setattr(admin_terms, "set_current_user", lambda conn, user_id: None)
    monkeypatch.setattr(
        admin_terms,
        "get_policy_version",
        lambda conn, requested_version_id: sample_policy_version(
            version_id=requested_version_id,
            status="vigente",
        ),
    )

    response = client.get(f"/admin/terms/versions/{version_id}")

    assert response.status_code != 404
    assert response.status_code == 200
