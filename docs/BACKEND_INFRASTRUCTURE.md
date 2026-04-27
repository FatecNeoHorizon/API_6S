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
The core of the application where the **Enterprise Rules** reside. The separation is made as follows:
* **Domain Procedures (`src/control/`)**: Contains the pure business logic and specialized algorithms, such as indicator calculations (DEC/FEC) and energy losses. These functions are unaware of the infrastructure (HTTP, database) and operate directly on domain data.
* **Application Services (`src/services/`)**: Acts as the Use Cases layer. It orchestrates the data flow, coordinating actions between repositories (to fetch/save data) and domain procedures (to execute business logic).

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

---

## 🔄 Lifecycle & Workflow

The application follows a structured lifespan routine upon startup:

1. **Database Connection**: Establishes tunnels to MongoDB and PostgreSQL
2. **Schema Setup**: Initializes collections and performs necessary validations
3. **Data Seeding**: Runs seed.py to ensure core indicators and parameters are present
4. **Route Registration**: Dynamically loads API endpoints

### User Management Flow (`src/api/routes/users.py`)

The user module is implemented with the same layered approach used by the rest of the backend:

- **Route layer**: exposes the REST contract and maps domain exceptions to HTTP responses.
- **Service layer**: centralizes business rules such as uniqueness checks, email normalization, password hashing, and soft delete orchestration.
- **Repository layer**: performs the SQL operations against PostgreSQL.
- **Schema layer**: validates request and response payloads with Pydantic.

#### Exposed endpoints

| Method | Path | Purpose | Main response |
|:---|:---|:---|:---|
| `GET` | `/users/profiles` | Lists available user profiles | `200 OK` with profile list |
| `GET` | `/users/` | Lists users that are not soft deleted | `200 OK` with user list |
| `GET` | `/users/{user_uuid}` | Returns one user by UUID | `200 OK` or `404 Not Found` |
| `POST` | `/users/` | Creates a new user | `201 Created` |
| `PATCH` | `/users/{user_uuid}` | Updates username and profile | `200 OK` or `404/409` |
| `PATCH` | `/users/{user_uuid}/active` | Toggles user active status | `200 OK` or `404 Not Found` |
| `DELETE` | `/users/{user_uuid}` | Performs logical deletion | `204 No Content` or `404 Not Found` |

#### Creation and update flow

1. The frontend sends a validated payload to the API.
2. Pydantic validates required fields and the application returns errors in pt-BR.
3. The service normalizes the email, hashes it with a deterministic salt, and encrypts the original value.
4. The service checks duplicate username and email before persisting.
5. The repository validates the profile UUID against `TB_PROFILE`.
6. The record is stored in `TB_USER` with the minimum data needed for access control and recovery.

#### Security and compliance notes

- Passwords are never stored in plain text.
- E-mail is stored as both hash and encrypted value.
- User listing and retrieval hide deleted records by default.
- Update operations are restricted to username and profile association.
- Deletion is logical, using `DELETED_AT`, preserving traceability and referential integrity.
- Validation failures are returned with localized messages in Brazilian Portuguese.

---

## 🐳 Docker Configuration

| Property | Value |
|:---|:---|
| Base Image | `python:3.11-slim` |
| Working Directory | `/app` |
| Exposed Port | `8000` |
| Execution Command | `fastapi dev` (Optimized for development) |

---

## 📊 Database Context (MongoDB)

The repository manages specific collections for energy grid infrastructure and performance indicators:

- **Network Structure**: `substations`, `distribution_transformers`, `at_network_segments`
- **Indicators**: `distribution_indices` (DEC/FEC), `energy_losses_tariff`
- **Consumer Data**: `consumer_units_pj`, `load_history`

---

## 🚀 Available Scripts

| Command | Action |
|:---|:---|
| `npm run dev` | Starts Uvicorn with `--reload` for development |
| `npm run test` | Executes the test suite using pytest |
| `npm run build` | Placeholder for CI/CD pipeline checks |

## 🔌 API Endpoint Documentation (Developer Reference)

This section documents backend API endpoints for developers, including upload processing flow, validation rules, temporary storage behavior, and load tracking.

### Upload Endpoints (`/upload`)

- `POST /upload/` (status `202 Accepted`)
    - Receives multipart files and starts asynchronous ETL processing.
    - Accepted form fields:
        - `energy_losses` (`.xlsx`)
        - `gbd` (`.zip`, expected to contain a `.gdb` directory)
        - `indicadores_continuidade` (`.csv`)
        - `indicadores_continuidade_limite` (`.csv`)
    - Response payload:
        - `status`: upload execution state initialization (`STARTED`)
        - `arquivos_recebidos`: list of successfully validated file keys
        - `load_ids`: dictionary mapping `file_key -> load_id`

- `GET /upload/status/{load_id}`
    - Returns load execution status from `load_history`.
    - Returns `404` when `load_id` does not exist.
    - When status is `ERROR`, includes `error_message`.

### Processing Flow

1. **Temporary File Management**: To ensure system security and cleanliness, each upload operates within an isolated temporary directory (`tmp/uploads/{upload_id}`). This directory is created at the beginning of the process and **automatically destroyed** at the end, even in case of failures, through an asynchronous context manager.
2. Each provided file is validated and read in memory.
3. Valid files are persisted to disk inside the temporary folder.
4. For `gbd`, ZIP content is extracted into a dedicated directory, and the `.gdb` path is used for ETL input.
5. A `load_history` document is created per accepted file (`file_key`).
6. **Asynchronous Task Scheduling**: A background task is scheduled to execute ETL processing. This allows the API to return an immediate response to the client (`202 Accepted`) while the data processing occurs independently in a dedicated worker.

### Validation Rules

- Extension validation per file key.
- MIME validation using content-based detection (`python-magic`), not only filename metadata.
- File size validation with configurable limit:
    - `max_upload_size_mb` (default: `500`)
- Empty upload protection:
    - If no file is sent, request is rejected.
- Dynamic file key support:
    - Pattern `^indicadores_continuidade_\d{4}_\d{4}$` is accepted as CSV input.

### ZIP/GBD Security and Integrity

- ZIP traversal protection:
    - Rejects entries containing `..` or absolute paths during extraction.
- GBD content integrity:
    - Rejects ZIP files that do not include a directory with `.gdb` suffix.

### Error Contract

- Validation failures are aggregated and returned as HTTP `422` with a list in `detail`.
- Typical validation errors include:
    - Unsupported file type for `file_key`
    - Invalid extension
    - Invalid detected MIME type
    - File size limit exceeded
    - Invalid ZIP/GBD structure

### Configuration Parameters

Upload behavior is controlled by backend settings:

- `max_upload_size_mb`: maximum accepted upload size per file
- `tmp_upload_path`: base path for temporary upload folders

### Operational Notes for Developers

- The current asynchronous worker function is a placeholder and marks load status as `SUCCESS` after scheduling flow execution.
- Load tracking is stored in `load_history`, enabling status polling independent of request lifecycle.
- Upload temporary folders are managed by context manager and cleaned up automatically.

### User Data Storage Context

The user CRUD implemented in this repository uses PostgreSQL as the sensitive-data store. The relevant tables are:

- `TB_USER`: credentials, profile association, activation flag, soft delete metadata, and audit timestamps.
- `TB_PROFILE`: profile catalog used to authorize user roles.

The module does not expose raw email values in responses. User-facing payloads return only the fields required by the frontend and operational flows.

---

## Logging

The application uses a structured logging system based on `structlog` and `TimedRotatingFileHandler`.

Full documentation: [`docs/LOGGING.md`](../docs/LOGGING.md)

---

*Last updated: 04/26/2026*