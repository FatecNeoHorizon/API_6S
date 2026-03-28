# Sprint 2 — Commercial Intelligence and Market Analysis

[Back to main README](../README.md#date-sprint-backlog)

> **Period:** 04/13/2026 → 05/03/2026  
> **Status:** ⏳ Waiting

---

## 🎯 Sprint Goal

Transform data into commercial intelligence — applying Machine Learning models to classify regions by criticality, generate loss rankings and calculate the physical TAM, delivering concrete metrics to Tecsys to support market decisions, with a primary focus on the transmission network.

---

## ✅ Sprint MVC — Deliverables

### 🟢 Minimum Commitment
What the team commits to delivering by the end of the sprint.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | Region classification by criticality using ML | ⬜ |
| 2 | Region ranking by energy losses | ⬜ |
| 3 | Physical TAM calculation and display | ⬜ |

### 🔵 Additional Deliverables
What will be delivered beyond the minimum, if time and context allow.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | User management with distinct profiles (Administrator and Analyst) | ⬜ |
| 2 | ML model performance metrics documented | ⬜ |

---

## 📋 User Stories and Requirements

| User Story | Description | Requirements | Priority |
|:-----------|:------------|:------------:|:--------:|
| US05 | As an analyst, I want to group regions by criticality level. | RF05 | 🔴 Highest |
| US06 | As an analyst, I want to calculate the physical TAM for sensor installation. | RF04 | 🔴 Highest |
| US07 | As an analyst, I want a ranking of regions by energy losses. | RF06 | 🟠 High |
| US08 | As an administrator, I want to register and manage users with distinct profiles. | RF07 | 🟠 High |
| US09 | As an analyst, I want ML models to have documented performance and validated metrics. | RNF04 | 🟡 Medium |

---

## 🏗️ Architecture and Technical Decisions

### Features for the ML model

BDGD data allows building concrete features per region (aggregated by `CONJ`):

| Feature | Source Layer | Field | Description |
|:--------|:------------|:------|:------------|
| Average DEC | UCBT_tab + UCMT_tab | DIC_01..12 (annual average) | Average outage duration |
| Average FEC | UCBT_tab + UCMT_tab | FIC_01..12 (annual average) | Average outage frequency |
| Average circuit loss | CTMT | PERD_MED | Average percentage loss |
| MV transformer losses | EQTRMT | PER_TOT (average per CONJ) | Transformer losses |

### Clustering model for criticality classification

To classify regions by criticality level (high, medium, low), the **K-Means**
algorithm with 3 clusters was adopted. The choice is justified by:

- Works well with the available tabular features (DEC, FEC, losses per CONJ)
- Straightforward implementation via scikit-learn, with extensive documentation and easy academic validation
- Fixed number of clusters aligned with requirement RF05 (low/medium/high)

The model is applied separately for transmission and distribution, using the
`network_type` attribute defined in Sprint 1. Performance is evaluated with **Silhouette Score** (RNF04).

### Regression model for loss ranking

For the region loss ranking, the **Random Forest Regressor** was adopted.
The main feature is `CTMT.PERD_MED` (average MV circuit loss), enriched
with `EQTRMT.PER_TOT` aggregated by `CONJ`. The ranking is generated separately
for transmission and distribution. Evaluated with **RMSE** (RNF04).

### Physical TAM calculation

Based on BDGD data, the physical TAM is calculated by counting the
monitorable points per network type:

**Transmission (Tecsys primary focus):**
- `SUB` — substations with geometry
- `UNTRAT` — HV transformers
- `SSDAT` — HV network segments (potential measurement points)
- `UNSEAT` — HV switching devices

**Distribution (secondary market):**
- `UNTRMT` — MV transformers

The `ARE_LOC` field is the operational criterion for separating viable points from
hard-to-reach ones. Validate `ARE_LOC` values with Tecsys before the sprint review.

### Access control with JWT

Authentication will be implemented with **JWT (JSON Web Token)** via `python-jose`
integrated with FastAPI. Credentials stored in PostgreSQL with bcrypt-hashed passwords.

---

*Last updated: 03/16/2026*