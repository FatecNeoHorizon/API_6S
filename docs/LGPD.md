# LGPD Compliance Documentation

## Overview

This document describes how the database was designed to comply with Brazil's General Data Protection Law — Lei Geral de Proteção de Dados (LGPD), Federal Law 13.709/2018.

## Applicable Principles (Art. 6, LGPD)

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

## Consent Management (Art. 7 and Art. 8, LGPD)

Consent is managed at the clause level — each user can accept or revoke individual clauses independently.

- `TB_POLICY_VERSION` stores the full immutable text of each policy version
- `TB_POLICY_CLAUSE` stores individual clauses with a `MANDATORY` flag
- `TB_CONSENT_LOG` records every consent event as an immutable append-only entry

The complete consent history is preserved forever — it is never deleted or updated. This allows proving at any point in time what the user accepted and when.

## Data Subject Rights (Art. 18, LGPD)

| Right | Implementation |
|---|---|
| **Access** | RLS ensures users can only read their own data |
| **Correction** | UPDATE is allowed on `TB_USER` for controlled fields used by the user CRUD |
| **Anonymization / Deletion** | Soft delete via `DELETED_AT` in the implemented user CRUD |
| **Portability** | Data can be exported from the application layer |
| **Revocation of consent** | New REVOCATION record inserted in `TB_CONSENT_LOG` |
| **Information** | Policy versions and clauses are stored and versioned |

### Right to Erasure — How It Works

Physical deletion is never performed on user data. In the user CRUD currently implemented in the backend, the delete operation is logical only. When a user is removed from the active dataset:

1. `DELETED_AT` is populated with the current timestamp
2. The user record is excluded from standard list and detail queries
3. The user UUID is preserved for referential integrity in audit logs and foreign keys
4. The profile history remains intact for operational traceability

The current CRUD does not overwrite personal fields with anonymized placeholders at delete time. That can be added later as a separate data-masking routine if required by policy.

## User CRUD and LGPD Alignment

The implemented user flow contributes to LGPD compliance in the following ways:

- **Data minimization**: user creation stores only username, email, password hash, encrypted email, and profile association.
- **Purpose limitation**: the data is used for authentication, access control, and user administration only.
- **Security**: email is stored as hash plus encrypted value, and passwords are hashed before persistence.
- **Access control**: user records are tied to profiles, which support role-based permissions.
- **Traceability**: create, update, activation toggle, and logical delete operations preserve timestamps and database history.
- **Transparency**: API responses and validation errors are localized for Brazilian Portuguese users.

### User CRUD Scope Covered by LGPD Controls

| Operation | LGPD impact |
|---|---|
| `POST /users` | Creates a user with the minimum necessary personal data and secure storage of e-mail/password |
| `GET /users` and `GET /users/{user_uuid}` | Exposes only operational fields needed by the frontend |
| `PATCH /users/{user_uuid}` | Allows controlled correction of username and profile association |
| `PATCH /users/{user_uuid}/active` | Supports account activation/inactivation without exposing sensitive data |
| `DELETE /users/{user_uuid}` | Performs logical deletion through `DELETED_AT` |

## Environment Separation

| Environment | Data | Access |
|---|---|---|
| **Production** | Real personal data | Restricted, MFA required |
| **Development** | Synthetic fictional data only | Development team |

Real data is never used outside production. The `V006__synthetic_seed.sql` migration populates the development environment with entirely fictional data generated manually, ensuring no data subject is exposed during development or testing.

## Sensitive Fields and Protection Strategy

| Field | Table | Protection |
|---|---|---|
| `EMAIL_ENC` | TB_USER | Application-layer encryption used to protect the original e-mail value |
| `EMAIL_HASH` | TB_USER |  Deterministic SHA-256 hash with fixed salt from `EMAIL_HASH_SALT`, used for lookup without exposing or decrypting the email |
| `PASSWORD_HASH` | TB_USER | Bcrypt hash — never stored in plain text |
| `SOURCE_IP` | TB_LOG, TB_SESSION, TB_AUTH_ATTEMPT, TB_CONSENT_LOG | Masked — only first 3 octets stored |
| `DETAILS` | TB_LOG | Encrypted JSONB |
| `TOKEN_HASH` | TB_PASSWORD_RESET | SHA-256 hash of the password reset token — the raw token is never stored |

Password reset tokens are not stored in plain text. The database stores only `TOKEN_HASH`, which contains the SHA-256 hash of the issued token. This reduces exposure in case of database access while preserving the ability to validate single-use reset requests.

## Audit Trail

Every action performed on sensitive data is recorded in `TB_LOG` with:
- Who performed the action (`USER_ID`)
- What was done (`ACTION`)
- Which record was affected (`ENTITY` + `ENTITY_ID`)
- From where (`SOURCE_IP`, `USER_AGENT`)
- The outcome (`RESULT`)
- When it happened (`CREATED_AT`)

The log table is append-only — UPDATE and DELETE are blocked at the database level via trigger, ensuring the audit trail cannot be tampered with.