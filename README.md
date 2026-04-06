# <p align="center">API 6th Semester - BD 2026


<p align="center">
  <img src="image/logo/Zeus.png" alt="Project logo" width="400">
</p>

<p align="center">
  <a href="#problem">💡 Context and Challenge</a> •
  <a href="#objective">🎯 Project Objective</a> •
  <a href="#requirements">📋 Requirements</a> •
  <a href="#product-backlog">📦 Product Backlog</a> •
  <a href="#sprint-backlog">🗓️ Sprint Backlog</a> •
  <a href="#dor-dod">✅ DoR / DoD</a> •
  <a href="#schedule">📅 Schedule</a> •
  <a href="#team-members">👥 Team Members</a> •
  <a href="#technologies">🛠️ Technologies</a> •
  <a href="#process-standards">📁 Process Standards</a> •
  <a href="#technical-documentation">📖 Technical Documentation</a> •
  <a href="#burndown">📈 Burndown</a>
</p>

---

## 💡 Context and Challenge <a id="problem"></a>

[Tecsys do Brasil](https://www.tecsysbrasil.com.br/), a partner company operating in the electrical grid monitoring sector, has products capable of identifying faults and vulnerabilities in the energy distribution infrastructure. However, despite mastering field monitoring technology, the company lacks a structured way to process and analyze the public data made available by ANEEL. Without this treatment, accurately identifying which regions of Brazil present the highest criticality in the distribution network requires significant manual effort — also making it difficult to identify where there is the greatest potential for applying their products.

---

## 🎯 Project Objective <a id="objective"></a>

The project's objective is to develop a platform that processes and analyzes data from ANEEL, transforming raw information into actionable indicators. This will allow analysts to identify priority regions based on criteria such as supply quality, energy losses and network vulnerability — providing the commercial team with concrete data to approach new markets and product application opportunities.

---

## 📋 Requirements <a id="requirements"></a>

<details>
<summary>Show Functional and Non-Functional Requirements</summary>

### Functional Requirements

| ID | Requirement | Description |
|:---|:---|:---|
| <a id="RF01">RF01</a> | _ETL Pipeline_ | The system must perform extraction, transformation and loading (ETL) of data from the ANEEL database, with log recording and data version control. |
| <a id="RF02">RF02</a> | _Distribution Network Dashboard_ | The system must display data related to distribution network structures (geographic, electrical and structural information) via interactive dashboards and reports. |
| <a id="RF03">RF03</a> | _Distribution Network Reports_ | The system must display quality indicators and metrics for electrical networks (DEC, FEC and energy losses), allowing filtering by region and period. |
| <a id="RF04">RF04</a> | _Physical TAM Calculation_ | The system must calculate and display the physical TAM (Total Addressable Market) for sensor installation in the electrical grid, identifying the maximum number of technically monitorable points in Brazil. |
| <a id="RF05">RF05</a> | _Criticality Classification with ML_ | The system must group regions or network areas by criticality level (high, medium, low), applying Machine Learning models to support action prioritization. |
| <a id="RF06">RF06</a> | _Energy Loss Ranking_ | The system must generate a ranking of regions based on energy loss indicators, using regression models to project and rank the most critical areas. |
| <a id="RF07">RF07</a> | _User and Profile Management_ | The system must allow user registration with distinct profiles (Administrator and Analyst), controlling access to features and data according to the profile. |
| <a id="RF08">RF08</a> | _SAM Calculation_ | The system must calculate and display SAM values, crossing the TAM with technical, regulatory and operational feasibility criteria. |
| <a id="RF09">RF09</a> | _Geographic Heatmap_ | The system must display a geographic heatmap indicating the criticality level of the electrical grid by region, with support for dynamic filters by indicator. |
| <a id="RF10">RF10</a> | _LGPD Compliance_ | The system must ensure LGPD compliance: explicit consent collection, personal data anonymization, retention and deletion policy, and generation of a data processing report (simplified ROPA for academic purposes). |

<br>

### Non-Functional Requirements

| ID | Requirement | Description |
|:---|:---|:---|
| <a id="RNF01">RNF01</a> | _Database Query Performance_ | Critical queries to the relational database (sensitive data) and MongoDB (ANEEL data) must perform adequately for smooth application use, with pagination and basic indexing. |
| <a id="RNF02">RNF02</a> | _Application Startup and Stability_ | The web application must start correctly and operate stably during continuous use sessions, without freezing or unexpected errors. |
| <a id="RNF03">RNF03</a> | _Responsiveness and Compatibility_ | The interface must be responsive, ensuring compatibility and a good experience on modern browsers. |
| <a id="RNF04">RNF04</a> | _ML Performance Metrics_ | The performance of the trained machine learning model must be documented with metrics appropriate to the task type: Silhouette Score for clustering, RMSE for regression and F1-Score for classification. |
| <a id="RNF05">RNF05</a> | _Post-Load Consistency_ | Whenever there is a new data load, indicators (DEC, FEC and losses) must be recalculated, displaying the date/time of the last load and the batch version identifier used. |

</details>

---

## 📦 Product Backlog <a id="product-backlog"></a>

<details>
<summary>Show Product Backlog</summary>

<br>

| ID | Rank | Priority | User Story | Sprint | Related Requirements |
|:---|:---|:---|:---|:---|:---|
| US01 | 01 | Highest | As a data analyst, I want to access structural reports of distribution networks, to identify geographic, electrical and structural characteristics of the monitored infrastructure. | 01 | [RF01](#RF01), [RF02](#RF02) |
| US02 | 02 | Highest | As a data analyst, I want the system to expose quality data (DEC, FEC, losses), to evaluate electrical grid performance by region and period. | 01 | [RF01](#RF01), [RF03](#RF03) |
| US03 | 03 | High | As a user, I want the system to respond quickly to my queries, without freezing during use. | 01 | [RNF01](#RNF01), [RNF02](#RNF02) |
| US04 | 04 | Medium | As a user, I want to access the system from any modern browser with a good visual experience. | 01 | [RNF03](#RNF03) |
| US05 | 01 | Highest | As a data analyst, I want to group regions by criticality level, so the commercial team can prioritize approaches in areas with the highest product application potential. | 02 | [RF05](#RF05) |
| US06 | 02 | Highest | As a commercial analyst, I want to calculate the physical TAM for sensor installation, to size the maximum universe of monitorable points in Brazil. | 02 | [RF04](#RF04) |
| US07 | 03 | High | As a data analyst, I want a ranking of regions by energy losses, to identify the most critical areas and support technical and commercial decisions. | 02 | [RF06](#RF06) |
| US08 | 04 | High | As an administrator, I want to register and manage users with distinct profiles, to control access to features according to each user's role. | 02 | [RF07](#RF07) |
| US09 | 05 | Medium | As a data analyst, I want ML models to have documented performance and validated metrics, to ensure the reliability of results generated by the system. | 02 | [RNF04](#RNF04) |
| US10 | 01 | Highest | As a commercial analyst, I want a SAM indicator, to identify the accessible market for the product by region based on technical and regulatory criteria. | 03 | [RF08](#RF08) |
| US11 | 02 | Highest | As a commercial analyst, I want a geographic visualization (heatmap), to visually identify priority regions for commercial outreach. | 03 | [RF09](#RF09) |
| US12 | 03 | High | As a user, I want control and transparency over my personal data (LGPD), to ensure my information is handled securely and in accordance with the law. | 03 | [RF07](#RF07), [RF10](#RF10) |
| US13 | 04 | Medium | As a data analyst, I want indicators to be automatically recalculated after each new data load, to ensure analyses always reflect the most up-to-date information. | 03 | [RNF05](#RNF05) |

</details>

---

## 🗓️ Sprint Backlog <a id="sprint-backlog"></a>

<details>
<summary>Show Sprint Backlog</summary>

### Sprint 1
[View Sprint 1 documentation](docs/SPRINT-1.md)



### 📹 Vídeo demonstrativo:

<div align="center">
  <a href="https://www.youtube.com/watch?v=w10nwgCj9kc">
    <img src="https://img.youtube.com/vi/w10nwgCj9kc/maxresdefault.jpg" alt="Vídeo demonstrativo - Clique para assistir" width="600">
  </a>
</div>


### 📈 Sprint 1 Evolution (Burndown) 
<img src="burndown/src/main/resources/static/sprint-1.png">

### Sprint 2
[View Sprint 2 documentation](docs/SPRINT-2.md)

### Sprint 3
[View Sprint 3 documentation](docs/SPRINT-3.md)

</details>

---

## ✅ Definition of Ready / Definition of Done <a id="dor-dod"></a>

<details>
<summary>Show DoR / DoD</summary>

### Definition of Ready (DoR)

*An issue is ready to enter the sprint when:*

- Has a title in the format `[TYPE] - Clear description`
- Has a type label defined (`type:feature`, `type:bug`, `type:hotfix`, etc.)
- Is linked to at least one User Story (US01–US13)
- Is linked to the related requirements (RF/RNF)
- Has clear and measurable acceptance criteria
- Has been estimated by the team
- Has no unresolved blocking dependencies

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

**LGPD (when applicable)**
- Sensitive data stored exclusively in PostgreSQL
- Public data (BDGD) stored in MongoDB
- No personal data exposed in logs or reports

</details>

---

## 📅 Schedule <a id="schedule"></a>

| Sprint | Name | Start Date | End Date | Status |
|:---:|:---|:---:|:---:|:---:|
| --- | KickOff                   | 03/02 | 03/06 | Ok |
| --- | Planning                  | 03/09 | 03/13 | Ok |
|  1  | Sprint 1                  | 03/16 | 04/05 | Ok |
|  2  | Sprint review / Planning  | 04/06 | 04/10 |    |
|  3  | Sprint 2                  | 04/13 | 05/03 |    |
|  4  | Sprint review / Planning  | 05/04 | 05/08 |    |
|  5  | Sprint 3                  | 05/11 | 05/31 |    |
|  6  | Sprint review             | 06/01 | 06/05 |    |
|  7  | Solutions Fair            | 06/11 |       |    |
|  8  | TG Presentations          | 06/15 | 06/19 |    |

---

## 👥 Team Members <a id="team-members"></a>

| *Name*                   | *Function*            | *LinkedIn*                                                  |
|:------------------:|:-----------------:|:---------------------------------------:|
| Vinicius Monteiro | Product Owner     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/viniciusvasm/ ) |
| Cesar Pelogia | Scrum Master  | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/cesar-augusto-anselmo-pelogia-truyts-94a08a268/ ) |
| Alexandre Jonas | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/alexandre-jonas-de-souza-fonseca-989920181/) |
| Eliézer Lopes     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/eli%C3%A9zer-lopes/) |
| Lucas Henrique | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/lucashenriqueco/) |
| Gabriel Souza | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gabriel-alves-de-souza-5b7747267/) |
| Gustavo Robert     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gustavo-robert/) |
| Vitor Morais       | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/vitor-faria-morais-330b19204/) |

---

## 🛠️ Technologies Used <a id="technologies"></a>

This solution consists of a main application and a support module for tracking project evolution (Burndown).

### 🖥️ Frontend
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

### ⚙️ Backend
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

### 🗄️ Database
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

### 📊 Burndown (Support Module)
[![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)](https://www.java.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![GitHub API](https://img.shields.io/badge/GitHub_API-181717?style=for-the-badge&logo=github&logoColor=white)](https://docs.github.com/en/rest)

### 🐳 DevOps
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Turborepo](https://img.shields.io/badge/Turborepo-EF4444?style=for-the-badge&logo=turborepo&logoColor=white)](https://turbo.build/)

### 💬 Communication
[![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://slack.com/)

---

## 📁 Process Standards <a id="process-standards"></a>

| Document | Description |
|:---------|:------------|
| [General Documentation](docs/DOCUMENTATION.md) | Centralized index of all project standards |
| [Commit and Branch Standards](docs/CONTRIBUTING.md) | Conventional Commits, branch naming and Git hooks |
| [Issue Tracking](docs/ISSUE-TRACKING.md) | How to trace issues, branches and PRs |
| [LGPD](docs/LGPD.md) | LGPD guidelines and data privacy compliance |

---

## 📖 Technical Documentation <a id="technical-documentation"></a>

| Document | Description |
|:---------|:------------|
| [Installation Manual](docs/INSTALLATION_MANUAL.md) | Complete setup guide for deploying the Z application via Docker Compose |
| [User Manual](docs/USER_MANUAL.MD) | Operating guide with focus on interface navigation, APIs, and ETL execution |
| [Prototyping](docs/UI-DESIGN.md) | User flows, screens, and UI components (Figma) |
| [How to Run the Project](docs/GETTING-STARTED.md) | Step-by-step setup, configuration, and local execution guide |
| [Relational database](docs/RELATIONAL-DATABASE.md) | Data model, architecture, and design decisions for PostgreSQL |
| [Non-Relational database](docs/NON-RELATIONAL_DATABASE.md) | MongoDB collections, schema validation, and indexes for ANEEL data |
| [API Patterns](docs/API_PATTERN_FRONTEND.md) | Conventions and best practices for frontend-backend API integration |
| [Components Pattern](docs/COMPONENTS_PATTERN.md)| UI component standardization and reuse guidelines |

---

## 📈 Project Evolution (Burndown) <a id="burndown"></a>

<img src="burndown/src/main/resources/static/burndown.png?v=e528788f8f984fb8ab09a89f6f61fc1c2a432a9f">

For the full guide on local usage, execution and CI, see: [Burndown Documentation](./burndown/README.md)