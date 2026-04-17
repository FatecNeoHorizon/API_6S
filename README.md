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
  <a href="#schedule">📅 Schedule</a> •
  <a href="#team-members">👥 Team Members</a> •
  <a href="#technologies">🛠️ Technologies</a> •
  <a href="#process-standards">📁 Process Standards</a> •
  <a href="#technical-documentation">📖 Technical Documentation</a>
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
| <a id="RF01">RF01</a> | **ETL Pipeline and Data Versioning** | The system must execute the extraction, transformation and loading (ETL) process for public ANEEL/BDGD data, with log records for each stage, batch version control, data origin traceability and persistence of processed data for analytical consumption across the platform. Each load must have a unique version identifier, execution date/time and processing status. |
| <a id="RF02">RF02</a> | **Distribution Network Structure Dashboard** | The system must provide interactive dashboards and reports containing geographic, electrical and structural information about the power distribution network, including, when applicable, substations, transformers, network segments, circuits and electrical sets, enabling the user to explore the infrastructure mesh and understand the physical distribution of assets by region. |
| <a id="RF03">RF03</a> | **Continuity and Loss Indicators Dashboard** | The system must display electrical network indicators, including DEC, FEC and energy losses, with filtering by time period and analytical scope. The solution must support time series visualization, summary indicators, regulatory status and analytical tables, providing the user with a consolidated view of service continuity and loss behavior in the network. |
| <a id="RF04">RF04</a> | **Physical TAM Calculation** | The system must calculate and display the physical TAM (Total Addressable Market) for sensor installation in the electrical grid, representing the maximum number of technically monitorable points, without considering commercial, financial or operational restrictions. In the first version, the calculation must use the electrical set as the base monitoring unit, consolidating results by utility and displaying the total value together with a summarized calculation memory and the reference batch used. |
| <a id="RF05">RF05</a> | **Machine Learning-Based Indicator Forecasting** | The system must allow the training, execution and versioning of Machine Learning models to forecast future electrical network indicators, initially focused on DEC and FEC. The solution must record the training dataset, variables used, training period, model version, generated forecasts and training parameters, enabling future network behavior analysis and supporting technical and commercial decision-making. |
| <a id="RF06">RF06</a> | **Analytical Criticality Ranking and Sorting** | The system must generate an analytical ranking of utilities or regions based on power continuity indicators, using DEC and FEC as primary variables and losses as a complementary prioritization variable. The solution must classify each record by criticality level, allow sorting from most critical to least critical, and offer alternative ordering by DEC, FEC or losses, without requiring regression or Machine Learning in the first version. |
| <a id="RF07">RF07</a> | **User, Profile, Login and First Access Management** | The system must allow user registration, listing, editing, inactivation and management with distinct profiles, in addition to providing login, first access flow, initial password setup and mandatory acceptance of the current legal terms. The registration process must store only the minimum necessary personal data and support profiles such as Administrator, Analyst and Viewer, with the permission model prepared for future expansion. |
| <a id="RF08">RF08</a> | **SAM Calculation** | The system must calculate and display the SAM (Serviceable Available Market) from the physical TAM by applying technical, regulatory and operational feasibility criteria that reduce the total number of possible points to the number of points realistically serviceable by Tecsys solutions. The calculation must consider rules such as infrastructure compatibility, technical network indicators, operational constraints and business filters, with traceability of the applied logic. |
| <a id="RF09">RF09</a> | **Geographic Visualization and Analytical Heatmap** | The system must provide geographic analytical visualization, including heatmaps by region or electrical set, allowing the highlighting of priority areas based on indicators such as DEC, FEC, losses or consolidated criticality. The interface must support dynamic filters by indicator and network type while preserving readability and performance. |
| <a id="RF10">RF10</a> | **LGPD Compliance and Consent Management** | The system must implement LGPD compliance mechanisms for personal data, including data minimization, explicit acceptance of terms and privacy policies, legal document versioning, immutable consent history recording, action traceability, retention policy, logical deletion with anonymization when applicable, and strict separation between public and sensitive data. The system must also maintain a foundation for the future implementation of data subject rights provided by law. |
| <a id="RF11">RF11</a> | **Dual-Database Storage Architecture** | The system must use a storage architecture separated by data purpose, employing a relational database for sensitive data and a non-relational database for public operational data. Personal data, credentials, consents and sensitive audit logs must be stored in PostgreSQL, while public ANEEL/BDGD data and analytical collections must be stored in MongoDB, in order to reduce exposure risk, simplify LGPD compliance and support large-scale ingestion and geospatial data handling. |
| <a id="RF12">RF12</a> | **Terms, Policies and Acceptance History Management** | The system must allow the creation, editing, versioning, publication, inactivation and consultation of terms of use and privacy policies, maintaining the full content of published versions and ensuring that the first access flow always displays the most recent active versions. Acceptance must be recorded with timestamp, user and accepted version, preserving an immutable history for audit and proof of consent. |

<br>

### Non-Functional Requirements

| ID | Requirement | Description |
|:---|:---|:---|
| <a id="RNF01">RNF01</a> | **Database Query Performance** | The system must ensure adequate performance for critical queries executed against both PostgreSQL and MongoDB, adopting pagination, indexing and query strategies compatible with the expected workload. Analytical and administrative queries must support fluid navigation, avoiding noticeable freezing during filtering, rankings, dashboards and list views. |
| <a id="RNF02">RNF02</a> | **Application Startup and Stability** | The web application must start correctly, remain stable during continuous use sessions and support navigation across pages, filters, dashboards and administrative flows without unexpected failures, freezes or improper loss of state. |
| <a id="RNF03">RNF03</a> | **Responsiveness and Compatibility** | The interface must be responsive and compatible with modern browsers, ensuring a good user experience across different resolutions and access contexts, with consistent behavior in tables, filters, dashboards, modals and forms. |
| <a id="RNF04">RNF04</a> | **ML Model Performance Documentation and Validation** | Every Machine Learning model used by the system must have its performance documented with metrics compatible with the problem type. For numerical forecasting and time series tasks, metrics such as RMSE, MAE or equivalent must be used; for classification, metrics such as F1-Score; and for clustering, metrics such as Silhouette Score, when applicable. The system must keep records of model version, training dataset, variables used, analyzed period and obtained results, enabling technical review and reliability validation. |
| <a id="RNF05">RNF05</a> | **Post-Load Consistency and Traceability** | Whenever a new ETL load is processed, the system must automatically recalculate the dependent indicators and analytical structures, including DEC, FEC, losses and correlated aggregations, ensuring consistency between the data shown in the interface and the latest validated batch. The application must display the date/time of the last load and the batch version identifier used in the analysis. |
| <a id="RNF06">RNF06</a> | **Security and Protection of Sensitive Data** | The system must protect credentials, consents and other personal data through appropriate security mechanisms, including secure password hashing, protection or encryption of sensitive fields, masking of data in logs when necessary, controlled access to administrative information and strict separation between development and production environments. |
| <a id="RNF07">RNF07</a> | **Auditability and Immutability of Sensitive Records** | Audit and consent records must be preserved in a traceable and tamper-resistant way, maintaining append-only or equivalent history for sensitive events, especially login, acceptance of terms, administrative actions and compliance-related events. The system must allow future proof of who performed a certain action, when it happened and which entity was affected. |
| <a id="RNF08">RNF08</a> | **Support for Geospatial and Large-Volume Data** | The solution must support the storage and querying of large volumes of semi-structured and geospatial BDGD/ANEEL data, using MongoDB as the main non-relational database for these datasets, with ingestion, indexing and querying capacity compatible with the needs of dashboards, heatmaps and analytical aggregations across the project. |

</details>

---

## 📦 Product Backlog <a id="product-backlog"></a>

| ID | Priority | Title | User Story | Estimate | Sprint | Related Requirements |
|:---|:---|:---|:---|:---:|:---:|:---|
| US01 | Highest | [Network Structure Reports](https://github.com/FatecNeoHorizon/API_6S/wiki/US01-%E2%80%94-Network-Structure-Reports-TO-DO) | As a data analyst, I want to access structural reports of distribution networks, to identify geographic, electrical and structural characteristics of the monitored infrastructure. | TBD | 01 | RF01, RF02, RNF01, RNF02, RNF03 |
| US02 | Highest | [Quality Indicators Dashboard](https://github.com/FatecNeoHorizon/API_6S/wiki/US02-%E2%80%94-Quality-Indicators-Dashboard-TO-DO) | As a data analyst, I want the system to expose quality data (DEC, FEC, losses), to evaluate electrical grid performance by region and period. | TBD | 01 | RF01, RF03, RNF01, RNF02, RNF03, RNF05 |
| US03 | High | [Physical TAM Calculation](https://github.com/FatecNeoHorizon/API_6S/wiki/US03-%E2%80%94-Physical-TAM-Calculation) | As a commercial analyst, I want to calculate the physical TAM for sensor installation, to size the maximum universe of monitorable points in Brazil. | TBD | 02 | RF04, RF01, RNF01, RNF05 |
| US04 | High | [Criticality Ranking](https://github.com/FatecNeoHorizon/API_6S/wiki/US04-%E2%80%94-Criticality-Ranking) | As a data analyst, I want a ranking of regions by energy losses, to identify the most critical areas and support technical and commercial decisions. | TBD | 02 | RF03, RF06, RF01, RNF01, RNF05 |
| US05 | High | [Login and First Access](https://github.com/FatecNeoHorizon/API_6S/wiki/US05-%E2%80%90-Login-and-First-Access-%F0%9F%9F%A0) | As a registered user, I want to log into the platform and complete my first access flow, so that I can securely activate my account and access the system. | TBD | 02 | RF07, RF10, RF11, RF12, RNF02, RNF06, RNF07 |
| US06 | High | [User CRUD Management](https://github.com/FatecNeoHorizon/API_6S/wiki/US06-%E2%80%94-User-CRUD-Management) | As an administrator, I want to create, edit, list and manage users, so that I can control who has access to the platform and maintain user records in compliance with LGPD principles. | TBD | 02 | RF07, RF10, RF11, RNF02, RNF06, RNF07 |
| US07 | High | [Terms and Consent Management](https://github.com/FatecNeoHorizon/API_6S/wiki/US07-%E2%80%94-Terms-and-Consent-Management) | As an administrator, I want to create and manage terms of use and privacy policies, so that users always accept the active versions required by the platform and the system maintains auditable consent records. | TBD | 02 | RF07, RF10, RF12, RNF06, RNF07 |
| US08 | High | [LGPD Audit Base](https://github.com/FatecNeoHorizon/API_6S/wiki/US08-%E2%80%94-LGPD-Audit-Base) | As an administrator, I want the system to register essential consent, access and administrative events, so that the platform starts complying with LGPD traceability and audit requirements. | TBD | 02 | RF10, RF11, RF12, RNF06, RNF07 |
| US09 | High | [ML Model Validation](https://github.com/FatecNeoHorizon/API_6S/wiki/US09-%E2%80%94-ML-Model-Validation) | As a data analyst, I want ML models to have documented performance and validated metrics, to ensure the reliability of results generated by the system. | TBD | 02 | RF05, RNF04, RF01, RNF05 |
| US10 | Medium | SAM Indicator | As a commercial analyst, I want a SAM indicator, to identify the accessible market for the product by region based on technical and regulatory criteria. | TBD | 03 | RF08, RF04, RF01, RNF01, RNF05 |
| US11 | Medium | Geographic Heatmap | As a commercial analyst, I want a geographic visualization (heatmap), to visually identify priority regions for commercial outreach. | TBD | 03 | RF09, RF03, RF06, RF01, RNF01, RNF03, RNF08 |
| US12 | Medium | LGPD Transparency and Control | As a user, I want control and transparency over my personal data (LGPD), to ensure my information is handled securely and in accordance with the law. | TBD | 03 | RF07, RF10, RF11, RF12, RNF06, RNF07 |
| US13 | Medium | Automatic Recalculation | As a data analyst, I want indicators to be automatically recalculated after each new data load, to ensure analyses always reflect the most up-to-date information. | TBD | 03 | RF01, RNF05, RNF01, RNF02 |

---

## 🗓️ Sprint Backlog <a id="sprint-backlog"></a>

<details>
<summary><b>Sprint 1</b></summary>

[View Sprint 1 documentation](docs/SPRINT1.md)
</details>

<details>
<summary><b>Sprint 2</b></summary>

[View Sprint 2 documentation](docs/SPRINT2.md)
</details>

<details>
<summary><b>Sprint 3</b></summary>

[View Sprint 3 documentation](docs/SPRINT3.md)
</details>

---

## 📅 Schedule <a id="schedule"></a>

| Sprint | Name | Start Date | End Date | Status |
|:---:|:---:|:---:|:---:|:---:|
| --- | KickOff                   | Mar 02 | Mar 06 | Ok |
| --- | Planning                  | Mar 09 | Mar 13 | Ok |
|  1  | Sprint 1                  | Mar 16 | Apr 05 | Ok |
|  2  | Sprint review / Planning  | Apr 06 | Apr 10 | Ok |
|  3  | Sprint 2                  | Apr 13 | May 03 |    |
|  4  | Sprint review / Planning  | May 04 | May 08 |    |
|  5  | Sprint 3                  | May 11 | May 31 |    |
|  6  | Sprint review             | Jun 01 | Jun 05 |    |
|  7  | Solutions Fair            | Jun 11 |       |    |
|  8  | TG Presentations          | Jun 15 | Jun 19 |    |

---

## 👥 Team Members <a id="team-members"></a>

| *Name*                   | *Function*            | *LinkedIn*                                                  |
|:------------------:|:-----------------:|:---------------------------------------:|
| Ruth da Silva Mira | Product Owner     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/ruth-mira/) |
| Cesar Pelogia | Scrum Master  | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/cesar-augusto-anselmo-pelogia-truyts-94a08a268/ ) |
| Alexandre Jonas | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/alexandre-jonas-de-souza-fonseca-989920181/) |
| Eliézer Lopes     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/eli%C3%A9zer-lopes/) |
| Gabriel Souza | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gabriel-alves-de-souza-5b7747267/) |
| Gustavo Robert     | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](http://www.linkedin.com/in/gustavo-robert/) |
| Lucas Henrique | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/lucashenriqueco/) |
| Vinicius Monteiro | Developer     | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin&labelColor=blue)](https://www.linkedin.com/in/viniciusvasm/ ) |
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
