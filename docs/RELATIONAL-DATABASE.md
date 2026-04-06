# Relational Database Documentation

## Overview

This database was designed to store sensitive user data in compliance with Brazil's General Data Protection Law (LGPD - Lei 13.709/2018). It uses PostgreSQL 15 with strict access controls, encryption strategies, and append-only audit tables.

## Technology Stack

- **Database**: PostgreSQL 15
- **Versioning**: Flyway 9
- **Containerization**: Docker + Docker Compose

## Migration Execution Order

Flyway executes migrations in sequential order. The following order must be respected:

| File | Description |
|---|---|
| `V001__create_tables.sql` | Creates all tables with constraints |
| `V002__create_roles.sql` | Creates database roles and grants permissions |
| `V003__create_triggers.sql` | Creates triggers for updated_at and append-only protection |
| `V004__security.sql` | Enables RLS and revokes public access |
| `V005__base_seed.sql` | Inserts minimum required data for all environments |
| `V006__synthetic_seed.sql` | Inserts fictional data for dev environment only |
| `V007__rls_policies.sql` | Creates Row Level Security policies |

## Table Descriptions

### `TB_PROFILE`
Stores user profiles for role-based access control (RBAC). Each user is assigned one profile that defines their permissions within the system.

| Column | Type | Rules |
|---|---|---|
| `PROFILE_UUID` | UUID | PK, auto-generated |
| `PROFILE_NAME` | VARCHAR(255) | NOT NULL, UNIQUE |
| `PERMISSIONS` | JSONB | NOT NULL |
| `DESCRIPTION` | TEXT | nullable |
| `CREATED_AT` | TIMESTAMPTZ | DEFAULT NOW() |
| `UPDATED_AT` | TIMESTAMPTZ | DEFAULT NOW(), updated by trigger |
| `DELETED_AT` | TIMESTAMPTZ | nullable, soft delete |

---

### `TB_USER`
Stores system users. Email is stored in two fields — one hashed for lookup, one encrypted for storage — following LGPD data minimization principles.

| Column | Type | Rules |
|---|---|---|
| `USER_UUID` | UUID | PK, auto-generated |
| `USERNAME` | VARCHAR(255) | NOT NULL, UNIQUE |
| `EMAIL_HASH` | VARCHAR(255) | NOT NULL, UNIQUE — used for lookup |
| `EMAIL_ENC` | VARCHAR(255) | NOT NULL — encrypted value |
| `PASSWORD_HASH` | VARCHAR(255) | NOT NULL — Argon2id |
| `PROFILE_ID` | UUID | FK → TB_PROFILE |
| `ACTIVE` | BOOLEAN | NOT NULL, DEFAULT true |
| `CREATED_AT` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `UPDATED_AT` | TIMESTAMPTZ | NOT NULL, updated by trigger |
| `DELETED_AT` | TIMESTAMPTZ | nullable, soft delete |

---

### `TB_SESSION`
Tracks active user sessions individually. Allows forced logout, active device listing, and automatic expiration — rights the data subject can exercise under LGPD.

| Column | Type | Rules |
|---|---|---|
| `SESSION_UUID` | UUID | PK, auto-generated |
| `USER_ID` | UUID | FK → TB_USER, NOT NULL |
| `SOURCE_IP` | VARCHAR(255) | NOT NULL, masked |
| `USER_AGENT` | VARCHAR(255) | NOT NULL |
| `EXPIRES_AT` | TIMESTAMPTZ | NOT NULL |
| `INVALIDATED_AT` | TIMESTAMPTZ | nullable |
| `CREATED_AT` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `UPDATED_AT` | TIMESTAMPTZ | NOT NULL, updated by trigger |
| `DELETED_AT` | TIMESTAMPTZ | nullable |

---

### `TB_AUTH_ATTEMPT`
Records every authentication attempt. Does not have a FK to `TB_USER` because the attempted email may not exist in the system. Feeds brute force detection logic.

| Column | Type | Rules |
|---|---|---|
| `ATTEMPT_UUID` | UUID | PK, auto-generated |
| `EMAIL_HASH` | VARCHAR(255) | NOT NULL — no UNIQUE, multiple attempts allowed |
| `SOURCE_IP` | VARCHAR(255) | NOT NULL, masked |
| `SUCCESS` | BOOLEAN | NOT NULL |
| `BLOCKED` | BOOLEAN | NOT NULL, DEFAULT false |
| `ATTEMPTED_AT` | TIMESTAMPTZ | DEFAULT NOW() |

---

### `TB_LOG`
Records all relevant system actions for accountability. This table is **append-only** — UPDATE and DELETE are blocked at the database level via trigger.

| Column | Type | Rules |
|---|---|---|
| `LOG_UUID` | UUID | PK, auto-generated |
| `USER_ID` | UUID | FK → TB_USER, nullable (system actions) |
| `ACTION` | VARCHAR(255) | NOT NULL, CHECK IN ('LOGIN', 'LOGOUT', 'READ', 'UPDATE', 'DELETE', 'AUTH_FAILURE') |
| `ENTITY` | VARCHAR(255) | NOT NULL |
| `ENTITY_ID` | VARCHAR(255) | NOT NULL |
| `SOURCE_IP` | VARCHAR(255) | NOT NULL, masked |
| `USER_AGENT` | VARCHAR(255) | NOT NULL |
| `RESULT` | VARCHAR(255) | NOT NULL, CHECK IN ('SUCCESS', 'FAILURE') |
| `DETAILS` | JSONB | nullable, encrypted |
| `CREATED_AT` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

---

### `TB_POLICY_VERSION`
Stores the complete immutable text of every version of privacy policies and terms of use. Required to prove, in case of audit, the exact text the user accepted.

| Column | Type | Rules |
|---|---|---|
| `VERSION_UUID` | UUID | PK, auto-generated |
| `VERSION` | VARCHAR(20) | NOT NULL, UNIQUE |
| `POLICY_TYPE` | VARCHAR(255) | NOT NULL, CHECK IN ('PRIVACY_POLICY', 'TERMS_OF_USE') |
| `CONTENT` | TEXT | NOT NULL |
| `EFFECTIVE_FROM` | TIMESTAMPTZ | NOT NULL |
| `CREATED_AT` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| `UPDATED_AT` | TIMESTAMPTZ | DEFAULT NOW(), updated by trigger |
| `DELETED_AT` | TIMESTAMPTZ | nullable |

---

### `TB_POLICY_CLAUSE`
Represents individual clauses that the user can accept or revoke independently. The `MANDATORY` field indicates clauses that cannot be revoked without closing the account.

| Column | Type | Rules |
|---|---|---|
| `CLAUSE_UUID` | UUID | PK, auto-generated |
| `POLICY_VERSION_ID` | UUID | FK → TB_POLICY_VERSION, NOT NULL |
| `CODE` | VARCHAR(50) | NOT NULL, UNIQUE |
| `TITLE` | VARCHAR(255) | NOT NULL |
| `DESCRIPTION` | TEXT | nullable |
| `MANDATORY` | BOOLEAN | NOT NULL |
| `DISPLAY_ORDER` | INT | NOT NULL |
| `CREATED_AT` | TIMESTAMPTZ | DEFAULT NOW() |
| `UPDATED_AT` | TIMESTAMPTZ | DEFAULT NOW(), updated by trigger |
| `DELETED_AT` | TIMESTAMPTZ | nullable |

---

### `TB_CONSENT_LOG`
Records every consent event per clause per user. Both CONSENT and REVOCATION are inserted as new records — never updated. This table is **append-only**.

To determine the current state of a clause for a user, always query the most recent record:
```sql
SELECT DISTINCT ON (CLAUSE_ID)
    CLAUSE_ID,
    ACTION,
    REGISTERED_AT
FROM TB_CONSENT_LOG
WHERE USER_ID = $1
ORDER BY CLAUSE_ID, CREATED_AT DESC;
```

| Column | Type | Rules |
|---|---|---|
| `LOG_UUID` | UUID | PK, auto-generated |
| `USER_ID` | UUID | FK → TB_USER, NOT NULL |
| `CLAUSE_ID` | UUID | FK → TB_POLICY_CLAUSE, NOT NULL |
| `ACTION` | VARCHAR(255) | NOT NULL, CHECK IN ('CONSENT', 'REVOCATION') |
| `SOURCE_IP` | VARCHAR(255) | NOT NULL, masked |
| `CHANNEL` | VARCHAR(255) | NOT NULL — WEB, MOBILE, API |
| `CREATED_AT` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

---

## Security Controls

### Triggers
- `update_timestamp()` — automatically updates `UPDATED_AT` on every UPDATE
- `fn_protect_append_only()` — blocks UPDATE and DELETE on `TB_LOG` and `TB_CONSENT_LOG`

### Roles
| Role | Permissions |
|---|---|
| `app_role` | SELECT, INSERT, UPDATE on operational tables. INSERT only on log tables |
| `log_role` | INSERT only on `TB_LOG` and `TB_CONSENT_LOG` |
| `dba_role` | ALL PRIVILEGES — for administration only, never used by the application |

### Row Level Security
RLS is enabled on `TB_USER`, `TB_SESSION`, and `TB_CONSENT_LOG`. Each user can only access their own records. The application must set the session variable before any query:
```sql
SET app.current_user_id = 'user-uuid-here';
```

### Soft Delete
No physical DELETE is performed on user data. The `DELETED_AT` field is populated instead. This supports the LGPD right to erasure while maintaining referential integrity for audit purposes.