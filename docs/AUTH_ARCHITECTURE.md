# 🔐 Authentication and Authorization Architecture

## 👁️ Overview

This document describes the authentication and authorization model adopted in the project, based on the **OAuth 2.0** protocol using the **Authorization Code Flow with PKCE**, with **Keycloak** as the centralized identity server.

Keycloak is responsible for authenticating the user and issuing tokens. The backend (FastAPI) validates these tokens locally and enforces authorization based on access profile.

---

## 🛠️ Technologies Involved

| Technology | Version | Purpose |
|:---|:---:|:---|
| **Keycloak** | latest | Identity and authorization server (IdP) |
| **OAuth 2.0 + PKCE** | RFC 6749 + RFC 7636 | Authorization protocol with SPA protection |
| **JWT (JSON Web Token)** | RFC 7519 | Token format issued by Keycloak |
| **JWKS** | RFC 7517 | Public keys for local JWT validation |
| **FastAPI** | 0.135.2 | Backend — validates the token and enforces profile-based authorization |
| **Docker Compose** | — | Keycloak runs alongside the backend and frontend |

---

## 🔄 Authentication Flow (Authorization Code Flow with PKCE)

### Diagram

```
User             Frontend             Keycloak          Backend (FastAPI)
   │                 │                    │                     │
   │  Clicks Login   │                    │                     │
   │────────────────>│                    │                     │
   │                 │                    │                     │
   │                 │ Generates          │                     │
   │                 │ code_verifier      │                     │
   │                 │ code_challenge     │                     │
   │                 │ (SHA-256)          │                     │
   │                 │                    │                     │
   │                 │ Sends redirect_uri │                     │
   │                 │ + code_challenge   │                     │
   │                 │───────────────────>│                     │
   │                 │                    │                     │
   │   Redirects to Keycloak login page   │                     │
   │<─────────────────────────────────────│                     │
   │                 │                    │                     │
   │ Enters login    │                    │                     │
   │ and password    │                    │                     │
   │─────────────────────────────────────>│                     │
   │                 │                    │                     │
   │                 │                    │ Validates credentials│
   │                 │                    │                     │
   │                 │   authorization_code                     │
   │                 │<───────────────────│                     │
   │                 │                    │                     │
   │                 │ Sends code +       │                     │
   │                 │ code_verifier      │                     │
   │                 │───────────────────>│                     │
   │                 │                    │                     │
   │                 │                    │ Validates PKCE      │
   │                 │                    │ (hash of verifier   │
   │                 │                    │  == challenge)      │
   │                 │                    │                     │
   │                 │  access_token      │                     │
   │                 │  refresh_token     │                     │
   │                 │<───────────────────│                     │
   │                 │                    │                     │
   │                 │ Authorization:     │                     │
   │                 │ Bearer <token>     │                     │
   │                 │─────────────────────────────────────────>│
   │                 │                    │    Validates token  │
   │                 │                    │    via JWKS         │
   │                 │                    │    Checks profile   │
   │                 │<─────────────────────────────────────────│
   │                 │    API Response    │                     │
```

---

### Step by Step

#### 1. Flow Initiation (Frontend)
- The user clicks the login button in the application
- The frontend generates two values: the `code_verifier` (random string, local secret) and the `code_challenge` (SHA-256 hash of the `code_verifier`)
- The `code_verifier` is temporarily stored on the client side (memory or `sessionStorage`)

#### 2. Redirect to Keycloak
- The frontend sends to Keycloak:
  - `response_type=code`
  - `redirect_uri` (application return URL)
  - `code_challenge` and `code_challenge_method=S256`
- Keycloak responds by redirecting the user to its own login page

#### 3. Authentication by Keycloak
- The user enters their credentials on the Keycloak login screen
- Keycloak validates the credentials and, on success, returns a temporary `authorization_code` to the configured `redirect_uri`

#### 4. Code-for-Token Exchange (Frontend → Keycloak)
- The frontend sends to Keycloak:
  - `grant_type=authorization_code`
  - `code` (the temporary code received)
  - `code_verifier` (the original secret generated in step 1)
- Keycloak validates that the hash of the `code_verifier` matches the `code_challenge` sent earlier **(PKCE protection)**
- On success, Keycloak issues and returns:
  - `access_token` — short-lived JWT used in API requests
  - `refresh_token` — long-lived JWT for renewing the `access_token` without a new login

#### 5. Accessing Protected Routes (Frontend → Backend)
- The frontend includes the `access_token` in the header of every request:
  ```
  Authorization: Bearer <access_token>
  ```
- The backend validates the token locally and, after validation, enforces authorization based on the user's profile

---

## 🔑 Token Validation in the Backend

The backend **does not call Keycloak on every request**. Validation is done locally using Keycloak's public key:

```
Backend Startup
        │
        ▼
Downloads Keycloak's public keys
Endpoint: /realms/{realm}/protocol/openid-connect/certs
        │
        ▼
Stores in cache (JWKS)
        │
        ▼
On every authenticated request:
  1. Verifies JWT signature using the cached public key
  2. Validates mandatory claims:
     - exp  → token has not expired
     - iss  → issuer matches the expected Keycloak instance
     - aud  → audience matches the configured client
  3. Extracts the user profile from the token
  4. Enforces profile-based authorization
```

> **Why local validation?**
> Eliminates extra latency and removes Keycloak as a point of failure on every request path. The JWKS is refreshed periodically in the background — Keycloak is only consulted on startup or during key rotation.

---

## 👥 Profile-Based Authorization

Access profiles determine which routes and resources each user can use:

| Profile | Access Level |
|:---|:---|
| **ADMIN** | Full access — user management, LGPD, terms, uploads, and all analytics |
| **MANAGER** | Operational access — system operation, uploads and analytics. No access to users, terms, or LGPD routes |
| **ANALYST** | Read-only access — dashboards, heatmap, network structure, and own data. No administrative management or upload |

Profiles are managed in the `TB_PROFILE` table in PostgreSQL and mirrored as realm roles in Keycloak. The JWT token carries the role directly via `realm_access.roles`, allowing the backend to enforce authorization without an extra database query.

---

## 🐳 Keycloak in Docker Compose

Keycloak runs as an additional service in the project's `docker-compose.yml`, alongside the backend and frontend:

```yaml
keycloak-postgres:
  image: postgres:15-alpine
  env_file:
    - envs/.env.keycloak-postgres.${APP_ENV:-dev}
  volumes:
    - keycloak_postgres_data:/var/lib/postgresql/data
  networks:
    - keycloak_network

keycloak:
  image: quay.io/keycloak/keycloak:26.2
  command: start-dev --import-realm
  env_file:
    - envs/.env.keycloak.${APP_ENV:-dev}
  ports:
    - "8180:8080"
  volumes:
    - ./keycloak:/opt/keycloak/data/import
  networks:
    - app_network
    - keycloak_network
  depends_on:
    keycloak-postgres:
      condition: service_healthy
```

Environment files: `envs/.env.keycloak.dev` (admin credentials + `KC_DB_*`) and `envs/.env.keycloak-postgres.dev` (dedicated PostgreSQL credentials).

> **Production note:** replace `start-dev` with `start` and configure `KC_HOSTNAME`, TLS certificate, and rotate all credentials.

---

## 🔒 Relation to LGPD

Adopting Keycloak reinforces the LGPD compliance principles documented in [LGPD.md](LGPD.md):

| Principle (Art. 6 LGPD) | How Keycloak contributes |
|:---|:---|
| **Security** | Credentials managed by Keycloak; the backend never receives or stores passwords |
| **Prevention** | Brute-force protection configurable in Keycloak (lockout by attempt count) |
| **Accountability** | Keycloak maintains an event log for authentication actions (login, logout, failures) |
| **Necessity** | The `access_token` carries only the claims needed for authorization (profile, `sub`) |

---

## 📚 Related Documents

| Document | Relationship |
|:---|:---|
| [LGPD.md](LGPD.md) | Compliance with Brazil's General Data Protection Law |
| [BACKEND_INFRASTRUCTURE.md](BACKEND_INFRASTRUCTURE.md) | FastAPI backend architecture where the token is validated |
| [RELATIONAL-DATABASE.md](RELATIONAL-DATABASE.md) | Data model — `TB_USER`, `TB_PROFILE`, `TB_SESSION` |
| [INSTALLATION_MANUAL.md](INSTALLATION_MANUAL.md) | Docker Compose installation guide (includes Keycloak service) |
| [LGPD_DATA_SEPARATION.md](LGPD_DATA_SEPARATION.md) | Sensitive data separation and Keycloak database |

---

**Last updated:** May 2026
**Status:** ✅ Flow validated
