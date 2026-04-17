# Sprint 3 — Strategic Vision and Compliance

[Back to main README](../README.md#date-sprint-backlog)

> **Period:** 05/11/2026 → 05/31/2026  
> **Status:** ⏳ Waiting

---

## 🎯 Sprint Goal

Deliver the complete strategic product vision — consolidating the SAM, the geographic heatmap and LGPD compliance, closing the analysis cycle that goes from raw BDGD/ANEEL data to commercial region prioritization for Tecsys, with emphasis on opportunities in the transmission network.

---

## ✅ Sprint MVC — Deliverables

### 🟢 Minimum Commitment
What the team commits to delivering by the end of the sprint.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | Geographic heatmap with Leaflet | ⬜ |
| 2 | SAM calculation and display | ⬜ |
| 3 | LGPD compliance | ⬜ |

### 🔵 Additional Deliverables
What will be delivered beyond the minimum, if time and context allow.

| # | Feature | Status |
|:--|:--------|:------:|
| 1 | Automatic recalculation of indicators after each new data load | ⬜ |

---

## 📋 User Stories and Requirements

| User Story | Description | Requirements | Priority |
|:-----------|:------------|:------------:|:--------:|
| US10 | As an analyst, I want a SAM indicator per region. | RF08 | 🔴 Highest |
| US11 | As a commercial analyst, I want a geographic visualization to prioritize regions for commercial outreach. | RF09 | 🔴 Highest |
| US12 | As a user, I want control and transparency over my personal data (LGPD). | RF07, RF10 | 🟠 High |
| US13 | As an analyst, I want indicators to be automatically recalculated after each new data load. | RNF05 | 🟡 Medium |

---

## ✅ Definition of Ready / Definition of Done

### Definition of Ready (DoR)

*An issue is ready to enter the sprint when:*

- Has a title in the format `[TYPE] - Clear description`
- Has a type label defined (`type:feature`, `type:bug`, `type:hotfix`, etc.)
- Is linked to at least one User Story (US01–US13)
- Is linked to the related requirements (RF/RNF)
- Has clear and measurable acceptance criteria
- Has been estimated by the team
- Has no unresolved blocking dependencies
- Has been given a preview date of when the issue might be ready for PR
- Developer responsible for the task has a clear view of the expected result

### Definition of Done (DoD)

*An issue is done when:*

**Development**
- Code implemented and functional
- Branch follows the pattern `type/number-description` (e.g. `feature/42-implement-jwt`)
- All commits follow Conventional Commits with `#number` required in the footer
- No commits rejected by the hook pending correction

**Review**
- Pull Request opened with `Closes #number` in the description
- Code review approved by at least 1 team member
- PR merged into `main` or `develop`
- Issue closed automatically by the merge

**Documentation**
- Technical documentation updated if necessary
- Documentation needed for the task to be validated by another member

**LGPD (when applicable)**
- Sensitive data stored exclusively in PostgreSQL
- Public data (BDGD) stored in MongoDB
- No personal data exposed in logs or reports

---

## 🏗️ Architecture and Technical Decisions

### Leaflet integration with React for the heatmap

The heatmap will be implemented with **Leaflet** integrated into React via
`react-leaflet`, with the `leaflet.heat` plugin for heatmap rendering.

The choice of Leaflet is justified by:
- Lower learning curve compared to alternatives such as Google Maps or Mapbox
- Native heatmap support via official plugin
- Open source with no API cost
- Clean integration with `react-leaflet` in the React frontend

**Aggregation strategy for the map:**  
The `CONJ` layer (82 MultiPolygon polygons) is the ideal aggregation level for
the heatmap. Instead of rendering millions of individual points, the map displays
82 geographic zones with the average criticality of each set — adequate
browser performance without compromising readability.

The map supports **filtering by network type** (transmission/distribution) and by
indicator (DEC, FEC, losses), using the `network_type` attribute defined in Sprint 1.

### SAM calculation

The SAM is obtained by applying filters over the physical TAM calculated in Sprint 2.
The `ARE_LOC` field from BDGD is the central operational criterion:

- **Technical:** points whose infrastructure is compatible with the Tecsys sensor
- **Regulatory:** distributors under mandatory DEC/FEC targets set by ANEEL
- **Operational:** `ARE_LOC != dense urban` — prioritization of the transmission
  network and peri-urban/rural points where installation logistics are viable

> The SAM closes the cycle: TAM answers *"how many points exist?"*,
> SAM answers *"how many points can Tecsys realistically serve?"*.
> For Tecsys, the answer lies predominantly in `SUB`, `UNTRAT` and
> `UNTRMT` with `ARE_LOC` rural or peri-urban.

### LGPD Compliance

LGPD compliance will be implemented on top of the sensitive data layer
already isolated in PostgreSQL since Sprint 1. The system collects only
strictly necessary data: **name, email, password and role**.

**Anonymization and protection**
- Password stored as a **bcrypt** hash — never in plain text
- Email and name masked in system logs and exported reports
- Role retained only for access profile control

**Explicit consent**
- Mandatory acceptance of terms of use at registration, in accordance with Art. 8 of the LGPD

**Retention and deletion policy**
- Data retained while the account is active
- Complete deletion within 30 days upon request, in accordance with Art. 18 of the LGPD
- Access logs retained for 90 days for auditing purposes

**Simplified ROPA**
- Data processing record generated for academic purposes

> The separation between PostgreSQL (sensitive data) and MongoDB (public BDGD data),
> defined in Sprint 1, was the main architectural factor that simplified
> LGPD compliance implementation in this sprint.

### Automatic recalculation of indicators

After each new data load, the system automatically triggers the recalculation
of DEC, FEC and loss indicators. The interface displays the date/time of the last
load and the batch version identifier, ensuring traceability (RNF05).

---

*Last updated: 03/16/2026*
