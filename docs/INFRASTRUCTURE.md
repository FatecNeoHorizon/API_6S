# 🚀 Backend Infrastructure Documentation

This document describes the core API for energy monitoring and indicator forecasting, built with **FastAPI** and structured with **Clean Architecture** to ensure scalability, high cohesion, and low coupling.

## 🏗️ System Architecture & Design Patterns

The sections below detail the backend architectural decisions, emphasizing the separation of domain logic from external infrastructure concerns.


```text
apps/backend/
├── main.py                # FastAPI entry point & Lifespan management
├── Dockerfile             # Container configuration (Python 3.11-slim)
├── package.json           # Development and automation scripts
├── requirements.txt       # Python dependencies
├── readme.md              # Local documentation
├── data/                  # Local data storage/volumes
└── src/                   # Main source code
    ├── api/               # REST Interface Layer
    │   ├── routes/        # API Endpoints
    │   └── schemas/       # Pydantic Models (DTOs)
    ├── config/            # Settings & Middlewares
    ├── control/           # Business Logic & Procedures
    ├── database/          # Persistence Layer
    │   ├── connection.py  # Driver configurations
    │   ├── setup.py       # DB Initialization
    │   └── collections/   # MongoDB Collection definitions
    ├── etl/               # Data Pipeline (Extract, Transform, Load)
    ├── model/             # Entities & Data Models
    │   └── seed.py        # Initial data seeding
    ├── repositories/      # Data Access Abstraction
    ├── services/          # Application Services
    └── utils/             # Helper functions (filters, etc.)
```


---

## 🏛️ Layered Architectural Decomposition

### 1. Transport & Interface Layer (`src/api/`)
This layer acts as the **Entry Point** for the system, responsible for the HTTP communication protocol.
* **Routing Handlers:** Implements RESTful endpoints using FastAPI, managing request/response lifecycles and status codes.
* **Data Transfer Objects (DTOs/Schemas):** Utilizes Pydantic for strict type validation and data serialization. This ensures that internal **Domain Entities** are never directly exposed to the client, preventing unintended side effects and over-posting.

### 2. Business Logic & Domain Procedures (`src/control/` & `src/services/`)
The core of the application where the **Enterprise Rules** reside.
* **Domain Procedures:** Contains specialized logic for power system calculations (e.g., DEC/FEC indices and energy loss algorithms). These are "pure" functions or procedures that operate on domain data.
* **Application Services:** Acts as an orchestrator (Use Case layer). It coordinates the flow of data between the repositories and the logic procedures, managing the high-level application state.

### 3. Data Access & Persistence Abstraction (`src/repositories/`)
Implements the **Repository Pattern** to decouple the business logic from the specific database implementation (MongoDB/PostgreSQL).
* By using this abstraction, the service layer remains agnostic to the underlying storage engine, allowing for easier unit testing through Mocking and ensuring the flexibility to swap database providers without rewriting business rules.

### 4. Persistence Layer & Schema Definition (`src/database/` & `src/model/`)
* **Infrastructure Models:** Defines the physical data structures and entities.
* **Connection Management:** Handles connection pooling, session lifecycles, and database-specific configurations (Collections for NoSQL and Tables for Relational).

### 5. Data Engineering & Pipeline Processing (`src/etl/`)
Dedicated to the **ETL (Extract, Transform, Load)** lifecycle for large datasets (e.g., DECFEC files).
* **Extraction:** Logic for sourcing raw data from external providers.
* **Transformation Engine:** Leverages **Pandas** for high-performance data manipulation, normalization, and cleaning.
* **Load Orchestration:** Manages the ingestion of processed time-series data into the MongoDB clusters.

---

## 🛠️ Technology Stack

| Technology | Version | Purpose |
|:---|:---:|:---|
| FastAPI | 0.135.2 | High-performance asynchronous web framework |
| Pydantic | 2.12.5 | Data validation and DTO management |
| PyMongo | 4.16.0 | MongoDB integration |
| psycopg2-binary | latest | PostgreSQL connectivity |
| Pandas | latest | Data processing for ETL flows |
| Python | 3.11 | Base programming language |

## 🔄 Lifecycle & Workflow

The application follows a structured lifespan routine upon startup:

1. **Database Connection**: Establishes tunnels to MongoDB and PostgreSQL
2. **Schema Setup**: Initializes collections and performs necessary validations
3. **Data Seeding**: Runs seed.py to ensure core indicators and parameters are present
4. **Route Registration**: Dynamically loads API endpoints

## 🐳 Docker Configuration

| Property | Value |
|:---|:---|
| Base Image | `python:3.11-slim` |
| Working Directory | `/app` |
| Exposed Port | `8000` |
| Execution Command | `fastapi dev` (Optimized for development) |

## 📊 Database Context (MongoDB)

The repository manages specific collections for energy grid infrastructure and performance indicators:

- **Network Structure**: `substations`, `distribution_transformers`, `at_network_segments`
- **Indicators**: `distribution_indices` (DEC/FEC), `energy_losses_tariff`
- **Consumer Data**: `consumer_units_pj`, `load_history`

## 🚀 Available Scripts

| Command | Action |
|:---|:---|
| `npm run dev` | Starts Uvicorn with `--reload` for development |
| `npm run test` | Executes the test suite using pytest |
| `npm run build` | Placeholder for CI/CD pipeline checks |

---

*Last updated: 04/17/2026*