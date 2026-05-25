# 📋 Access Log Retention Policy (LGPD Art. 7 Compliance)

## Overview

This document describes the implementation of a **90-day access log retention policy** to comply with LGPD (Lei Geral de Proteção de Dados - Brazilian General Data Protection Law) Article 7, which mandates lawful and legitimate data processing.

The US policy requires that authentication and access logs must be retained for exactly 90 days, after which they must be deleted or archived automatically.

---

## 🎯 Policy Scope

The retention policy applies to the following tables:

| Table | Timestamp Column | Operation | Purpose |
|---|---|---|---|
| `TB_AUTH_ATTEMPT` | `ATTEMPTED_AT` | **HARD DELETE** | Authentication attempt logs |
| `TB_SESSION` | `CREATED_AT` | **SOFT DELETE** | User session records |

### Future Tables (Extensible)
- `TB_LOG`: Operational audit logs (if created)
- `TB_ERROR_LOG`: Error tracking and debugging
- `TB_ACCESS_LOG`: API access logs
- Other audit/compliance logs following the same pattern

---

## ⚙️ Configuration

### Retention Period

The retention period is configured in `src/config/settings.py`:

```python
# LGPD Compliance: Log Retention Policy (Art. 7, LGPD)
access_log_retention_days: int = Field(
    default=90,
    description="Retention period in days for authentication and access logs"
)
```

**Environment Variable**: `ACCESS_LOG_RETENTION_DAYS`

To override the default 90 days:
```bash
export ACCESS_LOG_RETENTION_DAYS=60
```

---

## 🏗️ Architecture

### Component Layers

```
┌─────────────────────────────────────┐
│  Scheduler Layer (External)         │
│  - pg_cron, external cron, CI/CD    │
└────────────┬────────────────────────┘
             │ Invokes
┌────────────▼────────────────────────┐
│  Service Layer                      │
│  LogRetentionService                │
│  - calculate_cutoff_date()          │
│  - execute_cleanup()                │
│  - dry_run_cleanup()                │
└────────────┬────────────────────────┘
             │ Uses
┌────────────▼────────────────────────┐
│  Repository Layer                   │
│  LogRetentionRepository             │
│  - delete_old_auth_attempts()       │
│  - soft_delete_old_sessions()       │
└────────────┬────────────────────────┘
             │ Executes
┌────────────▼────────────────────────┐
│  Database Layer                     │
│  PostgreSQL Functions:              │
│  - execute_log_retention_cleanup()  │
│  - get_log_retention_dryrun()       │
│  - Indexes for performance          │
└─────────────────────────────────────┘
```

### Data Flow

1. **Scheduler** triggers cleanup at configured interval (e.g., daily at 2 AM)
2. **Service** calculates cutoff date based on retention period
3. **Repository** executes parameterized queries with proper error handling
4. **Database** functions perform atomic operations with transaction safety
5. **Logging** records all operations for audit and compliance

---

## 📚 Implementation Details

### Settings Configuration

File: `src/config/settings.py`

```python
class Settings(BaseSettings):
    # ...
    access_log_retention_days: int = Field(
        default=90,
        description="Retention period in days for authentication and access logs"
    )
```

### Repository Layer

File: `src/repositories/log_retention_repository.py`

**Key Methods:**

- `delete_old_auth_attempts(conn, cutoff_date, operation_id)`
  - Hard-deletes authentication attempts older than cutoff_date
  - Returns CleanupResult with deletion count
  - Suitable for non-sensitive logs

- `soft_delete_old_sessions(conn, cutoff_date, operation_id)`
  - Marks sessions as deleted by setting DELETED_AT
  - Maintains referential integrity
  - Preserves audit trail

- `get_auth_attempt_count(conn, days_old)`
  - Counts records older than specified days
  - Used for dry-run validation

- `get_session_count(conn, days_old)`
  - Counts sessions not yet deleted, older than specified days
  - Used for dry-run validation

### Service Layer

File: `src/services/log_retention_service.py`

**Key Methods:**

- `__init__(retention_days=None)`
  - Initializes with configured or override retention period

- `calculate_cutoff_date() -> datetime`
  - Returns: `now() - timedelta(days=retention_days)`

- `dry_run_cleanup() -> dict`
  - **Non-destructive** validation before actual cleanup
  - Shows count of records that would be deleted
  - Validates database state

- `execute_cleanup() -> dict`
  - Executes full cleanup operation
  - Returns operation_id and result summary
  - Handles errors per table gracefully

- `get_policy_summary() -> dict`
  - Returns current policy configuration
  - Useful for auditing and documentation

### Database Layer

File: `database/migrations/V010__log_retention_setup.sql`

**Key Functions:**

#### `execute_log_retention_cleanup(retention_days, operation_id)`

```sql
SELECT execute_log_retention_cleanup(90);
```

**Returns:**
| Column | Type | Description |
|--------|------|-------------|
| table_name | VARCHAR | Name of table processed |
| rows_affected | INT | Count of rows deleted/updated |
| cutoff_date | TIMESTAMPTZ | Cutoff date used |
| operation_id | VARCHAR | Operation tracking ID |

#### `get_log_retention_dryrun(retention_days)`

```sql
SELECT * FROM get_log_retention_dryrun(90);
```

**Returns:**
| Column | Type | Description |
|--------|------|-------------|
| table_name | VARCHAR | Name of table |
| would_delete_count | INT | Count that would be deleted |
| oldest_record | TIMESTAMPTZ | Timestamp of oldest record |
| cutoff_date | TIMESTAMPTZ | Cutoff date |

### Indexes for Performance

The migration creates indexes to optimize cleanup queries:

```sql
CREATE INDEX IX_TB_AUTH_ATTEMPT_ATTEMPTED_AT
    ON TB_AUTH_ATTEMPT (ATTEMPTED_AT DESC);

CREATE INDEX IX_TB_SESSION_CREATED_AT_DELETED_AT
    ON TB_SESSION (CREATED_AT DESC)
    WHERE DELETED_AT IS NULL;
```

---

## 🚀 Usage Examples

### 1. Dry-Run Validation

Preview what would be deleted without making changes:

```python
from src.services.log_retention_service import LogRetentionService

service = LogRetentionService()
results = service.dry_run_cleanup()

print(f"Retention Days: {results['retention_days']}")
print(f"Would delete: {results['tables']['TB_AUTH_ATTEMPT']['count']} auth attempts")
print(f"Would delete: {results['tables']['TB_SESSION']['count']} sessions")
```

### 2. Execute Cleanup

Perform actual cleanup operation:

```python
from src.services.log_retention_service import LogRetentionService
from src.database.postgres import get_pg_connection

service = LogRetentionService()
results = service.execute_cleanup()

print(f"Operation ID: {results['operation_id']}")
print(f"Status: {results['status']}")
print(f"Total deleted: {results['total_rows_deleted']}")
```

### 3. Custom Retention Period

Override default 90 days:

```python
from src.services.log_retention_service import LogRetentionService

# Use 60-day retention instead of 90
service = LogRetentionService(retention_days=60)
results = service.execute_cleanup()
```

### 4. Policy Information

Get current policy configuration:

```python
from src.services.log_retention_service import LogRetentionService

service = LogRetentionService()
policy = service.get_policy_summary()

print(f"Retention Standard: {policy['compliance_standard']}")
print(f"Tables: {policy['tables_under_retention']}")
```

### 5. Direct SQL Query

Execute cleanup directly in PostgreSQL:

```sql
-- Dry-run
SELECT * FROM get_log_retention_dryrun(90);

-- Execute cleanup
SELECT * FROM execute_log_retention_cleanup(90);

-- With custom operation ID
SELECT * FROM execute_log_retention_cleanup(90, 'manual-cleanup-2026-05-25');
```

### 6. Example CLI Script

File: `apps/backend/examples/retention_cleanup_example.py`

```bash
# Show policy info
python apps/backend/examples/retention_cleanup_example.py --info

# Dry-run (preview only)
python apps/backend/examples/retention_cleanup_example.py --dry-run

# Execute cleanup
python apps/backend/examples/retention_cleanup_example.py --execute

# Custom retention period
python apps/backend/examples/retention_cleanup_example.py --execute --days 60
```

---

## 📅 Scheduling Approaches

### Option 1: PostgreSQL pg_cron (Built-in)

**Pros:** Native to PostgreSQL, no external dependencies, reliable
**Cons:** Requires pg_cron extension

```sql
-- Create extension (admin only)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily cleanup at 2 AM UTC
SELECT cron.schedule('cleanup-auth-logs', '0 2 * * *', 
    'SELECT execute_log_retention_cleanup(90)');

-- Monitor scheduled jobs
SELECT * FROM cron.job;

-- View job logs
SELECT * FROM cron.job_run_details;

-- Unschedule if needed
SELECT cron.unschedule('cleanup-auth-logs');
```

### Option 2: External Cron Job (OS-level)

**Pros:** System-level scheduling, works without database modifications
**Cons:** Requires root/postgres access, external maintenance

```bash
# /etc/cron.d/database-maintenance
# Run daily at 2 AM UTC
0 2 * * * postgres psql -d zeus_db -c "SELECT execute_log_retention_cleanup(90)" >> /var/log/retention-cleanup.log 2>&1
```

Or with connection pooling (PgBouncer):

```bash
0 2 * * * postgres psql -h localhost -p 6432 -d zeus_db -c "SELECT execute_log_retention_cleanup(90)"
```

### Option 3: CI/CD Scheduled Pipeline

**Pros:** Version-controlled, integrates with deployment process
**Cons:** Depends on CI/CD infrastructure

#### GitHub Actions Example

File: `.github/workflows/log-retention-cleanup.yml`

```yaml
name: Log Retention Cleanup

on:
  schedule:
    # Run at 2 AM UTC daily
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run log retention cleanup
        env:
          POSTGRES_HOST: ${{ secrets.POSTGRES_HOST }}
          POSTGRES_PORT: ${{ secrets.POSTGRES_PORT }}
          POSTGRES_USER: ${{ secrets.POSTGRES_USER }}
          POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
          POSTGRES_DB: ${{ secrets.POSTGRES_DB }}
        run: |
          psql -h $POSTGRES_HOST -d $POSTGRES_DB -U $POSTGRES_USER -c \
            "SELECT * FROM execute_log_retention_cleanup(90);"
      
      - name: Log cleanup result
        if: success()
        run: echo "Log retention cleanup completed successfully"
      
      - name: Notify on failure
        if: failure()
        run: |
          echo "Log retention cleanup failed!"
          exit 1
```

### Option 4: Python Background Worker (APScheduler)

**Pros:** Application-level integration, flexible scheduling
**Cons:** Adds runtime overhead, requires worker process

Example in FastAPI lifespan:

```python
# src/config/lifespan.py
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler.start()
    scheduler.add_job(
        cleanup_logs_job,
        'cron',
        hour=2,
        minute=0,
        id='log-retention-cleanup'
    )
    yield
    # Shutdown
    scheduler.shutdown()

async def cleanup_logs_job():
    """Background job for log retention cleanup."""
    from src.services.log_retention_service import LogRetentionService
    from src.database.postgres import get_pg_connection, init_postgres_pool
    
    init_postgres_pool()
    try:
        service = LogRetentionService()
        results = service.execute_cleanup()
        log.info("background_cleanup_completed", results=results)
    finally:
        close_postgres_pool()
```

### Scheduling Recommendations

| Approach | Best For | Complexity | Reliability |
|----------|----------|-----------|-------------|
| **pg_cron** | Production PostgreSQL instances | Low | ⭐⭐⭐⭐⭐ |
| **External Cron** | Systems with direct DB access | Low | ⭐⭐⭐⭐ |
| **CI/CD Pipeline** | Cloud/managed databases | Medium | ⭐⭐⭐⭐ |
| **APScheduler** | Already using workers | Medium | ⭐⭐⭐ |

**Recommended for Production**: **Option 1 (pg_cron)** - Most reliable, least external dependency

---

## 🔒 Security Considerations

### Data Protection

- ✅ Uses parameterized queries to prevent SQL injection
- ✅ Soft-delete for TB_SESSION maintains referential integrity
- ✅ Hard-delete for TB_AUTH_ATTEMPT removes sensitive data
- ✅ All operations logged for audit trail
- ✅ Transaction safety ensures consistency

### Access Control

```sql
-- Recommend restricting function execution to admin role
REVOKE ALL ON FUNCTION execute_log_retention_cleanup FROM PUBLIC;
GRANT EXECUTE ON FUNCTION execute_log_retention_cleanup TO db_admin;

REVOKE ALL ON FUNCTION get_log_retention_dryrun FROM PUBLIC;
GRANT EXECUTE ON FUNCTION get_log_retention_dryrun TO db_admin;
```

### Audit Trail

All cleanup operations are logged with:
- `operation_id`: Unique identifier for tracking
- `table_name`: Which table was affected
- `rows_deleted`: Count of records removed
- `cutoff_date`: Date used for retention cutoff
- `timestamp`: When the operation occurred
- `status`: Success or failure indication
- `error`: Any error messages (if failed)

---

## 📊 Monitoring & Alerts

### Key Metrics to Monitor

1. **Cleanup Execution Time**
   - Expected: 1-10 seconds for typical volume
   - Alert if: > 30 seconds (possible table lock)

2. **Rows Deleted per Cycle**
   - Expected: Stable after initial cleanup
   - Alert if: Suddenly drops to 0 (may indicate retention issue)
   - Alert if: Suddenly spikes (unusual data accumulation)

3. **Cleanup Success Rate**
   - Expected: 100% success
   - Alert if: Any failures occur

### Suggested Monitoring Queries

```sql
-- View recent cleanup operations
SELECT * FROM cron.job_run_details
WHERE jobname = 'cleanup-auth-logs'
ORDER BY start_time DESC
LIMIT 10;

-- Check current cleanup backlog
SELECT * FROM get_log_retention_dryrun(90);

-- Monitor table growth over time
SELECT 
    'TB_AUTH_ATTEMPT' as table_name,
    COUNT(*) as record_count,
    MIN(ATTEMPTED_AT) as oldest_record,
    MAX(ATTEMPTED_AT) as newest_record
FROM TB_AUTH_ATTEMPT
UNION ALL
SELECT 
    'TB_SESSION',
    COUNT(*),
    MIN(CREATED_AT),
    MAX(CREATED_AT)
FROM TB_SESSION
WHERE DELETED_AT IS NULL;
```

### Alerting Setup

Example Prometheus/Grafana alert:

```yaml
- alert: LogRetentionCleanupFailed
  expr: increase(log_retention_cleanup_failures[1h]) > 0
  annotations:
    summary: "Log retention cleanup failed"
    description: "Cleanup job failed to complete"

- alert: LogRetentionBacklogTooLarge
  expr: log_retention_auth_attempt_count > 100000
  annotations:
    summary: "Too many old auth attempts pending deletion"
    description: "Check scheduler and cleanup function"
```

---

## 🧪 Testing

### Manual Testing

```python
# Test dry-run
from src.services.log_retention_service import LogRetentionService
from src.database.postgres import init_postgres_pool, close_postgres_pool

init_postgres_pool()
service = LogRetentionService(retention_days=90)

# Should return counts without modifying data
results = service.dry_run_cleanup()
assert results['retention_days'] == 90

# Should return cleanup results
results = service.execute_cleanup()
assert results['status'] in ['success', 'partial_failure']

close_postgres_pool()
```

### Integration Testing

```python
# Create test data
INSERT INTO TB_AUTH_ATTEMPT (EMAIL_HASH, SOURCE_IP, SUCCESS, ATTEMPTED_AT)
VALUES ('test@example.com', '127.0.0.1', true, NOW() - INTERVAL '100 days');

# Run cleanup
SELECT execute_log_retention_cleanup(90);

# Verify deletion
SELECT COUNT(*) FROM TB_AUTH_ATTEMPT
WHERE ATTEMPTED_AT < NOW() - INTERVAL '90 days';
-- Should return 0
```

---

## 📝 Documentation References

- [LGPD.md](./LGPD.md) - Overall LGPD compliance architecture
- [LOGGING.md](./LOGGING.md) - Application logging system
- [settings.py](../apps/backend/src/config/settings.py) - Configuration
- [log_retention_service.py](../apps/backend/src/services/log_retention_service.py) - Service implementation
- [log_retention_repository.py](../apps/backend/src/repositories/log_retention_repository.py) - Repository implementation
- [V010__log_retention_setup.sql](../database/migrations/V010__log_retention_setup.sql) - Database setup

---

## 🔍 Troubleshooting

### Issue: Cleanup is slow

**Check:**
- Table size: `SELECT pg_size_pretty(pg_total_relation_size('TB_AUTH_ATTEMPT'));`
- Index presence: `\d TB_AUTH_ATTEMPT` in psql
- Lock contention: Monitor during cleanup

**Solution:**
- Consider running during low-traffic hours
- Batch delete if table is very large:
  ```sql
  -- Delete in batches to reduce lock time
  DO $$
  BEGIN
    FOR i IN 1..100 LOOP
      DELETE FROM TB_AUTH_ATTEMPT
      WHERE ATTEMPTED_AT < NOW() - INTERVAL '90 days'
      LIMIT 1000;
      COMMIT;
    END LOOP;
  END $$;
  ```

### Issue: Cleanup never runs

**Check:**
1. Scheduler status: `SELECT * FROM cron.job;` (if using pg_cron)
2. Job logs: `SELECT * FROM cron.job_run_details;`
3. Database connectivity
4. User permissions on cleanup function

### Issue: `ATTEMPTED_AT` column not found

**Solution:**
- Run migration V010 to create indexes and validate
- Check TB_AUTH_ATTEMPT structure: `\d TB_AUTH_ATTEMPT`

### Issue: Permission denied on cleanup function

**Solution:**
```sql
-- Grant execute permission to appropriate role
GRANT EXECUTE ON FUNCTION execute_log_retention_cleanup TO your_app_role;
```

---

## 🔄 Future Enhancements

- [ ] Add cleanup for TB_LOG (operational audit logs)
- [ ] Add cleanup for TB_ERROR_LOG (error tracking)
- [ ] Add cleanup for TB_ACCESS_LOG (API access logs)
- [ ] Implement retention archival (move to cold storage)
- [ ] Add Prometheus metrics export
- [ ] Add real-time dashboard for retention status
- [ ] Implement graduated retention (30/60/90 days)
- [ ] Add compliance report generation

---

## 📞 Support & Compliance

For LGPD compliance questions or to report retention policy issues:
- **DPO Email**: dpo@tecsys.com.br
- **Response Time**: Up to 15 business days (LGPD Art. 18, §4)
- **Documentation**: All cleanups are logged for audit trail

---

**Last Updated**: May 25, 2026  
**Compliance Standard**: Lei Geral de Proteção de Dados (LGPD) - Federal Law 13.709/2018  
**LGPD Articles**: Art. 6 (Principles), Art. 7 (Lawfulness), Art. 12 (Access Rights), Art. 16 (Right to Erasure)
