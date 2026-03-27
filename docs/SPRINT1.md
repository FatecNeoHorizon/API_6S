# Sprint 1 — Reports and Data Structure

[Back to main README](../README.md#date-sprint-backlog)

> **Period:** 03/16/2026 → 04/05/2026  
> **Status:** 🔄 In progress

---

## 🎯 Sprint Goal

Establish the data foundation and visibility of the electrical grid — building the ETL pipeline over BDGD/ANEEL data and exposing the first quality indicators (DEC, FEC and losses) through a functional and responsive interface, covering both the transmission and distribution networks.

---

## ✅ Sprint MVC — Deliverables

### 🟢 Minimum Commitment
What the team commits to delivering by the end of the sprint.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | Functional ETL pipeline with the priority BDGD layers | ⬜ |
| 2 | DEC, FEC and loss indicators aggregated by region | ⬜ |

### 🔵 Additional Deliverables
What will be delivered beyond the minimum, if time and context allow.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | Interactive dashboard with filters by region and network type | ⬜ |
| 2 | Responsive interface compatible with modern browsers | ⬜ |

---

## 📋 User Stories and Requirements

| User Story | Description | Requirements | Priority |
|:-----------|:------------|:------------:|:--------:|
| US01 | As an analyst, I want to access structural reports of distribution networks. | RF01, RF02 | 🔴 Highest |
| US02 | As an analyst, I want the system to expose quality data (DEC, FEC, losses). | RF01, RF03 | 🔴 Highest |
| US03 | As a user, I want the system to respond quickly without freezing. | RNF01, RNF02 | 🟠 High |
| US04 | As a user, I want to access the system from any modern browser. | RNF03 | 🟡 Medium |

---

## 🏗️ Architecture and Technical Decisions

### Separation of responsibilities between databases

The data architecture was designed with two databases with distinct and complementary responsibilities:

**PostgreSQL — sensitive data**  
Responsible for storing data that requires LGPD compliance:
user credentials, access profiles, and any personally identifiable information.
The choice ensures transactional control, referential integrity, and ease
of auditing — essential requirements for legal compliance.

**MongoDB — public data (BDGD)**  
Responsible for storing BDGD/ANEEL data.
Since this is public data, there are no privacy restrictions. The choice is justified
by the ease of ingesting large volumes of semi-structured data and native
GeoJSON support — required for BDGD layers with geometry.

> This separation ensures that sensitive data never flows through or
> resides in the same environment as public operational data,
> simplifying LGPD compliance and reducing the risk surface.

### BDGD layers and ingestion strategy

The BDGD is composed of 43 layers. In this sprint, only the high-priority layers
for indicators and network structure are ingested:

**Mandatory layers in Sprint 1:**
- `SUB` — substations with geometry
- `UNTRAT` — HV transformers with losses and monthly energy
- `UNTRMT` — MV transformers with geometry and losses
- `SSDAT` — HV network segments with geometry
- `CTMT` — MV circuits with monthly loss indicators
- `UCBT_tab` — LV consumers with monthly DIC/FIC
- `UCMT_tab` — MV consumers with monthly DIC/FIC
- `UCAT_tab` — HV consumers with monthly DIC/FIC
- `CONJ` — geographic sets — aggregation level for the heatmap

**Special attention:**
`UCBT_tab` has 3M records (1.4GB in memory). Ingestion must be done
in chunks of 100,000 rows. A composite index `{DIST, MUN, CONJ}` must be
created before any analytical query.

### DEC and FEC indicator calculation

DEC and FEC are calculated from the fields `DIC_01..DIC_12` and `FIC_01..FIC_12`
present in the consumer tables (`UCBT_tab`, `UCMT_tab`, `UCAT_tab`).
The ETL aggregates these values by `MUN` (municipality) and `CONJ` (electrical set)
— never exposing individual data by consumer unit.

### Energy losses

Three granularities available in BDGD:
- **By MV circuit:** `CTMT.PERD_MED` — average percentage loss per circuit. Main feature for ranking.
- **By MV transformer:** `EQTRMT.PER_TOT` — total loss per transformer.
- **By HV transformer:** difference between `UNTRAT.ENES_XX` (secondary energy) and `UNTRAT.ENET_XX` (tertiary energy).

### API structure with FastAPI

The backend will be built with FastAPI for three main reasons:
exposing data via REST API to the React frontend, natural integration
with ML libraries (scikit-learn, pandas/geopandas), and automatic Swagger
documentation generation — facilitating client communication and route
validation during sprint reviews.

### ETL pipeline design

The pipeline follows the extract → transform → load flow, with log entries
at each stage and batch version control. Each load receives a version
identifier, allowing traceability of which dataset fed each indicator
displayed on the interface.

The `network_type` attribute (transmission/distribution) is derived from the nominal
voltage of each layer and stored as an indexable field in MongoDB for use in
subsequent sprints. The `ARE_LOC` field (location area: urban/rural/peri-urban),
present in several layers, is preserved to feed the SAM operational filter in Sprint 3.

---

*Last updated: 03/16/2026*