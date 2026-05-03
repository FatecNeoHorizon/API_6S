# 📋 Logging System

## 📦 Stack

| Component | Role |
|---|---|
| `structlog` | Structured log creation with context binding |
| `stdlib logging` | Root logger and handler management |
| `TimedRotatingFileHandler` | Daily file rotation with 30-day retention |
| `gz_rotator` | Automatic compression of rotated files to `.gz` |

---

## 🔀 Request Flow

```
HTTP request arrives
        ↓
LoggingMiddleware (src/config/logging_middleware.py)
  - Generates request_id (UUID v4)
  - Binds request_id, method, path, user_id to structlog context
  - Logs request_started
        ↓
Route handler / Service
  - Calls log.info(EVENT_CONSTANT, ...) with operational metadata only
        ↓
structlog processors
  - merge_contextvars  → merges request_id, method, path, user_id
  - add_log_level      → adds "level" field
  - add_logger_name    → adds "logger" field
  - TimeStamper        → adds "timestamp" in ISO 8601
  - JSONRenderer       → serializes to a single JSON line
        ↓
stdlib root logger
  - StreamHandler      → writes to container stdout
  - TimedRotatingFileHandler → writes to logs/app.log
        ↓
LoggingMiddleware
  - Logs request_finished with status_code and duration_ms
  - Calls clear_contextvars()
```

---

## 📁 File Locations

| Path | Description |
|---|---|
| `logs/app.log` | Current active log file |
| `logs/app.log.YYYY-MM-DD_HH-MM-SS.gz` | Rotated and compressed files |

The `logs/` directory is mapped as a Docker volume (`./logs:/app/logs`) and persists across container restarts.

---

## ♻️ Rotation Policy

| Setting | Value |
|---|---|
| Rotation trigger | Daily at midnight (`when="midnight"`) |
| Retention | 30 days (`backupCount=30`) |
| Compression | Automatic `.gz` after rotation via `gz_rotator` |

Files older than 30 days are deleted automatically by the handler.

---

## ✨ How to Add a New Log Event

**1. Define a constant in `src/config/log_events.py`:**

```python
USER_PASSWORD_CHANGED = "user.password_changed"
```

**2. Use the constant in the service or route:**

```python
import structlog
from src.config.log_events import USER_PASSWORD_CHANGED

log = structlog.get_logger()

log.info(USER_PASSWORD_CHANGED, user_id=str(user_uuid))
```

**Never use string literals directly:**

```python
# WRONG
log.info("user.password_changed", user_id=str(user_uuid))

# CORRECT
log.info(USER_PASSWORD_CHANGED, user_id=str(user_uuid))
```

---

## 🚫 Prohibited Fields

The following fields must **never** appear in any log entry:

| Field | Reason |
|---|---|
| `email` | Personal data — LGPD |
| `cpf` | Brazilian tax ID — sensitive personal data |
| `password` | Credential — must never be logged |
| `name` / `nome` | Personal data — LGPD |
| `senha` | Credential in Portuguese — must never be logged |

Use only UUIDs and operational metadata (counts, status codes, durations, flags).

The script `scripts/validate_log_privacy.py` can be used to audit the log file:

```bash
docker compose --profile backend exec backend python scripts/validate_log_privacy.py logs/app.log
```

---

## 📝 Example Log Lines

Request lifecycle with a successful user creation:

```json
{"event": "request_started", "path": "/users/", "method": "POST", "user_id": null, "request_id": "9da79a28-913f-4928-9a95-e263110572f3", "level": "info", "logger": "src.config.logging_middleware", "timestamp": "2026-04-27T01:09:08.223352Z"}
{"event": "user.created", "user_id": "1933c4ff-5b63-4189-b1b7-293a11cfc2a0", "profile_id": "dbdeb4a7-ec76-4643-931a-78616c1e3f68", "path": "/users/", "method": "POST", "request_id": "9da79a28-913f-4928-9a95-e263110572f3", "level": "info", "logger": "src.api.routes.users", "timestamp": "2026-04-27T01:09:08.447733Z"}
{"event": "request_finished", "status_code": 201, "duration_ms": 225.01, "path": "/users/", "method": "POST", "request_id": "9da79a28-913f-4928-9a95-e263110572f3", "level": "info", "logger": "src.config.logging_middleware", "timestamp": "2026-04-27T01:09:08.448862Z"}
```

Validation error example:

```json
{"event": "validation_error", "path": "/users/", "errors": [{"type": "value_error", "loc": ["body", "password"], "msg": "A senha deve conter pelo menos uma letra maiúscula."}], "request_id": "bdaa2f89-5bac-4701-b764-3039ee881040", "level": "warning", "logger": "src.config.exception_handlers", "timestamp": "2026-04-27T01:37:04.313103Z"}
```

Unhandled exception example:

```json
{"event": "unhandled_exception", "exception_type": "RuntimeError", "message": "unexpected error", "exc_info": true, "request_id": "61303840-b9bc-40f5-8240-97102a36e5e1", "level": "error", "logger": "src.config.exception_handlers", "timestamp": "2026-04-27T01:41:22.284878Z"}
```

---

*Last updated: 04/26/2026*