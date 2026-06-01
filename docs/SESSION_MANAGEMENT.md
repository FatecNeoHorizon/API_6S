# Session Management

This document describes how user sessions are created, maintained, renewed, and terminated in the Zeus platform.

## Overview

Sessions are managed by the backend independently of Keycloak's own session tracking. After the OAuth callback, the platform issues its own short-lived `access_token` and long-lived `refresh_token`, and stores a session record in PostgreSQL. Keycloak tokens are **not stored** — only the Keycloak `sub` claim is kept as a link in `TB_USER.KEYCLOAK_SUB`.

---

## Session Lifecycle

```
OAuth Callback
      │
      ▼
Backend exchanges code → Keycloak returns access_token + id_token
      │
      ▼
Backend validates Keycloak token (JWKS) and extracts: sub, roles, preferred_username
      │
      ▼
Looks up TB_USER by KEYCLOAK_SUB
  - User not found → 401 user_not_registered
  - User inactive   → 403 inactive_user
      │
      ▼
Creates row in TB_SESSION:
  - SESSION_UUID, USER_ID, SOURCE_IP (masked), USER_AGENT
  - EXPIRES_AT = now + jwt_refresh_token_expire_days
  - REFRESH_TOKEN_HASH = SHA-256(refresh_token)
      │
      ▼
Issues platform tokens:
  - access_token  → short-lived JWT (signed by backend, contains user_id + session_id + profile + username)
  - refresh_token → opaque random 48-byte URL-safe token
      │
      ▼
Checks pending consent (V_PENDING_CONSENT view)
  → Response includes pending_consent: true/false + pending_clauses list
```

---

## Database Table: `TB_SESSION`

| Column | Type | Description |
|:---|:---|:---|
| `SESSION_UUID` | UUID PK | Unique session identifier |
| `USER_ID` | UUID FK | Reference to `TB_USER.USER_UUID` |
| `SOURCE_IP` | VARCHAR | Masked client IP at login time |
| `USER_AGENT` | VARCHAR | Browser/client user-agent string |
| `EXPIRES_AT` | TIMESTAMPTZ | When the refresh token expires |
| `INVALIDATED_AT` | TIMESTAMPTZ | Set on logout or admin revocation; `NULL` = active |
| `CREATED_AT` | TIMESTAMPTZ | Session creation timestamp |
| `UPDATED_AT` | TIMESTAMPTZ | Last refresh timestamp |

**Constraint:** `UX_TB_SESSION_ONE_ACTIVE_PER_USER` — only one session with `INVALIDATED_AT IS NULL` is allowed per user at any time. A new login automatically replaces any existing active session.

---

## Token Types

| Token | Type | Lifetime | Storage |
|:---|:---|:---|:---|
| `access_token` | Signed JWT (backend key) | Short (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`) | Client memory / localStorage |
| `refresh_token` | Opaque URL-safe random string | Long (`JWT_REFRESH_TOKEN_EXPIRE_DAYS`) | Client storage |

The `access_token` contains: `user_id`, `session_id`, `profile_name`, `username`, `exp`.

The `refresh_token` is stored only as a hash (`REFRESH_TOKEN_HASH`) in `TB_SESSION` — the plain value is never persisted.

---

## Endpoints

### `POST /auth/callback`
Exchanges the OAuth authorization code for platform tokens.

**Request:**
```json
{
  "code": "<authorization_code>",
  "code_verifier": "<pkce_verifier>",
  "redirect_uri": "http://localhost:5173/auth/callback"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<opaque>",
  "token_type": "bearer",
  "pending_consent": false,
  "pending_clauses": [],
  "kc_id_token": "<keycloak_id_token>"
}
```

Rate-limited to **20 requests/minute** per IP.

---

### `POST /auth/refresh`
Rotates the refresh token and issues a new access token. The old refresh token is invalidated immediately (token rotation).

**Request:**
```json
{ "refresh_token": "<current_refresh_token>" }
```

**Response (`200 OK`):**
```json
{
  "access_token": "<new_jwt>",
  "refresh_token": "<new_opaque>",
  "token_type": "bearer"
}
```

Errors:
- `401 invalid_or_expired_refresh_token` — token not found or already consumed
- `403 inactive_user` — user was deactivated after the session was created

---

### `POST /auth/logout`
Invalidates the current session and calls Keycloak's Admin API to also revoke all Keycloak-side sessions for the user.

**Response:** `204 No Content`

The backend sets `TB_SESSION.INVALIDATED_AT = now()` for the current session, then best-effort calls Keycloak Admin API (`delete_user_sessions`). If the Keycloak call fails, it is silently swallowed — the local session is still invalidated.

---

### `GET /auth/sessions`
Lists all non-deleted sessions for the authenticated user — both active and previously invalidated.

**Response (`200 OK`):**
```json
[
  {
    "session_uuid": "...",
    "created_at": "2026-05-10T14:00:00Z",
    "source_ip": "192.168.x.x",
    "user_agent": "Mozilla/5.0 ...",
    "expires_at": "2026-06-10T14:00:00Z"
  }
]
```

---

### `DELETE /auth/sessions/{session_uuid}`
Revokes a specific session that belongs to the authenticated user. Cannot be used to revoke the **current** session (returns `400 cannot_revoke_current_session`).

Returns `204 No Content` on success, `404 session_not_found` if the session does not exist or belongs to another user.

---

## Consent Gate

Routes protected by `get_current_user` (the standard dependency) enforce both token validity **and** consent. If the user has pending mandatory clauses (`V_PENDING_CONSENT` returns rows), the request is rejected with `403 consent_required`.

Routes protected by `get_current_user_no_consent_check` enforce token validity only. This is used for:
- `POST /auth/logout`
- `GET /auth/me/export`
- `GET /auth/sessions`
- `DELETE /auth/sessions/{uuid}`

This ensures users with pending consent can still sign out or access their own data.

---

## LGPD: Session Data Export

Session records are included in the LGPD data export (`GET /auth/me/export`). The export contains all sessions (including terminated ones) with: `session_id`, `source_ip`, `user_agent`, `created_at`, `updated_at`, `expires_at`, `invalidated_at`.

---

## Related Documents

| Document | Relationship |
|:---|:---|
| [AUTH_ARCHITECTURE.md](AUTH_ARCHITECTURE.md) | OAuth 2.0 + PKCE flow and token validation |
| [LGPD.md](LGPD.md) | Compliance context for session data storage |
| [RELATIONAL_DATABASE.md](RELATIONAL_DATABASE.md) | `TB_SESSION` table definition |

---

*Last updated: 05/31/2026*
