# LGPD - Append-Only Consent History and Retrieval Logic

## 1. Consent History Model

The system records user consent through an append-only event model. Consent is not represented as a single mutable flag, such as `accepted = true`, because that would only show the latest condition and would erase the historical sequence of acceptance, revocation, and re-acceptance.

Instead, every consent-related action creates a new record in `TB_CONSENT_LOG`. This table stores consent events for all users in the system, with each event linked to a specific user through `USER_ID`.

Each consent event records:

| Field | Purpose |
|---|---|
| `USER_ID` | Identifies the user associated with the consent event |
| `CLAUSE_ID` | Identifies the specific clause accepted or revoked |
| `POLICY_VERSION_ID` | Identifies the version of the policy associated with the clause |
| `ACTION` | Indicates whether consent was accepted or revoked |
| `SOURCE_IP` | Records the technical origin of the action, when available |
| `USER_AGENT` | Records the client/browser context |
| `CHANNEL` | Identifies the channel through which the event was submitted |
| `CREATED_AT` | Records when the event occurred |

The table is therefore shared by all users, but the consent history of one specific person can be retrieved directly by filtering by `USER_ID`. The system does not need to list all users to locate a specific individual’s consent history.

---

## 2. Legal Basis and Compliance Rationale

This design supports the LGPD accountability and consent requirements by preserving evidence of the user’s decision at the time it was made.

Under **LGPD Art. 8, §5**, the burden of proof regarding consent belongs to the controller. The system must therefore be able to demonstrate that consent was obtained in a valid, traceable and auditable manner. `TB_CONSENT_LOG` provides this evidence by preserving each consent action as an independent event.

Under **LGPD Art. 6, X**, the accountability principle requires the controller to demonstrate compliance with data protection rules. The append-only model supports this principle because it preserves the historical sequence of consent events instead of overwriting it.

Under **LGPD Art. 12**, anonymized data is not considered personal data when it cannot be associated with an identified or identifiable natural person. After anonymization, the personal fields in `TB_USER` are removed or overwritten, while the technical `USER_ID` can remain as a non-identifying reference.

Under **LGPD Art. 16**, certain records may be preserved after the end of processing when retention is necessary for legal compliance, accountability or defense of rights. Consent history may therefore be preserved after anonymization as institutional evidence that the controller had a valid legal basis during the active relationship with the user.

---

## 3. Why an Event Model Is Required

A flag-based model would be insufficient because it would only represent the current state. For example:

```text
accepted = true
```

This does not prove when the consent was given, which version of the policy was accepted, whether the user revoked consent later, or whether a new version was accepted after revocation.

The event model preserves the full consent timeline:

```text
User A | Clause 1 | Policy v1 | CONSENT_ACCEPTED | 2026-04-13 10:01
User A | Clause 1 | Policy v1 | CONSENT_REVOKED  | 2026-04-20 14:30
User A | Clause 1 | Policy v2 | CONSENT_ACCEPTED | 2026-04-27 09:15
```

No previous row is modified or deleted. Each row remains as evidence of what occurred at a specific moment.

This allows the system to answer not only whether the user currently has valid consent, but also how that state was reached.

---

## 4. Current Consent State

The system derives the current consent state from the latest event in `TB_CONSENT_LOG` for each combination of user and clause.

The logical rule is:

```text
Current consent for a clause = latest event for USER_ID + CLAUSE_ID
```

A simplified query is:

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

For retrieving the latest state of all clauses for one user, the system can use:

```sql
SELECT DISTINCT ON (CLAUSE_ID)
    LOG_UUID,
    USER_ID,
    CLAUSE_ID,
    POLICY_VERSION_ID,
    ACTION,
    CREATED_AT
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id
ORDER BY CLAUSE_ID, CREATED_AT DESC, LOG_UUID DESC;
```

This retrieves one current event per clause for the selected user.

---

## 5. Pending Consent Evaluation

The project uses the consent history to determine whether a user still has mandatory pending clauses.

This is done through the pending consent logic, represented by `V_PENDING_CONSENT`. The view evaluates the latest consent event for each required clause and identifies which mandatory clauses have not yet been accepted.

The effective rule is:

```text
A mandatory clause is pending when:
- the user has no consent event for that clause; or
- the latest event is not an accepted consent.
```

This logic is used by the backend during authentication and protected route access. If mandatory consent is pending, the backend can block access and return the pending clauses to the frontend.

Therefore, `TB_CONSENT_LOG` stores the evidence, while the pending consent view derives the operational state used by the application.

---

## 6. Retrieving Consent for a Specific User

Because `TB_CONSENT_LOG` stores events from all users, searching for a specific person requires filtering by `USER_ID`.

Full consent history for one user:

```sql
SELECT
    LOG_UUID,
    USER_ID,
    CLAUSE_ID,
    POLICY_VERSION_ID,
    ACTION,
    SOURCE_IP,
    USER_AGENT,
    CHANNEL,
    CREATED_AT
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id
ORDER BY CREATED_AT DESC, LOG_UUID DESC;
```

Latest consent state per clause for one user:

```sql
SELECT DISTINCT ON (cl.CLAUSE_ID)
    cl.LOG_UUID,
    cl.USER_ID,
    cl.CLAUSE_ID,
    cl.POLICY_VERSION_ID,
    pv.POLICY_TYPE,
    pv.VERSION,
    cl.ACTION,
    cl.CREATED_AT
FROM TB_CONSENT_LOG cl
JOIN TB_POLICY_CLAUSE pc
  ON pc.CLAUSE_UUID = cl.CLAUSE_ID
JOIN TB_POLICY_VERSION pv
  ON pv.VERSION_UUID = COALESCE(cl.POLICY_VERSION_ID, pc.POLICY_VERSION_ID)
WHERE cl.USER_ID = :user_id
ORDER BY cl.CLAUSE_ID, cl.CREATED_AT DESC, cl.LOG_UUID DESC;
```

This allows the system to retrieve the consent state of a specific user without scanning or listing all members manually.

---

## 7. Tamper Resistance

Consent history must not be altered after it is recorded. For this reason, `TB_CONSENT_LOG` is protected as an append-only table.

The intended database control is a trigger that blocks `UPDATE` and `DELETE` operations:

```sql
CREATE OR REPLACE FUNCTION fn_protect_append_only()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Operation not allowed: this table is append-only for LGPD compliance';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TB_CONSENT_LOG_APPEND_ONLY
BEFORE UPDATE OR DELETE ON TB_CONSENT_LOG
FOR EACH ROW
EXECUTE FUNCTION fn_protect_append_only();
```

This means:

| Operation | Expected behavior |
|---|---|
| New consent | Insert a new row |
| Revocation | Insert a new row |
| Re-acceptance | Insert a new row |
| Update old event | Blocked |
| Delete old event | Blocked |

This mechanism preserves the evidentiary value of the consent history.

---

## 8. Evidence Supported by the History

The consent history can support several compliance and audit questions:

| Question | Evidence source |
|---|---|
| Did the user accept a specific clause? | `TB_CONSENT_LOG` filtered by `USER_ID` and `CLAUSE_ID` |
| What was the latest consent state? | Latest event by `CREATED_AT DESC` |
| Which policy version was accepted? | `POLICY_VERSION_ID` joined with `TB_POLICY_VERSION` |
| Did the user revoke consent? | A `CONSENT_REVOKED` event after a prior acceptance |
| Was consent valid at a given time? | Latest event before the target date |
| What clauses are still pending? | `V_PENDING_CONSENT` |
| What technical context was recorded? | `SOURCE_IP`, `USER_AGENT`, `CHANNEL`, `CREATED_AT` |

This makes the consent history useful both for operational control and for legal accountability.

---

## 9. Post-Anonymization Preservation

After user anonymization, personal fields in `TB_USER` are expected to be removed, cleared or replaced. Examples include username, encrypted email, email hash and password hash.

The consent log should not be automatically deleted as a consequence of anonymization. Instead, it may remain as an accountability record, provided that the remaining `USER_ID` no longer identifies a natural person.

Example:

```text
TB_CONSENT_LOG
USER_ID = 123e4567-e89b-12d3-a456-426614174000
CLAUSE_ID = clause-001
ACTION = CONSENT_ACCEPTED
CREATED_AT = 2026-04-13 10:01

TB_USER after anonymization
USER_UUID = 123e4567-e89b-12d3-a456-426614174000
USERNAME = [removed]
EMAIL_ENC = NULL
EMAIL_HASH = NULL
PASSWORD_HASH = [removed]
```

In this state, the identity has been removed, but the institutional proof that consent existed during the active period remains preserved.

This balances data minimization with the controller’s obligation to demonstrate compliance.

---

## 10. ROPA Entry

| Field | Value |
|---|---|
| Activity name | Append-only recording and preservation of consent events |
| Controller | Tecsys do Brasil Ltda. |
| Data subjects | Users who accept or revoke policy clauses |
| Data categories | User UUID, clause UUID, policy version UUID, consent action, timestamp, source IP, user-agent and channel |
| Processing purpose | Proof of consent, LGPD accountability, compliance evidence and legal defense |
| Legal basis | LGPD Art. 7, I; Art. 8, §5; Art. 6, X; Art. 16 |
| Storage table | `TB_CONSENT_LOG` |
| Related structures | `TB_USER`, `TB_POLICY_CLAUSE`, `TB_POLICY_VERSION`, `V_PENDING_CONSENT` |
| Current status derivation | Latest event per `USER_ID + CLAUSE_ID` |
| Tamper resistance | Database trigger blocking update and delete operations |
| Retention | Preserved while necessary for compliance, accountability and legal defense, including justified post-anonymization preservation |
| Third-party sharing | Not shared by default; may be made available to competent authority upon lawful request |

---

## 11. — Validation Questions and System Answers

### Question 1 — Where does the system store the latest consent given by a user?

The system does not store the latest consent as a separate mutable flag or status field. Instead, it stores every consent and revocation event in `TB_CONSENT_LOG`. The latest consent state is derived by selecting the most recent event for each combination of `USER_ID` and `CLAUSE_ID`, ordered by `CREATED_AT DESC`.

This ensures that the current consent state can be identified without losing the historical sequence of previous acceptances, revocations or re-acceptances.

---

### Question 2 — Does the system register consent only in `TB_CONSENT_LOG`?

Yes. `TB_CONSENT_LOG` is the official consent evidence table. It stores the complete append-only history of consent events.

The related policy structures, such as `TB_POLICY_VERSION` and `TB_POLICY_CLAUSE`, store the content and versioning of the policies and clauses. `TB_CONSENT_LOG` stores the user’s actions in relation to those clauses and versions.

Therefore, the consent event itself is recorded in `TB_CONSENT_LOG`, while the legal and textual context of the consent is obtained through its relationship with the policy tables.

---

### Question 3 — Is `TB_CONSENT_LOG` the same table for all users?

Yes. `TB_CONSENT_LOG` is a single shared table for the whole system. It records consent events from all users.

Each record is linked to one specific user through the `USER_ID` field. Because of this, the system can separate the consent history of each user without creating separate tables.

---

### Question 4 — How does the system retrieve the consent history of one specific person?

The system does not need to list all users to find one person’s consent history. It retrieves the records directly by filtering `TB_CONSENT_LOG` by `USER_ID`.

Example:

```sql
SELECT
    LOG_UUID,
    USER_ID,
    CLAUSE_ID,
    POLICY_VERSION_ID,
    ACTION,
    CREATED_AT
FROM TB_CONSENT_LOG
WHERE USER_ID = :user_id
ORDER BY CREATED_AT DESC;
```

This returns only the consent and revocation events associated with that specific user.

---

### Question 5 — How does the system know which consent version is currently valid?

The current consent version is identified by the latest event related to a specific user and clause. If the latest event is `CONSENT_ACCEPTED`, the clause is considered accepted. If the latest event is `CONSENT_REVOKED`, or if no event exists, the clause is considered pending.

The related `POLICY_VERSION_ID` allows the system to know which version of the policy was accepted or revoked.

---

### Question 6 — Why is this model legally safer than updating a single consent record?

Updating a single record would erase the previous state and weaken the controller’s ability to prove what happened over time.

The append-only model preserves the full evidence trail. It shows when consent was given, when it was revoked, whether it was accepted again, and which policy version was involved. This supports LGPD accountability and the controller’s burden of proof.

