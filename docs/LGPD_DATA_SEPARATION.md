# LGPD Data Separation: Dual-Database Architecture

**Card 1 | General | LGPD / ROPA**

**Related requirements:** RF11, RF10, RNF06, RNF08  
**Related documents:** [LGPD.md](LGPD.md), [NON-RELATIONAL_DATABASE.md](NON-RELATIONAL_DATABASE.md), [RELATIONAL-DATABASE.md](RELATIONAL-DATABASE.md), README RF10/RF11  
**Validated with:** Professor Sakaue  
**Last updated:** 05/10/2026

---

## 1. Purpose

This document records the architectural basis of the ZEUS LGPD compliance strategy: the project uses two different database systems because personal/sensitive data and public analytical data have different purposes, risks, and legal treatment.

The separation is not documented as a performance optimization. It is a structural compliance measure that supports:

- purpose limitation under LGPD Art. 6-I;
- necessity and data minimization under LGPD Art. 6-III;
- security and breach isolation under LGPD Art. 46;
- RF11, which formally requires storage separated by data purpose.

---

## 2. Legal Framework

### 2.1 Purpose Limitation - Art. 6-I, LGPD

Data collected for authentication, access control, consent, and audit must not be reused for analytical processing of ANEEL/BDGD public datasets.

In ZEUS, this rule is implemented structurally: personal data remains in PostgreSQL, while analytical data remains in MongoDB. A dashboard, TAM/SAM calculation, DEC/FEC analysis, ranking, or heatmap does not need personal data and therefore does not receive it.

### 2.2 Necessity / Data Minimization - Art. 6-III, LGPD

Minimization applies not only to which fields are collected, but also to which systems are allowed to access them.

The analytical layer uses MongoDB collections that do not store user identity, credentials, sessions, consent records, or personal audit details. This reduces the amount of personal data available to analytical processing by design.

### 2.3 Security Measures - Art. 46, LGPD

The dual-database architecture reduces the impact of isolated database compromise:

- a MongoDB incident exposes public ANEEL/BDGD analytical data, not ZEUS user personal data;
- a PostgreSQL incident exposes the sensitive application domain, not the full analytical infrastructure dataset;
- there is no stored `USER_UUID` reference in MongoDB that links a natural person to an analytical document.

### 2.4 RF11 - Dual-Database Storage Architecture

RF11 states that the system must use a storage architecture separated by data purpose:

- PostgreSQL: personal data, credentials, consents, sessions, and sensitive audit logs;
- MongoDB: public ANEEL/BDGD data, geospatial infrastructure data, and analytical collections.

This document is the LGPD interpretation of RF11.

---

## 3. Database Scope

### 3.1 PostgreSQL - Inside LGPD Personal Data Scope

PostgreSQL stores data that identifies, authenticates, tracks, or audits natural persons using the ZEUS system.

| Table | What it holds | LGPD category |
|---|---|---|
| `TB_USER` | Username, email hash/encrypted email, password hash, profile, status | Personal data - directly identifying |
| `TB_SESSION` | Session records, masked IP, user agent, timestamps | Personal data linked to authenticated user |
| `TB_AUTH_ATTEMPT` | Email hash, masked IP, authentication result | Pseudonymized personal data |
| `TB_CONSENT_LOG` | Consent and revocation events with timestamp and IP | Personal data linked to user |
| `TB_LOG` | Administrative actions by identified users | Personal data - actor and affected entity |
| `TB_PASSWORD_RESET` | Reset token hash and expiry | Personal data linked to user identity |
| `TB_POLICY_VERSION` | Policy and terms versions | Institutional data |
| `TB_POLICY_CLAUSE` | Clause text and mandatory flag | Institutional data |
| `TB_PROFILE` | Role and permission definitions | Institutional data |

### 3.2 MongoDB - Outside Personal Data Scope

MongoDB stores public or operational datasets related to legal entities, infrastructure, geographic areas, and aggregated regulatory indicators. These documents are outside the ZEUS personal data scope as long as the controls in Section 5 remain in force.

| Collection | What it holds | LGPD classification |
|---|---|---|
| `energy_losses_tariff` | Energy loss and tariff data per distributor | Not personal data; distributor is a legal entity |
| `substations` | Substation identifiers, distributor code, and infrastructure metadata | Not personal data |
| `distribution_transformers` | Transformer identifiers, technical specs, and infrastructure location data | Not personal data |
| `conj` | UC set geometry, DEC/FEC indicators, and annual summaries | Not personal data; aggregated/regulatory infrastructure data |
| `distribution_indices` | Regulatory continuity measurements per distributor, UC set, period, and indicator | Not personal data; CNPJ identifies a legal entity |
| `tam_sam` | Market sizing analytical outputs | Not personal data |
| `predictions` | Forecast outputs for analytical indicators | Not personal data |
| `load_history` | ETL load execution metadata | Operational metadata, not personal data when no user identifier is stored |
| `geodatabases` | Imported geodatabase metadata | Operational metadata, not personal data when no user identifier is stored |

---

## 4. Architecture

```text
ZEUS Application Layer - FastAPI

User management          Analytical dashboards
Authentication           TAM / SAM calculations
Consent flows            DEC / FEC indicators
Audit logging            Geographic heatmap

        |                           |
        | PostgreSQL connection      | MongoDB connection
        | sensitive domain           | analytical domain
        v                           v

PostgreSQL                         MongoDB
LGPD personal data scope            Outside ZEUS personal data scope

- users                             - public ANEEL/BDGD data
- credentials                       - infrastructure geometry
- sessions                          - regulatory metrics
- consent records                   - analytical collections
- sensitive audit logs              - predictions and market sizing
```

Architectural invariant:

- no cross-database join is part of the documented architecture;
- no MongoDB document should store `USER_UUID`, `USER_ID`, email, name, password, CPF, session token, consent identifier, or other natural-person identifier;
- PostgreSQL and MongoDB use distinct connection flows and environment configuration.

---

## 5. Controls That Enforce the Separation

| Control | Mechanism | What it prevents |
|---|---|---|
| Separate database systems | PostgreSQL for sensitive relational data; MongoDB for public/semi-structured analytical data | Accidental relational joins between personal data and analytical documents |
| Separate connection flows | PostgreSQL uses `get_postgres_connection()`; MongoDB uses `get_db()`/`get_client()` from the backend database connection module | Mixing credentials and query paths in normal repository/service code |
| No user identifiers in MongoDB schemas | Current MongoDB collection schemas model distributors, CNPJ, UC sets, geometry, indicators, loads, predictions, and TAM/SAM data; they do not model `USER_UUID` | Persistent linkage between a natural person and analytical records |
| No cross-database foreign keys | MongoDB references distributor codes, CNPJ, UC set codes, geodatabase IDs, and infrastructure identifiers only | Stored relationship between `TB_USER.USER_UUID` and a MongoDB record |
| Separate repository/domain patterns | User, policy, consent, and authentication logic live in PostgreSQL repositories; analytical collections are handled through MongoDB collection setup and analytical services | Developer-level confusion between sensitive CRUD and analytical processing |
| Log privacy validation | Application logging documentation requires no personal data in operational logs and references `scripts/validate_log_privacy.py` as the validation gate | Personal data leaking to log files that could be reused by analytical or operational pipelines |
| Code review invariant | Any PR adding user identifiers, email, CPF, names, session data, consent references, or personal audit fields to MongoDB must be blocked | Future erosion of the LGPD separation argument |

Important implementation note: MongoDB `validationLevel="strict"` validates inserts and updates against the configured JSON Schema, but it does not by itself reject every undeclared field unless the schema is written to do that. Therefore, the current LGPD guarantee depends on both schema design and code review. If the team wants this to become a fully mechanical database-level guarantee, add explicit rejection of additional user-identifying fields to MongoDB validators and CI checks.

---

## 6. Legal Properties Achieved

### 6.1 Purpose Limitation at Infrastructure Level

Instead of relying only on a policy that says "do not use authentication data for analytics", ZEUS stores each data domain in a different database system. This makes the intended purpose visible in the infrastructure:

- authentication, consent, sessions, and audit belong to PostgreSQL;
- ANEEL/BDGD analytics belong to MongoDB.

The architecture makes misuse harder and easier to detect in review.

### 6.2 Minimization by Default

Analytical operations such as TAM calculation, SAM evolution, criticality ranking, DEC/FEC analysis, heatmap rendering, and forecasts operate on MongoDB collections. These collections do not need and do not store ZEUS user personal data.

As a result, analytical processing receives only the data needed for its purpose.

### 6.3 Breach Isolation

| Scenario | Personal data exposed? | Analytical ANEEL/BDGD data exposed? | Person-to-network linkage possible? |
|---|---|---|---|
| PostgreSQL only breached | Yes | No | No stored MongoDB analytical data is exposed |
| MongoDB only breached | No | Yes | No, because MongoDB stores no ZEUS user identifier |
| Both databases breached | Yes | Yes | Only if an attacker also has enough application context to correlate data outside the documented storage model |

A single-database architecture would expose both domains in the same compromise. The dual-database architecture limits each isolated incident to its own data domain.

---

## 7. ROPA Entry

| Field | Value |
|---|---|
| Activity name | Structural separation of personal data and public analytical data into distinct database systems |
| Controller | Tecsys do Brasil Ltda. |
| Measure type | Technical security measure under LGPD Art. 46; architectural purpose limitation under Art. 6-I; minimization control under Art. 6-III |
| PostgreSQL scope | Users, credentials, sessions, password reset tokens, consent records, policy acceptance history, and sensitive audit logs |
| MongoDB scope | Public ANEEL/BDGD data, infrastructure geometry, distributor/regulatory metrics, analytical collections, forecasts, TAM/SAM outputs |
| Cross-contamination controls | No `USER_UUID` in MongoDB schemas, separate connection flows, no cross-database foreign keys, no documented cross-database joins, code review invariant |
| Breach isolation property | MongoDB breach: no ZEUS personal data exposure from MongoDB; PostgreSQL breach: no direct exposure of MongoDB analytical collections |
| Legal basis for architecture | RF11 + LGPD Art. 46 + LGPD Art. 6-I + LGPD Art. 6-III |
