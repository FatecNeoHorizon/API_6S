# LGPD Compliance Documentation

## Overview

This document describes how the database was designed to comply with Brazil's General Data Protection Law — Lei Geral de Proteção de Dados (LGPD), Federal Law 13.709/2018.

## Applicable Principles (Art. 6, LGPD)

| Principle | How It Was Implemented |
|---|---|
| **Purpose** | Data is collected exclusively for authentication, consent management, and access control |
| **Adequacy** | Only fields strictly necessary for each function were modeled |
| **Necessity** | No unnecessary personal data fields — email stored as deterministic hash + encrypted value |
| **Free access** | RLS policies ensure each user can only access their own data, while ADMIN users may manage records when operationally required |
| **Data quality** | `UPDATED_AT` triggers track changes on mutable tables |
| **Transparency** | Policy versions and clauses are stored with full content and versioning |
| **Security** | Encryption at rest and in transit, deterministic lookup hash for email, append-only consent evidence, RLS, and database roles |
| **Prevention** | Synthetic data in dev/homolog — no real data outside production |
| **Non-discrimination** | Profiles and permissions are role-based, not individual |
| **Accountability** | Immutable policy and consent records preserve evidence of the rules presented and the user's decisions |

## Consent Management (Art. 7 and Art. 8, LGPD)

Consent is managed at the clause level — each user can accept or revoke individual clauses independently.

- `TB_POLICY_VERSION` stores the full immutable text of each policy version
- `TB_POLICY_CLAUSE` stores individual clauses with a `MANDATORY` flag
- `TB_CONSENT_LOG` records every consent or revocation event as an immutable append-only entry
- `V_PENDING_CONSENT` helps identify pending required or optional clauses based on the most recent consent state

The complete consent history is preserved forever — it is never deleted or updated. This allows proving at any point in time what the user accepted and when.

## Data Subject Rights (Art. 18, LGPD)

| Right | Implementation |
|---|---|
| **Access** | RLS ensures users can only read their own data |
| **Correction** | UPDATE is allowed on mutable records through `app_role` and application rules |
| **Anonymization / Deletion** | Soft delete via `DELETED_AT` plus explicit anonymization tracking in `ANONYMIZED_AT` |
| **Portability** | Data can be exported from the application layer |
| **Revocation of consent** | A new `REVOCATION` record is inserted in `TB_CONSENT_LOG` |
| **Information** | Policy versions and clauses are stored and versioned |

### Right to Erasure — How It Works

Physical deletion is never performed on user data. When a user requests erasure:

1. Personal data fields are overwritten with anonymized values
2. `ANONYMIZED_AT` is populated with the current timestamp
3. `DELETED_AT` is populated with the current timestamp
4. `ACTIVE` is set to `false`
5. The user UUID is preserved for referential integrity in consent history and security records

## EMAIL_HASH Generation Details

The system uses a deterministic SHA-256 hash for email lookup.

- Source fields: user email before encryption
- Salt source: `EMAIL_HASH_SALT` in the backend environment file
- Storage format: 64-character hexadecimal text
- Target columns:
  - `TB_USER.EMAIL_HASH`
  - `TB_AUTH_ATTEMPT.EMAIL_HASH`

This design allows deterministic search and correlation without decrypting `EMAIL_ENC`.

Because the email field is treated as immutable in the relational model, there is no hash update flow for email changes.

## Terms and Consent Immutability

The legal evidence model is intentionally append-only:

- `TB_POLICY_VERSION` is append-only to preserve the exact full text of each published version
- `TB_POLICY_CLAUSE` is append-only to preserve the exact clause structure associated with each version
- `TB_CONSENT_LOG` is append-only to preserve the full history of consent and revocation decisions

This supports auditability, legal proof, and chronological reconstruction of the consent context presented to each data subject.

## Environment Separation

| Environment | Data | Access |
|---|---|---|
| **Production** | Real personal data | Restricted, controlled credentials |
| **Development** | Synthetic fictional data only | Development team |

Real data is never used outside production. The `V006__synthetic_seed.sql` migration populates development with fictional data only and can be disabled in production through the Flyway placeholder configuration.

## Sensitive Fields and Protection Strategy

| Field | Table | Protection |
|---|---|---|
| `EMAIL_ENC` | TB_USER | AES-256 encryption at application layer |
| `EMAIL_HASH` | TB_USER | Deterministic SHA-256 hash with fixed salt from `EMAIL_HASH_SALT`, used for lookup without exposing or decrypting the email |
| `EMAIL_HASH` | TB_AUTH_ATTEMPT | Deterministic SHA-256 hash for correlation of login attempts |
| `PASSWORD_HASH` | TB_USER | Argon2id — never stored in plain text |
| `TOKEN_HASH` | TB_PASSWORD_RESET | SHA-256 hash of the reset token — the raw token is never stored |
| `SOURCE_IP` | TB_SESSION, TB_AUTH_ATTEMPT, TB_CONSENT_LOG | Masked — only the minimum operational format should be stored |

## LGPD Mapping (Table / Field vs. Legal Basis)

| Table / Field | Purpose | LGPD Basis |
|---|---|---|
| `TB_USER.USERNAME` | user identity within the system | Art. 7, V — contract execution / legitimate operational use |
| `TB_USER.EMAIL_ENC` | communication and account recovery | Art. 7, V or Art. 7, I depending on business flow |
| `TB_USER.EMAIL_HASH` | deterministic lookup without decryption | Art. 6 (necessity, security) + same basis as email collection |
| `TB_USER.ANONYMIZED_AT` | proof of erasure handling | Art. 18, IV |
| `TB_SESSION.*` | authentication session control | Art. 7, V — contract execution / system security |
| `TB_AUTH_ATTEMPT.*` | fraud and brute-force prevention | Art. 7, VI and Art. 6, VIII — security / prevention |
| `TB_PASSWORD_RESET.TOKEN_HASH` | secure password reset flow | Art. 7, V — contract execution / account access continuity |
| `TB_POLICY_VERSION.*` | preserve published legal text | Art. 8 — proof of consent context |
| `TB_POLICY_CLAUSE.*` | preserve clause structure and mandatory flags | Art. 8 — proof of consent granularity |
| `TB_CONSENT_LOG.*` | preserve consent and revocation history | Art. 7, I and Art. 8 |

## Final Compliance Notes

The current relational design supports LGPD compliance through a combination of:

- data minimization (`EMAIL_HASH` + `EMAIL_ENC` split)
- explicit anonymization tracking with `ANONYMIZED_AT`
- append-only legal evidence for terms and consent
- role-based access control and row-level security
- environment separation between synthetic and real data
