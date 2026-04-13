# Sprint 2 — Commercial Intelligence and Market Analysis

[Back to main README](../README.md#date-sprint-backlog)

> **Period:** 04/13/2026 → 05/03/2026  
> **Status:** ⏳ Waiting

---

## 🎯 Sprint Goal

Transform data into commercial intelligence — applying Machine Learning models to classify regions by criticality, generate loss rankings and calculate the physical TAM, delivering concrete metrics to Tecsys to support market decisions.

---

## ✅ Sprint MVC — Deliverables

### 🟢 Minimum Commitment
What the team commits to delivering by the end of the sprint.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | Prediction of market indicators using ML | ⬜ |
| 2 | Region ranking by energy losses | ⬜ |
| 3 | Physical TAM calculation and display | ⬜ |

### 🔵 Additional Deliverables
What will be delivered beyond the minimum, if time and context allow.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | User management with distinct profiles (Administrator and Analyst) | ⬜ |

---

## 📋 User Stories and Requirements

| User Story | Description | Requirements | Priority |
|:-----------|:------------|:------------:|:--------:|
| US05 | As an analyst, I want to calculate the physical TAM for sensor installation. | RF04 | Medium |
| US06 | As an analyst, I want a ranking of regions by energy losses. | RF06 | Low |
| US07 | As an administrator, I want to register and manage users with distinct profiles. | RF07 | High |
| US09 | As an analyst, I want ML models to predict market behavior based on validated metrics. | RNF04 | Medium |

---

## 🏗️ Architecture and Technical Decisions

### Features for the ML model

BDGD data allows building concrete features per region (aggregated by `CONJ`):

| Feature |  Description |
|:--------|:------------|
| Average DEC | Average outage duration |
| Average FEC | Average outage frequency |

### Prediction of market indicators

To accurately predict the market indicators we will implement trough a time series approach

- Works well with the available tabular features (DEC, FEC, losses per CONJ)

The model is applied for DEC/FEC and distribution, using the
`distribution_indices` collection defined in Sprint 1.
### Access control with JWT

Authentication will be implemented with **JWT (JSON Web Token)** via `python-jose`
integrated with FastAPI. Credentials stored in PostgreSQL with bcrypt-hashed passwords.

---

*Last updated: 04/12/2026*