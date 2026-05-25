# Implementation & Integration Guide: Access Log Retention Policy

## 🚀 Quick Start

### For Developers

1. **Understand the policy**
   ```bash
   # Read the main documentation
   cat docs/LOG_RETENTION_POLICY.md
   ```

2. **Review the code structure**
   ```
   src/config/settings.py                    # Configuration constants
   src/repositories/log_retention_repository.py  # Database queries
   src/services/log_retention_service.py      # Business logic
   database/migrations/V010__log_retention_setup.sql  # Database setup
   examples/retention_cleanup_example.py      # Usage example
   ```

3. **Test locally**
   ```bash
   # Run migration
   # psql -d your_db -f database/migrations/V010__log_retention_setup.sql
   
   # Dry-run validation
   python apps/backend/examples/retention_cleanup_example.py --dry-run
   
   # Execute cleanup
   python apps/backend/examples/retention_cleanup_example.py --execute
   ```

### For DevOps/SRE

1. **Choose scheduling method** (see [LOG_RETENTION_POLICY.md](./LOG_RETENTION_POLICY.md#-scheduling-approaches))
2. **Set up monitoring** (see Monitoring section below)
3. **Test in staging** before production deployment
4. **Document runbook** for manual cleanup if needed

---

## 📋 Implementation Checklist

### Phase 1: Code Review ✓ COMPLETE

- [x] Settings configuration added (`access_log_retention_days = 90`)
- [x] Repository layer implemented (`log_retention_repository.py`)
- [x] Service layer implemented (`log_retention_service.py`)
- [x] Database migration created (`V010__log_retention_setup.sql`)
- [x] Example script provided (`retention_cleanup_example.py`)
- [x] Documentation completed (`LOG_RETENTION_POLICY.md`)
- [x] Frontend impact analysis done (`FRONTEND_RETENTION_IMPACT.md`)

### Phase 2: Testing (Before Production)

- [ ] **Unit Tests**: Test repository methods individually
  ```python
  # Example test file to create: tests/test_log_retention.py
  def test_delete_old_auth_attempts():
      # Insert test data
      # Call delete method
      # Verify count
      pass
  ```

- [ ] **Integration Tests**: Test full cleanup flow
  ```bash
  # Run against test database
  python -m pytest apps/backend/tests/test_log_retention.py
  ```

- [ ] **Dry-run Validation**: Preview cleanup on staging
  ```bash
  python apps/backend/examples/retention_cleanup_example.py --dry-run
  ```

- [ ] **Manual Cleanup Test**: Execute one cleanup cycle
  ```bash
  python apps/backend/examples/retention_cleanup_example.py --execute
  ```

- [ ] **Verify data integrity**: Check that only old records are deleted
  ```sql
  -- Should show only records >= 90 days old were deleted
  SELECT COUNT(*) FROM TB_AUTH_ATTEMPT 
  WHERE ATTEMPTED_AT >= NOW() - INTERVAL '90 days';
  ```

### Phase 3: Deployment

- [ ] **Migration**: Run V010__log_retention_setup.sql against production
- [ ] **Configuration**: Set `ACCESS_LOG_RETENTION_DAYS` environment variable
- [ ] **Scheduler**: Set up one of the scheduling approaches
- [ ] **Monitoring**: Set up alerts (see Monitoring section)
- [ ] **Verification**: Run dry-run on production
- [ ] **Runbook**: Document manual procedures
- [ ] **Team Notification**: Inform team of new retention policy

### Phase 4: Operations

- [ ] **Initial Cleanup**: Run first cleanup cycle manually
- [ ] **Monitor Results**: Track execution time and row counts
- [ ] **Set Alerts**: Monitor for failures
- [ ] **Document**: Update runbooks with actual timings
- [ ] **Review**: Post-implementation review after first month

---

## 🔧 Configuration

### Environment Variables

```bash
# In .env.backend or container environment
ACCESS_LOG_RETENTION_DAYS=90

# Optional: override for testing
# ACCESS_LOG_RETENTION_DAYS=7  # For testing with 7-day retention
```

### Settings.py

Already configured with:
```python
access_log_retention_days: int = Field(
    default=90,
    description="Retention period in days for authentication and access logs"
)
```

---

## 🗂️ File Structure

```
API_6S/
├── apps/backend/
│   ├── src/
│   │   ├── config/
│   │   │   └── settings.py                    ← Retention config
│   │   ├── repositories/
│   │   │   └── log_retention_repository.py    ← Database layer
│   │   ├── services/
│   │   │   └── log_retention_service.py       ← Business logic
│   │   └── tests/
│   │       └── (test files - TO CREATE)
│   ├── examples/
│   │   └── retention_cleanup_example.py       ← Usage example
│   └── main.py                                 ← FastAPI app
├── database/
│   └── migrations/
│       └── V010__log_retention_setup.sql      ← Database setup
├── docs/
│   ├── LOG_RETENTION_POLICY.md               ← Complete documentation
│   ├── FRONTEND_RETENTION_IMPACT.md          ← UI/UX impacts
│   ├── LGPD.md                               ← Overall LGPD compliance
│   ├── LOGGING.md                            ← Log system
│   └── (other docs)
└── README.md
```

---

## 💻 Common Commands

### Dry-run Validation

```bash
# Check what would be deleted (no changes)
python apps/backend/examples/retention_cleanup_example.py --dry-run
```

**Output**:
```
================================================================================
DRY-RUN: Log Retention Cleanup
================================================================================

Retention Period: 90 days
Querying database for records that would be deleted...

Cutoff Date: 2026-02-24T10:30:00+00:00

TB_AUTH_ATTEMPT:
  Records that would be deleted: 1234
  Oldest record timestamp: 2025-10-20T08:15:30+00:00

TB_SESSION:
  Records that would be deleted: 567
  Oldest record timestamp: 2025-10-22T14:45:00+00:00

TOTAL RECORDS TO DELETE: 1801

⚠ 1801 records are eligible for cleanup.
  Run with --execute flag to perform actual cleanup.
```

### Execute Cleanup

```bash
# Actually delete records
python apps/backend/examples/retention_cleanup_example.py --execute
```

**Output**:
```
================================================================================
EXECUTING: Log Retention Cleanup
================================================================================

Retention Period: 90 days
Starting cleanup operation...

Operation ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Status: SUCCESS
Cutoff Date: 2026-02-24T10:30:00+00:00

TB_AUTH_ATTEMPT:
  Rows deleted/updated: 1234

TB_SESSION:
  Rows deleted/updated: 567

TOTAL ROWS PROCESSED: 1801

✓ Cleanup completed successfully!
```

### Direct SQL Execution

```bash
# Connect to database
psql -h postgres -U postgres -d zeus_db

# Preview cleanup
SELECT * FROM get_log_retention_dryrun(90);

# Execute cleanup
SELECT * FROM execute_log_retention_cleanup(90);

# With custom operation ID
SELECT * FROM execute_log_retention_cleanup(90, 'my-operation-id');
```

### Show Policy Info

```bash
# Display current retention policy
python apps/backend/examples/retention_cleanup_example.py --info
```

---

## 📊 Monitoring Setup

### PostgreSQL Query Examples

```sql
-- Check next cleanup time (if using pg_cron)
SELECT jobid, jobname, schedule, last_run_status, last_run_time
FROM cron.job
WHERE jobname = 'cleanup-auth-logs';

-- View cleanup history
SELECT start_time, end_time, status, return_message
FROM cron.job_run_details
WHERE jobname = 'cleanup-auth-logs'
ORDER BY start_time DESC
LIMIT 20;

-- Current record counts
SELECT 'TB_AUTH_ATTEMPT' as table_name, COUNT(*) as record_count
FROM TB_AUTH_ATTEMPT
UNION ALL
SELECT 'TB_SESSION', COUNT(*)
FROM TB_SESSION
WHERE DELETED_AT IS NULL;

-- Oldest records per table
SELECT 'TB_AUTH_ATTEMPT' as table_name, MIN(ATTEMPTED_AT) as oldest_record
FROM TB_AUTH_ATTEMPT
UNION ALL
SELECT 'TB_SESSION', MIN(CREATED_AT)
FROM TB_SESSION
WHERE DELETED_AT IS NULL;

-- Records eligible for cleanup
SELECT 'TB_AUTH_ATTEMPT' as table_name, 
       COUNT(*) as cleanup_eligible
FROM TB_AUTH_ATTEMPT
WHERE ATTEMPTED_AT < NOW() - INTERVAL '90 days'
UNION ALL
SELECT 'TB_SESSION',
       COUNT(*)
FROM TB_SESSION
WHERE DELETED_AT IS NULL
AND CREATED_AT < NOW() - INTERVAL '90 days';
```

### Prometheus Metrics (Example)

If implementing Prometheus integration:

```python
# In log_retention_service.py or separate metrics module
from prometheus_client import Counter, Gauge, Histogram

cleanup_executions = Counter(
    'log_retention_cleanup_total',
    'Total cleanup executions',
    ['status', 'table']
)

cleanup_rows_deleted = Gauge(
    'log_retention_rows_deleted',
    'Rows deleted in last cleanup',
    ['table']
)

cleanup_duration = Histogram(
    'log_retention_cleanup_duration_seconds',
    'Cleanup operation duration'
)
```

### Alert Rules (Prometheus)

```yaml
groups:
  - name: log_retention
    rules:
      - alert: LogRetentionCleanupFailed
        expr: increase(log_retention_cleanup_total{status="failure"}[1h]) > 0
        annotations:
          summary: "Log retention cleanup failed"
          description: "Cleanup failed in last hour. Check logs."

      - alert: LogRetentionExecutionSlow
        expr: log_retention_cleanup_duration_seconds > 30
        annotations:
          summary: "Log retention cleanup is slow"
          description: "Cleanup took {{ $value }} seconds. May indicate performance issue."

      - alert: LogRetentionBacklogLarge
        expr: log_retention_rows_eligible > 100000
        annotations:
          summary: "Large backlog of records for cleanup"
          description: "{{ $value }} records pending cleanup. Consider manual execution."
```

---

## 🐛 Troubleshooting

### Problem: Migration fails

**Check**: 
```sql
-- Verify tables exist
SELECT * FROM information_schema.tables
WHERE table_name IN ('TB_AUTH_ATTEMPT', 'TB_SESSION');

-- Check column existence
SELECT column_name FROM information_schema.columns
WHERE table_name = 'TB_AUTH_ATTEMPT';
```

**Solution**: Ensure all migrations up to V009 have run successfully

### Problem: Cleanup takes too long

**Check**:
```sql
-- Table size
SELECT pg_size_pretty(pg_total_relation_size('TB_AUTH_ATTEMPT'));

-- Row count
SELECT COUNT(*) FROM TB_AUTH_ATTEMPT;

-- Index status
\d TB_AUTH_ATTEMPT
```

**Solution**: Consider batching deletes if table > 1GB

### Problem: "function does not exist" error

**Check**:
```sql
-- List functions
\df execute_log_retention_cleanup
\df get_log_retention_dryrun
```

**Solution**: Run V010 migration again

### Problem: Permission denied

**Solution**:
```sql
-- Grant permissions
GRANT EXECUTE ON FUNCTION execute_log_retention_cleanup TO your_app_role;
GRANT EXECUTE ON FUNCTION get_log_retention_dryrun TO your_app_role;
```

---

## 📝 Testing Guide

### Unit Test Example

```python
# tests/test_log_retention_repository.py
import pytest
from datetime import datetime, timezone
from src.repositories.log_retention_repository import LogRetentionRepository
from src.database.postgres import get_pg_connection

@pytest.fixture
def test_db_connection():
    with get_pg_connection() as conn:
        yield conn

def test_delete_old_auth_attempts(test_db_connection):
    """Test deletion of old authentication attempts."""
    # Insert test data
    cutoff = datetime.now(timezone.utc)
    
    # Execute deletion
    result = LogRetentionRepository.delete_old_auth_attempts(
        test_db_connection,
        cutoff,
        "test-operation-123"
    )
    
    # Assertions
    assert result.table_name == "TB_AUTH_ATTEMPT"
    assert result.rows_deleted >= 0
    assert result.operation_id == "test-operation-123"
```

### Integration Test Example

```python
# tests/test_log_retention_service.py
def test_dry_run_returns_valid_counts(test_db_connection):
    """Test dry-run returns valid cleanup counts."""
    service = LogRetentionService(retention_days=90)
    results = service.dry_run_cleanup()
    
    assert 'retention_days' in results
    assert 'cutoff_date' in results
    assert 'tables' in results
    assert 'TB_AUTH_ATTEMPT' in results['tables']
    assert 'TB_SESSION' in results['tables']
```

---

## 📞 Support Contacts

| Role | Contact | Responsibility |
|------|---------|-----------------|
| **DPO (Data Protection Officer)** | dpo@tecsys.com.br | LGPD compliance |
| **Database Admin** | [admin] | Migration, monitoring |
| **Backend Team** | [team] | Code maintenance |
| **DevOps/SRE** | [team] | Scheduler setup, monitoring |

---

## 🔗 Related Resources

- [LOG_RETENTION_POLICY.md](./LOG_RETENTION_POLICY.md) - Complete policy documentation
- [FRONTEND_RETENTION_IMPACT.md](./FRONTEND_RETENTION_IMPACT.md) - UI/UX impact analysis
- [LGPD.md](./LGPD.md) - Overall LGPD compliance architecture
- [AUTH_ARCHITECTURE.md](./AUTH_ARCHITECTURE.md) - Authentication design
- [LOGGING.md](./LOGGING.md) - Application logging system
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Development guidelines

---

## ✅ Post-Implementation Checklist (30 days after deployment)

- [ ] First cleanup executed successfully
- [ ] No errors in cleanup logs
- [ ] Monitoring alerts functioning
- [ ] Team trained on manual cleanup procedure
- [ ] Runbook updated with actual execution times
- [ ] Performance metrics stable
- [ ] No user-facing issues reported
- [ ] Compliance audit completed

---

**Version**: 1.0  
**Status**: Ready for Implementation  
**Last Updated**: May 25, 2026  
**Next Review**: August 25, 2026 (after first 90-day cycle)
