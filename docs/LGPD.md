# 📋 LGPD Compliance Documentation

## 👁️ Overview

This document describes how the database was designed to comply with Brazil's General Data Protection Law — Lei Geral de Proteção de Dados (LGPD), Federal Law 13.709/2018.

## ✅ Applicable Principles (Art. 6, LGPD)

| Principle | How It Was Implemented |
|---|---|
| **Purpose** | Data is collected exclusively for authentication and access control |
| **Adequacy** | Only fields strictly necessary for each function were modeled |
| **Necessity** | No unnecessary personal data fields — email stored as hash + encrypted value |
| **Free access** | RLS policies ensure each user can only access their own data |
| **Data quality** | `UPDATED_AT` triggers track all changes with timestamps |
| **Transparency** | Policy versions and clauses are stored with full content |
| **Security** | Encryption at rest and in transit, append-only logs, RLS, roles |
| **Prevention** | Synthetic data in dev/homolog — no real data outside production |
| **Non-discrimination** | Profiles and permissions are role-based, not individual |
| **Accountability** | All actions are logged in `TB_LOG` with actor, action, result and timestamp |

## 🤝 Consent Management (Art. 7 and Art. 8, LGPD)

Consent is managed at the clause level — each user can accept or revoke individual clauses independently.

- `TB_POLICY_VERSION` stores the full immutable text of each policy version
- `TB_POLICY_CLAUSE` stores individual clauses with a `MANDATORY` flag
- `TB_CONSENT_LOG` records every consent event as an immutable append-only entry

The complete consent history is preserved forever — it is never deleted or updated. This allows proving at any point in time what the user accepted and when.

## 👤 Data Subject Rights (Art. 18, LGPD)

| Right | Implementation |
|---|---|
| **Access** | RLS ensures users can only read their own data |
| **Correction** | UPDATE is allowed on `TB_USER` for controlled fields used by the user CRUD |
| **Anonymization / Deletion** | Soft delete via `DELETED_AT` in the implemented user CRUD |
| **Portability** | Data can be exported from the application layer |
| **Revocation of consent** | New REVOCATION record inserted in `TB_CONSENT_LOG` |
| **Information** | Policy versions and clauses are stored and versioned |

## Data Protection Officer Contact (Art. 41, §1)

ZEUS discloses the Data Protection Officer (Encarregado pelo Tratamento de Dados Pessoais) contact channel required by LGPD Art. 41.

The disclosed information is:

- DPO identification: `Encarregado pelo Tratamento de Dados Pessoais`
- Contact email: `dpo@tecsys.com.br`
- Response commitment: up to 15 business days, following LGPD Art. 18, §4

The purpose of this contact channel is to allow data subjects to exercise LGPD Art. 18 rights, including access, correction, deletion, portability, consent revocation, and requests for information about personal data processing.

### 🗑️ Right to Erasure — How It Works

Physical deletion is never performed on user data. In the user CRUD currently implemented in the backend, the delete operation is logical only. When a user is removed from the active dataset:

1. `DELETED_AT` is populated with the current timestamp
2. The user record is excluded from standard list and detail queries
3. The user UUID is preserved for referential integrity in audit logs and foreign keys
4. The profile history remains intact for operational traceability

The current CRUD does not overwrite personal fields with anonymized placeholders at delete time. That can be added later as a separate data-masking routine if required by policy.

## 👥 User CRUD and LGPD Alignment

The implemented user flow contributes to LGPD compliance in the following ways:

- **Data minimization**: user creation stores only username, email, password hash, encrypted email, and profile association.
- **Purpose limitation**: the data is used for authentication, access control, and user administration only.
- **Security**: email is stored as hash plus encrypted value, and passwords are hashed before persistence.
- **Access control**: user records are tied to profiles, which support role-based permissions.
- **Traceability**: create, update, activation toggle, and logical delete operations preserve timestamps and database history.
- **Transparency**: API responses and validation errors are localized for Brazilian Portuguese users.

### 🎯 User CRUD Scope Covered by LGPD Controls

| Operation | LGPD impact |
|---|---|
| `POST /users` | Creates a user with the minimum necessary personal data and secure storage of e-mail/password |
| `GET /users` and `GET /users/{user_uuid}` | Exposes only operational fields needed by the frontend |
| `PATCH /users/{user_uuid}` | Allows controlled correction of username and profile association |
| `PATCH /users/{user_uuid}/active` | Supports account activation/inactivation without exposing sensitive data |
| `DELETE /users/{user_uuid}` | Performs logical deletion through `DELETED_AT` |

## 🌍 Environment Separation

| Environment | Data | Access |
|---|---|---|
| **Production** | Real personal data | Restricted, MFA required |
| **Development** | Synthetic fictional data only | Development team |

Real data is never used outside production. The `V006__synthetic_seed.sql` migration populates the development environment with entirely fictional data generated manually, ensuring no data subject is exposed during development or testing.

## 🔒 Sensitive Fields and Protection Strategy

| Field | Table | Protection |
|---|---|---|
| `EMAIL_ENC` | TB_USER | Application-layer encryption used to protect the original e-mail value |
| `EMAIL_HASH` | TB_USER |  Deterministic SHA-256 hash with fixed salt from `EMAIL_HASH_SALT`, used for lookup without exposing or decrypting the email |
| `PASSWORD_HASH` | TB_USER | Bcrypt hash — never stored in plain text |
| `SOURCE_IP` | TB_LOG, TB_SESSION, TB_AUTH_ATTEMPT, TB_CONSENT_LOG | Masked — only first 3 octets stored |
| `DETAILS` | TB_LOG | Encrypted JSONB |
| `TOKEN_HASH` | TB_PASSWORD_RESET | SHA-256 hash of the password reset token — the raw token is never stored |

Password reset tokens are not stored in plain text. The database stores only `TOKEN_HASH`, which contains the SHA-256 hash of the issued token. This reduces exposure in case of database access while preserving the ability to validate single-use reset requests.

## 📊 Audit Trail

Every action performed on sensitive data is recorded in `TB_LOG` with:
- Who performed the action (`USER_ID`)
- What was done (`ACTION`)
- Which record was affected (`ENTITY` + `ENTITY_ID`)
- From where (`SOURCE_IP`, `USER_AGENT`)
- The outcome (`RESULT`)
- When it happened (`CREATED_AT`)

The log table is append-only — UPDATE and DELETE are blocked at the database level via trigger, ensuring the audit trail cannot be tampered with.

## 🔍 Application-Layer Logging

All HTTP requests and business operations are recorded by a structured logging system built on `structlog` and `TimedRotatingFileHandler`.

Logs are written in JSON format to `logs/app.log`, rotated daily, and compressed to `.gz` after rotation with 30 days of retention.

The logging system enforces LGPD compliance at the application layer:
- No personal data is ever written to log files — only UUIDs, status codes, durations, and event constants
- Prohibited fields (`email`, `cpf`, `password`, `name`, `nome`, `senha`) are validated by `scripts/validate_log_privacy.py`
- Each request is assigned a unique `request_id` for end-to-end traceability without exposing user identity

Full documentation: [`docs/LOGGING.md`](docs/LOGGING.md)

## Dual-Database Separation as Structural LGPD Measure

ZEUS uses a dual-database architecture as a compliance control, not only as a technical storage choice:

- **PostgreSQL** stores personal and sensitive application data: users, credentials, sessions, password reset tokens, consent records, policy acceptance history, and sensitive audit logs.
- **MongoDB** stores public ANEEL/BDGD analytical data: distributor/regulatory indicators, geospatial infrastructure data, TAM/SAM outputs, predictions, and ETL metadata.

This separation supports purpose limitation, minimization, and security under LGPD by keeping analytical processing structurally separated from personal data processing. MongoDB must not store `USER_UUID`, email, CPF, name, session token, consent reference, or any other natural-person identifier from the ZEUS user domain.

The full ROPA entry, breach isolation analysis, professor validation argument, and control checklist are documented in [`docs/LGPD_DATA_SEPARATION.md`](LGPD_DATA_SEPARATION.md).

## LGPD ANONYMIZATION, LOGICAL EXCLUSION AND DATA RETENTION

### ANONYMIZATION & LOGICAL EXCLUSION
For anonymization and logical exclusion, we need only to alter/delete tables that contains the user id as a FK.
For the TB_CONSENT_LOG table, we keep the user id column but remove its reference to TB_USER
For other tables such as TB_PASSWORD_RESET, validate if they are indeed required and being used, if not we can safely drop those tables. Otherwise we just remove the user id reference to its TB_USER table

That way we ensure there is no referencial integrity to keep between the tables while also recording the user id on these tables.

Next we only need to change the 'delete users' feature to fully delete its equivalent row on TB_USER

### DATA RETENTION
To ensure data retention, we need to perform the following steps:

- Create a new database (ie USER_RETENTION_DB)
- On the created database, create a new table (ie DELETED_USERS) with two columns, one being an UUID serving as a PK, and another one is the id of the deleted user that was stored in TB_USER
- Change the 'delete users' feature so before it deletes anything, it creates a new row on DELETED_USERS with the id of the user being deleted
- Create a python function that calls pg_dump.exe via shell to dump the database containing TB_USERS
- Create a python function that modifies the .sql file created by pg_dump.exe, removing the insertion of users inside the DELETED_USERS table
- Create a python function that calls pg_restore.exe via shell to restore the database using the modified .sql file

References:
- https://www.geeksforgeeks.org/postgresql/how-to-dump-and-restore-postgresql-database/
- https://www.geeksforgeeks.org/postgresql/postgresql-restore-database/

---

*Last updated: 05/19/2026*
