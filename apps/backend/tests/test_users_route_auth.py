# apps/backend/tests/test_users_route_auth.py

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.dependencies.auth import AuthenticatedUser, get_current_user
from src.api.routes import users
from src.api.schemas.user_schemas import UserCreateResponse, UserResult


USER_ID = "11111111-1111-1111-1111-111111111111"
SESSION_ID = "22222222-2222-2222-2222-222222222222"


def create_test_client(current_user: AuthenticatedUser | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(users.router)

    if current_user is not None:
        app.dependency_overrides[get_current_user] = lambda: current_user

    return TestClient(app)


def authenticated_user(profile_name: str = "USER") -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=USER_ID,
        session_id=SESSION_ID,
        profile_name=profile_name,
    )


def sample_user_result(user_uuid=None) -> UserResult:
    now = datetime.now(timezone.utc)
    return UserResult(
        user_uuid=user_uuid or uuid4(),
        username="TEST_USER",
        profile_id=uuid4(),
        active=True,
        first_access_completed=True,
        created_at=now,
        updated_at=now,
    )


def test_users_routes_require_authentication_without_token():
    client = create_test_client()
    user_uuid = uuid4()
    profile_id = uuid4()

    requests = [
        ("get", "/users/", None),
        ("get", "/users/profiles", None),
        ("get", f"/users/{user_uuid}", None),
        (
            "post",
            "/users/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "Password@123",
                "profile_id": str(profile_id),
            },
        ),
        (
            "patch",
            f"/users/{user_uuid}",
            {"username": "updateduser", "profile_id": str(profile_id)},
        ),
        ("patch", f"/users/{user_uuid}/active", {"active": False}),
        ("delete", f"/users/{user_uuid}", None),
    ]

    for method, path, payload in requests:
        response = (
            getattr(client, method)(path, json=payload)
            if payload is not None
            else getattr(client, method)(path)
        )
        assert response.status_code == 401


def test_read_users_routes_allow_authenticated_user(monkeypatch):
    client = create_test_client(authenticated_user("USER"))
    user_uuid = uuid4()
    profile_id = uuid4()

    monkeypatch.setattr(users, "list_users_service", lambda: [sample_user_result(user_uuid)])
    monkeypatch.setattr(
        users,
        "list_profiles_service",
        lambda: [SimpleNamespace(profile_uuid=profile_id, profile_name="USER")],
    )
    monkeypatch.setattr(users, "get_user_by_id_service", lambda _: sample_user_result(user_uuid))

    assert client.get("/users/").status_code == 200
    assert client.get("/users/profiles").status_code == 200
    assert client.get(f"/users/{user_uuid}").status_code == 200


def test_write_users_routes_reject_authenticated_non_admin():
    client = create_test_client(authenticated_user("USER"))
    user_uuid = uuid4()
    profile_id = uuid4()

    assert client.post(
        "/users/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password@123",
            "profile_id": str(profile_id),
        },
    ).status_code == 403

    assert client.patch(
        f"/users/{user_uuid}",
        json={"username": "updateduser", "profile_id": str(profile_id)},
    ).status_code == 403

    assert client.patch(f"/users/{user_uuid}/active", json={"active": False}).status_code == 403
    assert client.delete(f"/users/{user_uuid}").status_code == 403


def test_write_users_routes_allow_admin(monkeypatch):
    client = create_test_client(authenticated_user("ADMIN"))
    user_uuid = uuid4()
    profile_id = uuid4()
    now = datetime.now(timezone.utc)

    monkeypatch.setattr(
        users,
        "create_user_service",
        lambda _: UserCreateResponse(
            user_uuid=user_uuid,
            username="NEWUSER",
            profile_id=profile_id,
            active=True,
            first_access_completed=False,
            created_at=now,
        ),
    )
    monkeypatch.setattr(users, "update_user_service", lambda *_: sample_user_result(user_uuid))
    monkeypatch.setattr(users, "set_user_active_service", lambda *_: sample_user_result(user_uuid))
    monkeypatch.setattr(users, "delete_user_service", lambda _: None)

    assert client.post(
        "/users/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password@123",
            "profile_id": str(profile_id),
        },
    ).status_code == 201

    assert client.patch(
        f"/users/{user_uuid}",
        json={"username": "updateduser", "profile_id": str(profile_id)},
    ).status_code == 200

    assert client.patch(f"/users/{user_uuid}/active", json={"active": False}).status_code == 200
    assert client.delete(f"/users/{user_uuid}").status_code == 204