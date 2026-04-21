# Installation Manual - Zeus Project

Guide to prepare the environment, configure variables, and deploy the Zeus application via Docker Compose.

## Contents

- Prerequisites and component overview
- segmented `.env` files configuration and CSV data setup
- Docker installation steps
- Validation and troubleshooting

**Documentation sources consulted:** Main README, documentation in `docs/`, `docker-compose.yml`, backend/frontend files, SQL migrations, and project folder structure.

---

## 1. Installation Overview

The project is structured as a **monorepo** with:
- FastAPI Backend
- React/Vite Frontend
- PostgreSQL relational database
- MongoDB non-relational database
- Flyway for migrations
- Mongo Express for database inspection

The main installation method is via the `docker-compose.yml` file in the project root.

### 1.1 Components to Be Started

| Service | Function | Default Port |
|---------|----------|------------------|
| **postgres** | Storage of sensitive data and LGPD tables | 5432 |
| **flyway** | Automatic execution of SQL migrations | --- |
| **mongo** | Storage of ANEEL/BDGD public dataset | 27017 |
| **mongo-express** | MongoDB administration web interface | 8081 |
| **backend** | FastAPI and ETL trigger | 8000 |
| **frontend** | React/Vite application | 5173 |

### 1.2 Compose Profiles

| Profile | Services started | Use case |
|---------|------------------|----------|
| **backend** | `postgres`, `flyway`, `mongo`, `backend` | Backend and ETL development |
| **frontend** | `postgres`, `flyway`, `mongo`, `backend`, `frontend` | UI development with complete backend stack |
| **full** | All services | Full integration environment |
| **tools** | `mongo`, `mongo-express` | MongoDB administration interface |

---

## 2. Prerequisites

Before starting, ensure your machine has sufficient resources to run multiple containers and handle large data loads. The `docs/SPRINT1.md` file highlights that the CSV file `indicadores-continuidade-coletivos-2020-2029.csv` contains **5 million rows**, requiring adequate memory allocation for MongoDB and backend processing.

- Docker Desktop or Docker Engine with Docker Compose enabled
- Terminal access to the `API_6S` root directory
- Permission to open ports **5432, 5173, 8000, 8081, and 27017**
- CSV indicators file available for ETL (if you plan to populate the `distribution_indices` collection)

---

## 3. Minimum Expected Structure

After extracting the ZIP file, the project root must contain at least these directories:
- `apps/`
- `database/`
- `docs/`
- `docker-compose.yml`
- `envs/`

The backend is located in `apps/backend` and the frontend in `apps/frontend`.

### 3.1 Data Folder

The backend service mounts the local folder `./data` to `/app/data` inside the container. The `CSV_FILE_PATH` value must be set in `envs/.env.backend.{dev|prod}`.

**Important:** Place the CSV file with this name inside the `data` folder at the project root before running the ETL.

---

## 4. Segmented `.env` File Configuration

The project uses service-specific environment files in the repository root, with a version per environment (`dev` and `prod`) and a tracked template (`example`).

> **⚠️ Security:** Do not include real credentials in public repositories.

### 4.1 Files by Service

| Service | Dev file | Prod file | Tracked template |
|-------|-----------|-----------|------------------|
| **Backend (FastAPI)** | `envs/.env.backend.dev` | `envs/.env.backend.prod` | `envs/.env.backend.example` |
| **Frontend (Vite)** | `envs/.env.frontend.dev` | `envs/.env.frontend.prod` | `envs/.env.frontend.example` |
| **MongoDB** | `envs/.env.mongo.dev` | `envs/.env.mongo.prod` | `envs/.env.mongo.example` |
| **PostgreSQL** | `envs/.env.postgres.dev` | `envs/.env.postgres.prod` | `envs/.env.postgres.example` |
| **Flyway** | `envs/.env.flyway.dev` | `envs/.env.flyway.prod` | `envs/.env.flyway.example` |

### 4.2 Main Variables

| Block | Variables | Note |
|-------|-----------|------|
| **PostgreSQL** | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT` | Used by database and Flyway |
| **MongoDB** | `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`, `MONGO_HOST`, `MONGO_PORT`, `MONGO_USER`, `MONGO_PASSWORD`, `MONGO_DB_NAME` | Used by MongoDB and backend |
| **Backend application** | `APP_ENV`, `FRONTEND_URL`, `BACKEND_URL`, `CSV_FILE_PATH`, `EMAIL_HASH_SALT` | `EMAIL_HASH_SALT` is required for deterministic SHA-256 email hashing |
| **Flyway** | `FLYWAY_URL`, `FLYWAY_USER`, `FLYWAY_PASSWORD`, `FLYWAY_PLACEHOLDERS_seed_synthetic_data` | PostgreSQL migrations and control of synthetic dev seed |

### 4.3 Fill-in Example

Below is an illustrative `dev` setup. Adjust usernames, passwords, hosts and database names according to your environment:

In `envs/.env.postgres.dev`:

POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=tecsys
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

In `envs/.env.mongo.dev`:

MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_USER=admin
MONGO_PASSWORD=password
MONGO_DB_NAME=tecsys

In `envs/.env.backend.dev`:

APP_ENV=dev
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
CSV_FILE_PATH=/app/data/indicadores-continuidade-coletivos-2020-2029.csv
EMAIL_HASH_SALT=dev-fixed-salt-change-me
MONGO_MAX_POOL_SIZE=10
MONGO_SERVER_SELECTION_TIMEOUT_MS=120000
MONGO_CONNECT_TIMEOUT_MS=10000

In `envs/.env.frontend.dev`:

VITE_API_URL=http://localhost:8000

In `envs/.env.flyway.dev`:

FLYWAY_URL=jdbc:postgresql://postgres:5432/tecsys
FLYWAY_USER=admin
FLYWAY_PASSWORD=password
FLYWAY_PLACEHOLDERS_seed_synthetic_data=true

> **Environment selection note:** Docker Compose selects files with `APP_ENV` (`dev` by default), e.g. `envs/.env.backend.${APP_ENV:-dev}`.

---

## 5. Installation with Docker Compose

### 5.1 Standard Flow

1. Review the service-specific environment files for the target environment
2. Ensure the `data` folder exists and, if necessary, place the CSV indicators file in it
3. Execute:
   ```bash
   docker compose --profile full up --build
   ```
4. Wait for image creation, PostgreSQL and MongoDB startup, and Flyway migration execution
5. After completion, validate the services at the URLs mentioned in the next section

### 5.2 What Happens During Startup

Compose executes the following sequence (profile `full`):

1. Starts PostgreSQL and waits for the healthcheck
2. Executes SQL migrations via Flyway
3. Starts MongoDB
4. Creates the backend container with FastAPI/Uvicorn only after PostgreSQL and MongoDB are healthy, and Flyway has completed successfully
5. Starts the Vite frontend

To run only part of the stack:

```bash
# Backend focused flow
docker compose --profile backend up --build

# Frontend focused flow
docker compose --profile frontend up --build

# Mongo Express only
docker compose --profile tools up
```

The backend mounts the data folder and is ready to process the CSV via endpoint.

---

## 6. Post-Installation Validation

Once the containers are active, use the table below to verify that the installation is intact:

| Verification | URL/Command | Expected Result |
|--------|-------------|-----------------|
| Frontend | `http://localhost:5173` | React interface loading the Zeus application |
| Backend | `http://localhost:8000` | Simple JSON response from root route |
| Swagger | `http://localhost:8000/docs` | FastAPI automatic documentation |
| Mongo Express | `http://localhost:8081` | MongoDB web panel |
| Containers | `docker compose --profile full ps` | Services with `running`/`healthy` status for the selected profile |

### 6.1 Relational Validation

To confirm the relational structure after startup, check:

- `TB_PASSWORD_RESET` exists
- `ANONYMIZED_AT` exists in `TB_USER`
- `EMAIL_HASH` is `VARCHAR(64)` in `TB_USER` and `TB_AUTH_ATTEMPT`
- `V_PENDING_CONSENT` exists
- `TB_POLICY_VERSION`, `TB_POLICY_CLAUSE`, and `TB_CONSENT_LOG` are append-only

---

## 7. Local Installation Without Docker (Optional)

Although the project's main flow is Docker-oriented, it is possible to install applications manually for development. This option requires separate configuration of Python, Node.js, PostgreSQL, and MongoDB.

- **Backend:** Python 3.11, install `requirements.txt` and start with Uvicorn/FastAPI in the `apps/backend` directory
- **Frontend:** Node.js 20, run `npm install` in `apps/frontend` and start with `npm run dev`
- **Databases:** Provision PostgreSQL and MongoDB manually, and apply migrations present in `database/migrations`
- **Variables:** Adjust environment variables to point to local services

---

## 8. Common Issues and Quick Fixes

| Symptom | Likely Cause | Suggested Action |
|-----------|-------------|-------------------|
| Frontend doesn't load | Frontend container didn't start or port 5173 is occupied | Check logs with `docker compose logs frontend` and free the port |
| Swagger unavailable | Backend didn't start or crashed due to connection error | Check backend logs and credentials in environment files |
| Migration fails | Wrong PostgreSQL/Flyway parameters | Review `envs/.env.postgres.*` and `envs/.env.flyway.*` |
| Synthetic seed should not run in production | Flyway placeholder still enabled | Set `FLYWAY_PLACEHOLDERS_seed_synthetic_data=false` in production |
| Hash lookup behavior differs between environments | Missing or inconsistent `EMAIL_HASH_SALT` | Align `EMAIL_HASH_SALT` in the backend environment file |
| CSV processing fails | File not found or name mismatch | Confirm file in `data` folder and `CSV_FILE_PATH` |
| Mongo connection error | Incompatible MongoDB username/password | Review `MONGO_*` in `envs/.env.mongo.*` and `envs/.env.backend.*` |

---

## 9. Final Installation Checklist

- [ ] Service-specific files (`.env.*.dev` or `.env.*.prod`) have been created and filled
- [ ] A profile-based command (for example `docker compose --profile full up --build`) completed without critical errors
- [ ] Ports 5173, 8000, 8081, 5432, and 27017 are accessible
- [ ] Backend Swagger opens correctly
- [ ] The relational schema contains the expected security and LGPD support fields
- [ ] The frontend opens and allows navigation to the dashboard

---

**Last updated:** April 20, 2026
