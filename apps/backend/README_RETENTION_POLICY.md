# Access Log Retention Policy - Components README

This directory contains the implementation of the 90-day access log retention policy for LGPD compliance.

## 📁 File Structure

```
backend/
├── src/
│   ├── config/
│   │   └── settings.py
│   │       └── access_log_retention_days: int = 90  (NEW)
│   │
│   ├── repositories/
│   │   └── log_retention_repository.py  (NEW)
│   │       ├── delete_old_auth_attempts()
│   │       ├── soft_delete_old_sessions()
│   │       ├── get_auth_attempt_count()
│   │       └── get_session_count()
│   │
│   └── services/
│       └── log_retention_service.py  (NEW)
│           ├── calculate_cutoff_date()
│           ├── dry_run_cleanup()
│           ├── execute_cleanup()
│           └── get_policy_summary()
│
├── examples/
│   └── retention_cleanup_example.py  (NEW)
│       └── Command-line utility for cleanup execution
│
├── tests/
│   └── test_log_retention.py  (TO CREATE)
│       └── Unit and integration tests
│
└── main.py
    └── (No changes - cleanup is triggered externally)

database/
└── migrations/
    └── V010__log_retention_setup.sql  (NEW)
        ├── Table validation
        ├── Index creation
        ├── execute_log_retention_cleanup()
        └── get_log_retention_dryrun()

docs/
├── LOG_RETENTION_POLICY.md  (NEW)
│   └── Complete policy specification and usage guide
├── FRONTEND_RETENTION_IMPACT.md  (NEW)
│   └── Analysis of UI/UX impacts
├── RETENTION_IMPLEMENTATION_GUIDE.md  (NEW)
│   └── Step-by-step implementation and operations
└── (other documentation)
```

## 🚀 Quick Start

### 1. Apply Database Migration

```bash
# Connect to your database and run:
psql -d your_database -f database/migrations/V010__log_retention_setup.sql
```

### 2. Test Dry-Run (No Changes)

```bash
cd apps/backend
python examples/retention_cleanup_example.py --dry-run
```

### 3. Show Policy Information

```bash
python examples/retention_cleanup_example.py --info
```

### 4. Execute Cleanup

```bash
python examples/retention_cleanup_example.py --execute
```

## 📖 Documentation

- **[LOG_RETENTION_POLICY.md](../docs/LOG_RETENTION_POLICY.md)** - Complete policy documentation
  - Configuration options
  - Architecture overview
  - Scheduling approaches
  - Monitoring & alerts
  - Troubleshooting

- **[RETENTION_IMPLEMENTATION_GUIDE.md](../docs/RETENTION_IMPLEMENTATION_GUIDE.md)** - Implementation checklist
  - Phase-by-phase checklist
  - Testing procedures
  - Common commands
  - Monitoring setup

- **[FRONTEND_RETENTION_IMPACT.md](../docs/FRONTEND_RETENTION_IMPACT.md)** - UI/UX impact analysis
  - Session management analysis
  - Frontend changes needed
  - User experience considerations

## 🔧 Components

### Settings (`settings.py`)

Configuration constant for retention period:

```python
access_log_retention_days: int = Field(default=90)
```

Override with: `export ACCESS_LOG_RETENTION_DAYS=90`

### Repository (`log_retention_repository.py`)

Handles database operations:

```python
# Delete old auth attempts
result = LogRetentionRepository.delete_old_auth_attempts(conn, cutoff_date, operation_id)

# Soft-delete old sessions
result = LogRetentionRepository.soft_delete_old_sessions(conn, cutoff_date, operation_id)

# Count records eligible for cleanup
count_result = LogRetentionRepository.get_auth_attempt_count(conn, days_old=90)
```

### Service (`log_retention_service.py`)

Orchestrates cleanup operations:

```python
service = LogRetentionService(retention_days=90)

# Dry-run (preview only)
results = service.dry_run_cleanup()

# Execute cleanup
results = service.execute_cleanup()

# Get policy info
policy = service.get_policy_summary()
```

### Database Functions (`V010__log_retention_setup.sql`)

PostgreSQL functions for cleanup:

```sql
-- Preview cleanup
SELECT * FROM get_log_retention_dryrun(90);

-- Execute cleanup
SELECT * FROM execute_log_retention_cleanup(90);
```

### CLI Script (`retention_cleanup_example.py`)

Command-line utility for developers/operators:

```bash
python retention_cleanup_example.py --help
python retention_cleanup_example.py --dry-run
python retention_cleanup_example.py --execute
python retention_cleanup_example.py --info
python retention_cleanup_example.py --execute --days 60
```

## 📊 Tables Affected

### TB_AUTH_ATTEMPT
- **Operation**: HARD DELETE
- **Timestamp Column**: `ATTEMPTED_AT`
- **Logic**: Delete records older than 90 days
- **Index**: `IX_TB_AUTH_ATTEMPT_ATTEMPTED_AT`
- **Rationale**: Non-sensitive operation logs, safe to delete completely

### TB_SESSION
- **Operation**: SOFT DELETE (set DELETED_AT)
- **Timestamp Column**: `CREATED_AT`
- **Logic**: Mark records as deleted if older than 90 days and not already deleted
- **Index**: `IX_TB_SESSION_CREATED_AT_DELETED_AT`
- **Rationale**: Maintains referential integrity and audit trail

## 🔄 Execution Flow

```
┌─────────────────────────────────┐
│  Scheduler (external)           │  ← Daily at 2 AM (configurable)
│  pg_cron / cron / CI/CD         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Python Service                 │
│  LogRetentionService            │
│  - Calculate cutoff date        │
│  - Call repository methods      │
│  - Log results                  │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Python Repository              │
│  LogRetentionRepository         │
│  - Build parameterized queries  │
│  - Handle connections           │
│  - Return results               │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  PostgreSQL Database            │
│  - DELETE old auth attempts     │
│  - UPDATE sessions (soft delete)│
│  - Log operations               │
└─────────────────────────────────┘
```

## 🎯 Scheduling Options

Choose one:

1. **PostgreSQL pg_cron** (Recommended)
   ```sql
   SELECT cron.schedule('cleanup-logs', '0 2 * * *', 
       'SELECT execute_log_retention_cleanup(90)');
   ```

2. **External Cron**
   ```bash
   0 2 * * * postgres psql -d zeus_db -c "SELECT execute_log_retention_cleanup(90)"
   ```

3. **CI/CD Pipeline** (.github/workflows/retention-cleanup.yml)

4. **Python APScheduler** (Background worker)

See [LOG_RETENTION_POLICY.md](../docs/LOG_RETENTION_POLICY.md#-scheduling-approaches) for details.

## 🧪 Testing

### Dry-run Test

```bash
python examples/retention_cleanup_example.py --dry-run
# No data is modified - safe to run anytime
```

### Execute Test (on staging)

```bash
python examples/retention_cleanup_example.py --execute --days 1
# Deletes records older than 1 day (test mode)
```

### Integration Test

```bash
cd apps/backend
python -m pytest tests/test_log_retention.py -v
```

## 📊 Monitoring

### Key Metrics

- Cleanup execution time (expected: 1-10 seconds)
- Rows deleted per cycle (should be stable)
- Success rate (expected: 100%)

### Monitoring Queries

```sql
-- See cleanup status
SELECT * FROM cron.job_run_details 
WHERE jobname = 'cleanup-auth-logs' 
ORDER BY start_time DESC LIMIT 10;

-- Count records eligible for cleanup
SELECT * FROM get_log_retention_dryrun(90);

-- Table growth
SELECT COUNT(*) FROM TB_AUTH_ATTEMPT;
SELECT COUNT(*) FROM TB_SESSION WHERE DELETED_AT IS NULL;
```

## 🔒 Security

- Uses parameterized queries (prevent SQL injection)
- Soft-delete for sessions (maintain referential integrity)
- All operations logged for audit trail
- Transaction safety for atomic operations
- Restricted function execution (admin role recommended)

## 🔗 Related Documentation

- **[LGPD.md](../docs/LGPD.md)** - Overall LGPD compliance
- **[LOGGING.md](../docs/LOGGING.md)** - Application logging system
- **[AUTH_ARCHITECTURE.md](../docs/AUTH_ARCHITECTURE.md)** - Authentication design

## ✅ Compliance

- **LGPD Article 6**: Principles (Purpose, Adequacy, Necessity)
- **LGPD Article 7**: Lawfulness (90-day policy enforcement)
- **LGPD Article 12**: Right to Access (data export reflects retention)
- **LGPD Article 16**: Right to Erasure (soft-delete preserves audit trail)

## 📞 Support

- **Documentation**: See docs/ directory
- **DPO**: dpo@tecsys.com.br (LGPD compliance questions)
- **Database Admin**: [contact] (Migration support)
- **Backend Team**: [contact] (Code questions)

---

**Version**: 1.0  
**Status**: Ready for Implementation  
**Last Updated**: May 25, 2026
