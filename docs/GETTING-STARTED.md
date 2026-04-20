## :whale: How to Run with Docker <a id="how-to-run-with-docker"></a>

---

[Back to main README](../README.md#date-sprint-backlog)

---

### Prerequisites

- Docker installed and running
- Docker Compose (`docker compose`) enabled

### 1. Configure segmented environment files

This project uses service-specific environment files under the `envs/` directory.

Tracked templates:

- `envs/.env.backend.example`
- `envs/.env.frontend.example`
- `envs/.env.mongo.example`
- `envs/.env.postgres.example`
- `envs/.env.flyway.example`

Create the corresponding `.dev` or `.prod` files according to the environment you want to run.

Minimum values to review:

- `envs/.env.backend.dev`
  - `APP_ENV`
  - `BACKEND_URL`
  - `FRONTEND_URL`
  - `CSV_FILE_PATH`
  - `EMAIL_HASH_SALT`
- `envs/.env.postgres.dev`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_HOST`
  - `POSTGRES_PORT`
- `envs/.env.flyway.dev`
  - `FLYWAY_URL`
  - `FLYWAY_USER`
  - `FLYWAY_PASSWORD`
  - `FLYWAY_PLACEHOLDERS_seed_synthetic_data`

Example backend configuration:

```env
APP_ENV=dev
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
CSV_FILE_PATH=/app/data/indicadores-continuidade-coletivos-2020-2029.csv
EMAIL_HASH_SALT=dev-fixed-salt-change-me
```

Example Flyway configuration:

```env
FLYWAY_URL=jdbc:postgresql://postgres:5432/tecsys
FLYWAY_USER=admin
FLYWAY_PASSWORD=password
FLYWAY_PLACEHOLDERS_seed_synthetic_data=true
```

> Never commit real credentials or production secrets.

### 2. Start the services with profiles

At the project root (`API_6S`):
```bash
docker compose --profile full up --build -d
```

You can start only the services needed for your task:

```bash
# Backend development

docker compose --profile backend up --build -d

# Frontend development

docker compose --profile frontend up --build -d

# Full stack

docker compose --profile full up --build -d

# MongoDB admin tools only

docker compose --profile tools up -d
```

Profile matrix:

- `backend`: `postgres`, `flyway`, `mongo`, `backend`
- `frontend`: backend stack + `frontend`
- `full`: all services
- `tools`: `mongo`, `mongo-express`

Services started:

- `frontend` at `http://localhost:5173`
- `backend` at `http://localhost:8000`
- `postgres` at `localhost:5432`
- `mongo` at `localhost:27017`
- `mongo-express` at `http://localhost:8081` when using `tools`

The following steps run automatically on first startup:

1. PostgreSQL starts and waits for the healthcheck to pass
2. Flyway runs all database migrations in order:
   - `V001` — creates baseline relational objects and view
   - `V002` — creates roles and permissions
   - `V003` — creates triggers
   - `V004` — enables security (RLS + REVOKE + hash documentation)
   - `V005` — inserts base seed data
   - `V006` — inserts synthetic fictional data for development when enabled
   - `V007` — creates Row Level Security policies and operational indexes
3. Backend starts only after PostgreSQL and MongoDB are healthy, and after Flyway completes successfully
4. Frontend starts after the backend is available

### 3. View logs (optional)
```bash
docker compose logs -f
```

Or for a specific service:
```bash
docker compose logs -f backend
```

To view Flyway migration logs specifically:
```bash
docker compose logs flyway
```

### 4. Stop the environment
```bash
docker compose down
```

To also remove database volumes:
```bash
docker compose down -v
```

> Use `docker compose down -v` whenever a migration fails or you need to reset the database to a clean state. This forces Flyway to rerun all migrations from scratch.

### 5. Restart a single service (optional)
```bash
docker compose --profile backend up -d --build backend
```
```bash
docker compose --profile frontend restart frontend
```

### 6. Database structure

The sensitive data database runs on PostgreSQL 15 and is managed exclusively through Flyway migrations located in `database/migrations/`.

The relational flow uses:

- deterministic `EMAIL_HASH` fields (`VARCHAR(64)`) for secure lookup
- `ANONYMIZED_AT` for explicit erasure tracking
- append-only records for published terms and consent history
- RLS on critical tables
- `TB_PASSWORD_RESET` for secure single-use reset tokens

To check the migration history directly in the database:
```sql
SELECT version, description, installed_on, success
FROM flyway_schema_history
ORDER BY installed_rank;
```

For full database design documentation, see [`docs/RELATIONAL-DATABASE.md`](./RELATIONAL-DATABASE.md).
For LGPD compliance documentation, see [`docs/LGPD.md`](./LGPD.md).
