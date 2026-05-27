import time

import httpx
import structlog

from src.config.settings import Settings

log = structlog.get_logger()


class KeycloakAdminError(Exception):
    pass


class KeycloakUserAlreadyExistsError(KeycloakAdminError):
    pass


class KeycloakUserNotFoundError(KeycloakAdminError):
    pass


class KeycloakAdminClient:
    def __init__(self, settings: Settings):
        self._base_url = settings.keycloak_url.rstrip("/")
        self._realm = settings.keycloak_realm
        self._client_id = settings.keycloak_admin_client_id
        self._username = settings.keycloak_admin_username
        self._password = settings.keycloak_admin_password
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    def _get_admin_token(self) -> str:
        if self._token and time.time() < self._token_expires_at - 10:
            return self._token

        response = httpx.post(
            f"{self._base_url}/realms/master/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": self._client_id,
                "username": self._username,
                "password": self._password,
            },
            timeout=10,
        )

        if response.status_code != 200:
            raise KeycloakAdminError(
                f"Failed to obtain admin token: {response.status_code} {response.text}"
            )

        data = response.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + data.get("expires_in", 60)
        log.debug("keycloak.admin_token.refreshed")
        return self._token

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._get_admin_token()}"}

    def _url(self, path: str) -> str:
        return f"{self._base_url}/admin/realms/{self._realm}/{path.lstrip('/')}"

    def create_user(self, *, username: str, email: str, enabled: bool = True) -> str:
        """Creates a user in Keycloak. Returns the KEYCLOAK_SUB (UUID)."""
        response = httpx.post(
            self._url("users"),
            json={
                "username": username,
                "email": email,
                "enabled": enabled,
                "emailVerified": True,
                "requiredActions": ["UPDATE_PASSWORD"],
            },
            headers=self._headers(),
            timeout=10,
        )

        if response.status_code == 409:
            raise KeycloakUserAlreadyExistsError(
                f"User '{email}' already exists in Keycloak."
            )
        if response.status_code != 201:
            raise KeycloakAdminError(
                f"Failed to create user in Keycloak: {response.status_code} {response.text}"
            )

        location = response.headers.get("Location", "")
        keycloak_sub = location.rstrip("/").split("/")[-1]

        if not keycloak_sub:
            raise KeycloakAdminError(
                "Keycloak did not return a user ID in the Location header."
            )

        log.info("keycloak.user.created", keycloak_sub=keycloak_sub, email=email)
        return keycloak_sub

    def assign_realm_role(self, keycloak_sub: str, role_name: str) -> None:
        """Assigns a realm role to a user."""
        role_resp = httpx.get(
            self._url(f"roles/{role_name}"),
            headers=self._headers(),
            timeout=10,
        )

        if role_resp.status_code == 404:
            raise KeycloakAdminError(
                f"Role '{role_name}' not found in Keycloak realm '{self._realm}'."
            )
        if role_resp.status_code != 200:
            raise KeycloakAdminError(
                f"Failed to fetch role '{role_name}': {role_resp.status_code} {role_resp.text}"
            )

        role = role_resp.json()

        assign_resp = httpx.post(
            self._url(f"users/{keycloak_sub}/role-mappings/realm"),
            json=[{"id": role["id"], "name": role["name"]}],
            headers=self._headers(),
            timeout=10,
        )

        if assign_resp.status_code not in (200, 204):
            raise KeycloakAdminError(
                f"Failed to assign role '{role_name}' to '{keycloak_sub}': "
                f"{assign_resp.status_code} {assign_resp.text}"
            )

        log.info("keycloak.role.assigned", keycloak_sub=keycloak_sub, role=role_name)

    def set_user_enabled(self, keycloak_sub: str, enabled: bool) -> None:
        """Enables or disables a user in Keycloak."""
        response = httpx.put(
            self._url(f"users/{keycloak_sub}"),
            json={"enabled": enabled},
            headers=self._headers(),
            timeout=10,
        )

        if response.status_code == 404:
            raise KeycloakUserNotFoundError(
                f"User '{keycloak_sub}' not found in Keycloak."
            )
        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                f"Failed to update user '{keycloak_sub}': "
                f"{response.status_code} {response.text}"
            )

        log.info("keycloak.user.enabled_updated", keycloak_sub=keycloak_sub, enabled=enabled)

    def delete_user(self, keycloak_sub: str) -> None:
        """Deletes a user from Keycloak."""
        response = httpx.delete(
            self._url(f"users/{keycloak_sub}"),
            headers=self._headers(),
            timeout=10,
        )

        if response.status_code == 404:
            raise KeycloakUserNotFoundError(
                f"User '{keycloak_sub}' not found in Keycloak."
            )
        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                f"Failed to delete user '{keycloak_sub}': "
                f"{response.status_code} {response.text}"
            )

        log.info("keycloak.user.deleted", keycloak_sub=keycloak_sub)

    def update_user_role(
        self, keycloak_sub: str, old_role: str, new_role: str
    ) -> None:
        """Replaces the old realm role with a new one for a user."""
        if old_role == new_role:
            return

        old_role_resp = httpx.get(
            self._url(f"roles/{old_role}"),
            headers=self._headers(),
            timeout=10,
        )
        if old_role_resp.status_code == 200:
            old_role_data = old_role_resp.json()
            httpx.delete(
                self._url(f"users/{keycloak_sub}/role-mappings/realm"),
                json=[{"id": old_role_data["id"], "name": old_role_data["name"]}],
                headers=self._headers(),
                timeout=10,
            )
            log.info(
                "keycloak.role.removed", keycloak_sub=keycloak_sub, role=old_role
            )

        self.assign_realm_role(keycloak_sub, new_role)


_client: KeycloakAdminClient | None = None


def get_keycloak_admin_client() -> KeycloakAdminClient:
    """Returns a module-level singleton so the token cache persists across requests."""
    global _client
    if _client is None:
        _client = KeycloakAdminClient(Settings())
    return _client
