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

### Append-Only Consent History

User consent is recorded through an append-only event model in `TB_CONSENT_LOG`. The system does not store consent as a single mutable flag. Instead, every acceptance or revocation creates a new event, preserving the full consent timeline.

This model supports the controller’s burden of proof under LGPD Art. 8, §5, and the accountability principle under Art. 6, X, because the system can demonstrate when consent was given, which clause was accepted, which policy version applied, and whether the user later revoked or re-accepted consent.

`TB_CONSENT_LOG` is a shared table for all users. Each record is linked to a specific user through `USER_ID`, and to the applicable legal content through `CLAUSE_ID` and `POLICY_VERSION_ID`.

The current consent state is derived from the latest event for each `USER_ID + CLAUSE_ID` combination:

```sql
SELECT
    ACTION,
    POLICY_VERSION_ID,
    CREATED_AT
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id
  AND CLAUSE_ID = :clause_id
ORDER BY CREATED_AT DESC, LOG_UUID DESC
LIMIT 1;
```

If the latest action is `CONSENT_ACCEPTED`, the clause is considered accepted. If the latest action is `CONSENT_REVOKED`, or if no event exists, the clause is considered pending.

The system does not need to list all users to find a specific person’s consent history. It retrieves the required records directly by filtering `TB_CONSENT_LOG` by `USER_ID`.

### Pending Consent Enforcement

The operational consent state is derived through `V_PENDING_CONSENT`, which identifies mandatory clauses that still require user acceptance.

This pending consent logic is used by the authentication flow, authorization dependencies and middleware. If a user has unresolved mandatory consent, protected routes may be blocked until the required clauses are accepted.

Thus:

- `TB_CONSENT_LOG` stores the immutable evidence history;
- `TB_POLICY_VERSION` and `TB_POLICY_CLAUSE` store the legal and textual context;
- `V_PENDING_CONSENT` derives the current pending-consent state;
- authentication and middleware enforce access restrictions when consent is pending.

### Tamper Resistance and Retention

Consent records are protected as append-only evidence. Existing consent events must not be updated or deleted. Revocation or re-acceptance must be represented by inserting a new event.

This preserves the evidentiary sequence required for LGPD compliance and legal defense.

After anonymization, the consent history may be preserved as non-identifying institutional evidence, provided that the remaining `USER_ID` can no longer identify a natural person. This supports LGPD Art. 12 regarding anonymized data and Art. 16 regarding justified post-termination retention for legal compliance and defense of rights.

### Consent Proof and Evidence Hash

Consent is recorded as an append-only event history in `TB_CONSENT_LOG`. The system does not use a mutable consent flag. Each acceptance or revocation creates a new event linked to `USER_ID`, `CLAUSE_ID`, `POLICY_VERSION_ID`, `ACTION` and `CREATED_AT`.

This model supports LGPD Art. 8 because it preserves evidence that consent was free, informed, specific and unambiguous. It also supports the controller’s burden of proof under Art. 8, §5 and the accountability principle under Art. 6, X.

To strengthen the proof model, each consent event should also store a deterministic `CONSENT_HASH`. This hash is calculated from the core evidentiary fields of the row:

```text
USER_ID + CLAUSE_ID + POLICY_VERSION_ID + ACTION + CREATED_AT
```

The hash is stored alongside the consent event and works as an additional integrity check. If any of these fields are changed after insertion, recalculating the hash will expose the mismatch.

The consent hash complements the existing append-only protection. The append-only trigger prevents `UPDATE` and `DELETE` operations on `TB_CONSENT_LOG`; the hash provides a verifiable seal over the main values of the event.

A simplified verification query is:

```sql
SELECT
    LOG_UUID,
    CONSENT_HASH,
    fn_compute_consent_log_hash(
        USER_ID,
        CLAUSE_ID,
        POLICY_VERSION_ID,
        ACTION,
        CREATED_AT
    ) AS RECALCULATED_HASH,
    CONSENT_HASH = fn_compute_consent_log_hash(
        USER_ID,
        CLAUSE_ID,
        POLICY_VERSION_ID,
        ACTION,
        CREATED_AT
    ) AS HASH_VALID
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id;
```

The complete evidence chain is reconstructed by joining:

```text
TB_CONSENT_LOG
TB_POLICY_CLAUSE
TB_POLICY_VERSION
```

This allows the system to prove who consented, which clause was accepted or revoked, which policy version applied, when the event occurred and whether the stored evidence remains consistent.

`TB_CONSENT_LOG` is a shared table for all users. The consent history of a specific person is retrieved directly through `USER_ID`; the system does not need to list all users to find the required individual.

The consent proof model is therefore based on:

- clause-level consent records;
- policy version traceability;
- append-only storage;
- deterministic evidence hash;
- pending-consent enforcement through `V_PENDING_CONSENT`;
- post-anonymization preservation when legally justified under LGPD Art. 12 and Art. 16.


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
