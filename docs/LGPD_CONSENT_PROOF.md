# LGPD - Consent Proof Model and Evidence Hash

## 1. Purpose

This document describes how the system proves user consent under the LGPD and how the consent evidence chain is strengthened through a deterministic evidence hash stored with each consent event.

The system already records consent as an append-only history in `TB_CONSENT_LOG`. The proposed improvement adds a `CONSENT_HASH` field calculated from the core evidentiary values of the consent row:

```text
USER_ID + CLAUSE_ID + POLICY_VERSION_ID + ACTION + CREATED_AT
```

The purpose of this hash is not to replace the append-only trigger. It works as an additional integrity control. If any relevant value in a consent record is changed outside the expected flow, the stored hash will no longer match the recalculated hash.

---

## 2. LGPD Consent Requirements

LGPD Art. 8 requires consent to be free, informed, specific and unambiguous. Art. 8, §5 establishes that the controller bears the burden of proving that valid consent was obtained.

The system addresses these requirements as follows:

| Requirement | System evidence |
|---|---|
| Free | Optional clauses can be declined without blocking access when they are not operationally mandatory. The system records only the clauses actually accepted or revoked. |
| Informed | `TB_POLICY_CLAUSE` stores the clause content and `TB_POLICY_VERSION` stores the version context, allowing reconstruction of what was presented to the user. |
| Specific | Consent is recorded per clause, not only at the document or policy level. Each event refers to one `CLAUSE_ID`. |
| Unambiguous | A consent event is inserted only after an affirmative action in the consent flow. The event includes `ACTION`, `CREATED_AT`, `SOURCE_IP`, `USER_AGENT` and `CHANNEL`. |

This structure supports LGPD Art. 7, I for consent-based processing, Art. 8, §5 for burden of proof, and Art. 6, X for accountability.

---

## 3. Evidence Stored by the System

Each consent event is stored in `TB_CONSENT_LOG` with the user, clause, policy version, action and technical context.

The consent event itself is stored in:

```text
TB_CONSENT_LOG
```

The legal content and policy version are reconstructed through:

```text
TB_POLICY_CLAUSE
TB_POLICY_VERSION
```

Together, these tables allow the system to answer the essential evidentiary questions:

| Question | Evidence |
|---|---|
| Who gave consent? | `TB_CONSENT_LOG.USER_ID` |
| Which clause was accepted or revoked? | `TB_CONSENT_LOG.CLAUSE_ID` |
| Which policy version applied? | `TB_CONSENT_LOG.POLICY_VERSION_ID` and `TB_POLICY_VERSION.VERSION` |
| What was the text shown to the user? | `TB_POLICY_CLAUSE` content and metadata |
| When did the action occur? | `TB_CONSENT_LOG.CREATED_AT` |
| Was it an acceptance or revocation? | `TB_CONSENT_LOG.ACTION` |
| What technical context was recorded? | `SOURCE_IP`, `USER_AGENT`, `CHANNEL` |
| Was the record later altered? | `CONSENT_HASH` recalculation and append-only trigger |

---

## 4. Complete Evidence Chain

A complete consent record is reconstructed by joining the consent event with the policy clause and policy version.

```sql
SELECT
    cl.LOG_UUID,
    cl.USER_ID,
    cl.CLAUSE_ID,
    cl.POLICY_VERSION_ID,
    cl.ACTION,
    cl.CREATED_AT,
    cl.SOURCE_IP,
    cl.USER_AGENT,
    cl.CHANNEL,
    cl.CONSENT_HASH,
    pc.CODE AS CLAUSE_CODE,
    pc.TITLE AS CLAUSE_TITLE,
    pc.MANDATORY,
    pv.POLICY_TYPE,
    pv.VERSION
FROM TB_CONSENT_LOG cl
JOIN TB_POLICY_CLAUSE pc
  ON pc.CLAUSE_UUID = cl.CLAUSE_ID
JOIN TB_POLICY_VERSION pv
  ON pv.VERSION_UUID = COALESCE(cl.POLICY_VERSION_ID, pc.POLICY_VERSION_ID)
WHERE cl.USER_ID = :user_id
ORDER BY cl.CREATED_AT DESC, cl.LOG_UUID DESC;
```

This chain proves who consented, what was accepted or revoked, which version applied and when the event occurred.

---

## 5. Evidence Hash

The `CONSENT_HASH` is a deterministic SHA-256 hash generated from the core immutable values of the consent event:

```text
USER_ID
CLAUSE_ID
POLICY_VERSION_ID
ACTION
CREATED_AT
```

The hash is stored in the same row as the consent event. It provides an integrity seal for the evidentiary fields.

A simplified representation is:

```text
CONSENT_HASH = SHA256(
  USER_ID || CLAUSE_ID || POLICY_VERSION_ID || ACTION || CREATED_AT
)
```

The hash should be computed by the database before insertion, through a trigger. This prevents the application layer from deciding or manipulating the hash value.

The hash does not make the record immutable by itself. Immutability is still enforced by the append-only trigger that blocks `UPDATE` and `DELETE`. The hash adds a second verification layer: even if a value were changed outside the expected flow, recalculating the hash would expose the mismatch.

---

## 6. Tamper Resistance

The consent protection model uses two complementary controls:

| Control | Function |
|---|---|
| Append-only trigger | Blocks `UPDATE` and `DELETE` on `TB_CONSENT_LOG` |
| Evidence hash | Detects inconsistency if key evidentiary fields are altered |

The correct way to represent a change in consent is never to update an old row. A revocation or re-acceptance must create a new event.

Example:

```text
CONSENT_ACCEPTED  → first event
CONSENT_REVOKED   → second event
CONSENT_ACCEPTED  → third event
```

The full timeline remains available, and each row has its own hash.

---

## 7. Current Consent State

The current state is derived from the latest event for each combination of user and clause:

```sql
SELECT
    ACTION,
    POLICY_VERSION_ID,
    CREATED_AT,
    CONSENT_HASH
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id
  AND CLAUSE_ID = :clause_id
ORDER BY CREATED_AT DESC, LOG_UUID DESC
LIMIT 1;
```

If the latest event is `CONSENT_ACCEPTED`, the clause is considered accepted. If the latest event is `CONSENT_REVOKED`, or if no event exists, the clause is considered pending.

The operational pending-consent logic is derived through `V_PENDING_CONSENT`.

---

## 8. Specific User Retrieval

`TB_CONSENT_LOG` stores events from all users in a single table. The system does not need to list all users to find one individual’s consent history.

It retrieves the required evidence directly by filtering by `USER_ID`:

```sql
SELECT *
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id
ORDER BY CREATED_AT DESC, LOG_UUID DESC;
```

For the current state per clause:

```sql
SELECT DISTINCT ON (CLAUSE_ID)
    LOG_UUID,
    USER_ID,
    CLAUSE_ID,
    POLICY_VERSION_ID,
    ACTION,
    CREATED_AT,
    CONSENT_HASH
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id
ORDER BY CLAUSE_ID, CREATED_AT DESC, LOG_UUID DESC;
```

---

## 9. Integrity Verification Query

To verify whether a stored consent event still matches its evidentiary fields, the system can recalculate the hash and compare it with the stored value.

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

A `HASH_VALID = true` result indicates that the stored hash is consistent with the current row values.

---

## 10. User Agent Consistency

`USER_AGENT` should be stored consistently for all consent events. It is not part of the proposed hash because the hash is focused on the core legal event: user, clause, policy version, action and timestamp.

However, `USER_AGENT` strengthens the evidentiary context by linking the event to a browser or client environment. For this reason, the consent endpoint should always store a value, using `unknown` only when the header is unavailable.

---

## 11. Post-Anonymization Preservation

After anonymization, personal identifiers in `TB_USER` should be removed or replaced. The consent history may remain as non-identifying institutional evidence if `USER_ID` no longer maps to an identifiable natural person.

This supports LGPD Art. 12 regarding anonymized data and Art. 16 regarding justified post-termination retention for legal compliance and defense of rights.

The consent hash remains useful after anonymization because it proves that the historical consent evidence was not altered, without requiring personal data to remain identifiable.

---

## 12. ROPA Entry

| Field | Value |
|---|---|
| Activity name | Consent collection and evidence integrity preservation |
| Controller | Tecsys do Brasil Ltda. |
| Data subjects | Platform users who accept or revoke clauses |
| Data categories | User UUID, clause UUID, policy version UUID, consent action, timestamp, source IP, user-agent, channel and consent hash |
| Purpose | Establishing proof of consent, accountability and legal defense |
| Legal basis | LGPD Art. 7, I; Art. 8, §5; Art. 6, X; Art. 16 |
| Storage table | `TB_CONSENT_LOG` |
| Related tables | `TB_POLICY_CLAUSE`, `TB_POLICY_VERSION`, `TB_USER` |
| Integrity control | Append-only trigger and deterministic SHA-256 consent hash |
| Retention | Preserved while necessary for compliance, accountability and legal defense |
| Sharing | Not shared by default; available to competent authority upon lawful request |

---

## 13. FAQ

This section summarizes the review questions raised during the consent proof validation and the corresponding technical answers implemented or documented by the system.

### Question 1 — Is the current consent model sufficient to prove that a person accepted the terms or clauses?

Yes. The consent model is structured to produce evidence of consent at the clause level. Each consent event is recorded in `TB_CONSENT_LOG` and linked to:

- the user who performed the action;
- the specific clause accepted or revoked;
- the policy version associated with that clause;
- the action performed;
- the timestamp of the event;
- the technical context of the request.

This allows the system to reconstruct the evidence chain and demonstrate who consented, what was accepted, when the action occurred and which policy version applied.

### Question 2 — How does the system prove that the consent was related to a specific clause and policy version?

The consent event stored in `TB_CONSENT_LOG` references both `CLAUSE_ID` and `POLICY_VERSION_ID`.

The legal content is not stored only as free text in the log. Instead, the system reconstructs the accepted content by joining:

```text
TB_CONSENT_LOG
TB_POLICY_CLAUSE
TB_POLICY_VERSION
```

This makes it possible to verify the exact clause and the corresponding policy version that were available at the time of consent.

### Question 3 — How does the system certify that the consent row was not changed after being recorded?

The system uses two complementary integrity controls.

First, `TB_CONSENT_LOG` is protected by an append-only model. Existing consent events must not be updated or deleted. Any later revocation or re-acceptance must create a new event.

Second, the proposed improvement adds a deterministic `CONSENT_HASH` to each consent row. This hash is calculated from the core evidentiary fields:

```text
USER_ID + CLAUSE_ID + POLICY_VERSION_ID + ACTION + CREATED_AT
```

If one of these fields is changed after insertion, the stored hash will no longer match a recalculated hash.

### Question 4 — What is the purpose of the consent hash?

The consent hash is an additional assurance mechanism. It does not replace the append-only rule, but strengthens it.

The append-only trigger prevents normal `UPDATE` and `DELETE` operations. The hash allows later verification that the main legal evidence fields remain consistent with the original event.

Therefore, the hash works as a tamper-evidence seal for the consent row.

### Question 5 — How is the hash generated?

The hash should be generated by the database, not manually by the application. A database function computes a SHA-256 hash using the core consent fields, and a `BEFORE INSERT` trigger fills `CONSENT_HASH` when a new row is inserted into `TB_CONSENT_LOG`.

This ensures that every consent event receives a hash automatically and consistently.

### Question 6 — How can the system verify the hash later?

The system can recalculate the hash using the same fields and compare it with the stored `CONSENT_HASH`.

Example:

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

If `HASH_VALID` is `true`, the stored hash matches the current row values. If it is `false`, the record requires investigation.
