from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.dependencies.auth import AuthenticatedUser, get_current_user
from src.api.routes import auth


def create_test_app_with_user(current_user: AuthenticatedUser):
    app = FastAPI()
    app.include_router(auth.router)
    app.dependency_overrides[get_current_user] = lambda: current_user
    return app


def test_get_auth_me_returns_authenticated_user_context():
    user_id = uuid4()
    session_id = uuid4()

    app = create_test_app_with_user(
        AuthenticatedUser(
            user_id=str(user_id),
            session_id=str(session_id),
            username="admin",
            profile_name="ADMIN",
            first_access_completed=True,
            active=True,
        )
    )

    client = TestClient(app)
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": str(user_id),
        "username": "admin",
        "profile": "ADMIN",
        "first_access_completed": True,
        "active": True,
    }


def test_get_auth_me_does_not_expose_sensitive_or_internal_fields():
    user_id = uuid4()
    session_id = uuid4()

    app = create_test_app_with_user(
        AuthenticatedUser(
            user_id=str(user_id),
            session_id=str(session_id),
            username="admin",
            profile_name="ADMIN",
            first_access_completed=True,
            active=True,
        )
    )

    client = TestClient(app)
    response = client.get("/auth/me")

    assert response.status_code == 200
    body = response.json()

    forbidden_fields = {
        "password",
        "password_hash",
        "email",
        "email_hash",
        "email_enc",
        "session_id",
        "refresh_token",
        "access_token",
        "token",
    }

    for field in forbidden_fields:
        assert field not in body