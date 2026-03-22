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
| **Correction** | UPDATE is allowed on `TB_USER` via `app_role` |
| **Anonymization / Deletion** | Soft delete via `DELETED_AT` + data anonymization script |
| **Portability** | Data can be exported from the application layer |
| **Revocation of consent** | New REVOCATION record inserted in `TB_CONSENT_LOG` |
| **Information** | Policy versions and clauses are stored and versioned |

### Right to Erasure — How It Works

Physical deletion is never performed on user data. When a user requests erasure:

1. Personal data fields are overwritten with anonymized values
2. `DELETED_AT` is populated with the current timestamp
3. `ACTIVE` is set to `false`
4. The user UUID is preserved for referential integrity in audit logs
5. Audit logs referencing the user are preserved but dissociated from the data subject

## Environment Separation

| Environment | Data | Access |
|---|---|---|
| **Production** | Real personal data | Restricted, MFA required |
| **Development** | Synthetic fictional data only | Development team |

Real data is never used outside production. The `V006__synthetic_seed.sql` migration populates the development environment with entirely fictional data generated manually, ensuring no data subject is exposed during development or testing.

## Sensitive Fields and Protection Strategy

| Field | Table | Protection |
|---|---|---|
| `EMAIL_ENC` | TB_USER | AES-256 encryption at application layer |
| `EMAIL_HASH` | TB_USER | One-way hash for lookup without exposing value |
| `PASSWORD_HASH` | TB_USER | Argon2id — never stored in plain text |
| `SOURCE_IP` | TB_LOG, TB_SESSION, TB_AUTH_ATTEMPT, TB_CONSENT_LOG | Masked — only first 3 octets stored |
| `DETAILS` | TB_LOG | Encrypted JSONB |

## Audit Trail

Every action performed on sensitive data is recorded in `TB_LOG` with:
- Who performed the action (`USER_ID`)
- What was done (`ACTION`)
- Which record was affected (`ENTITY` + `ENTITY_ID`)
- From where (`SOURCE_IP`, `USER_AGENT`)
- The outcome (`RESULT`)
- When it happened (`CREATED_AT`)

The log table is append-only — UPDATE and DELETE are blocked at the database level via trigger, ensuring the audit trail cannot be tampered with.