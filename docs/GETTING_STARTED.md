## :whale: How to Run with Docker <a id="how-to-run-with-docker"></a>

---

[Back to main README](../README.md#date-sprint-backlog)

---

### Prerequisites

- Docker installed and running
- Docker Compose (`docker compose`) enabled

### 1. Create the environment file

At the project root, create a `.env` file with the variables used in `docker-compose.yml`.

Copy the example file and fill in the values:
```bash
cp .env.example .env
```

Minimum example:
```env
# PostgreSQL
POSTGRES_DB=zeus
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_strong_password
POSTGRES_HOST=postgres
POSTGRES_PORT=

# MongoDB
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=your_strong_password

# Mongo Express
MONGO_HOST=
MONGO_PORT=
MONGO_USER=
MONGO_PASSWORD=
MONGO_DB_NAME=

# Flyway
FLYWAY_URL=jdbc:postgresql://postgres:5432/zeus
FLYWAY_USER=postgres
FLYWAY_PASSWORD=your_strong_password

# Keycloak
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=your_strong_password
KEYCLOAK_REALM=zeus
KEYCLOAK_CLIENT_ID=zeus-app
KEYCLOAK_CLIENT_SECRET=

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
KEYCLOAK_URL=http://localhost:8080
```

> Never commit the `.env` file. It is already listed in `.gitignore`.

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

# Full stack (includes Keycloak)
docker compose --profile full up --build -d

# Keycloak only (identity server + app network)
docker compose --profile auth up -d

# MongoDB admin tools only
docker compose --profile tools up -d
```

Profile matrix:

| Profile | Services |
|:---|:---|
| `backend` | `postgres`, `flyway`, `mongo`, `backend` |
| `frontend` | backend stack + `frontend` |
| `auth` | `keycloak` |
| `full` | all services |
| `tools` | `mongo`, `mongo-express`, `pgadmin` |

Services started:

- `frontend` at `http://localhost:5173`
- `backend` at `http://localhost:8000`
- `keycloak` at `http://localhost:8180`
- `postgres` at `localhost:5432`
- `mongo` at `localhost:27017`

For `tools`, `mongo-express` is exposed at `http://localhost:8081`.

The following steps run automatically on first startup:

1. PostgreSQL starts and waits for the healthcheck to pass
2. Flyway runs all database migrations in order:
   - `V001` — creates all tables
   - `V002` — creates roles and permissions
   - `V003` — creates triggers
   - `V004` — enables security (RLS + REVOKE)
   - `V005` — inserts base seed data
   - `V006` — inserts synthetic fictional data for development
   - `V007` — creates Row Level Security policies
3. Backend starts only after PostgreSQL and MongoDB are healthy, and after Flyway completes successfully
4. Frontend starts after the backend is available

### 3. Configure Keycloak (first run only)

Keycloak runs with the `auth` or `full` profile and is available at `http://localhost:8180`.

On first startup, the `zeus` realm is imported automatically from `keycloak/realm-zeus.json`. It includes:
- The `zeus-app` client (public, PKCE-only, redirect to `http://localhost:5173/*`)
- Realm roles: `ADMIN`, `ANALYST`, `VIEWER`

The only manual step is creating users and assigning roles:

1. Access `http://localhost:8180/admin` with the credentials in `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`
2. Select the `zeus` realm
3. Go to **Users → Add user**, create the user, then go to **Role Mapping** and assign the appropriate role

> For the full authentication and authorization flow, see [AUTH_ARCHITECTURE.md](AUTH_ARCHITECTURE.md).

### 4. View logs (optional)
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

### 5. Stop the environment
```bash
docker compose down
```

To also remove database volumes:
```bash
docker compose down -v
```

> Use `docker compose down -v` whenever a migration fails or you need to reset the database to a clean state. This forces Flyway to rerun all migrations from scratch.

### 6. Restart a single service (optional)
```bash
docker compose --profile backend up -d --build backend
```
```bash
docker compose --profile frontend restart frontend
```

### 7. Database structure

The sensitive data database runs on PostgreSQL 15 and is managed exclusively through Flyway migrations located in `database/migrations/`.

**Never edit a migration file that has already been executed.** Flyway stores a checksum for each migration and will refuse to proceed if a previously applied file is modified. To make changes, always create a new migration file with the next version number.

To check the migration history directly in the database:
```sql
SELECT version, description, installed_on, success
FROM flyway_schema_history
ORDER BY installed_rank;
```

For full database design documentation, see [`docs/database.md`](./database.md).
For LGPD compliance documentation, see [`docs/lgpd.md`](./lgpd.md).