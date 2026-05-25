-- Migration: V010__log_retention_setup.sql
-- Purpose: Set up the log retention policy infrastructure for LGPD compliance
-- Description: Creates a database function for cleaning up old logs and indexes
--              to support efficient retention policy enforcement
-- LGPD Standard: Lei Geral de Proteção de Dados (Federal Law 13.709/2018)
--                Article 7: Lawfulness and legitimacy of data processing
--                Article 12: Right to access data

-- ============================================================================
-- Validation: Ensure TB_AUTH_ATTEMPT table is ready for retention
-- ============================================================================

-- Validate TB_AUTH_ATTEMPT structure
DO $$
DECLARE
    v_table_exists BOOLEAN;
    v_attempted_at_exists BOOLEAN;
    v_email_hash_exists BOOLEAN;
BEGIN
    -- Check if TB_AUTH_ATTEMPT exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'TB_AUTH_ATTEMPT'
    ) INTO v_table_exists;

    IF NOT v_table_exists THEN
        RAISE WARNING 'TB_AUTH_ATTEMPT table does not exist yet';
    ELSE
        -- Check for ATTEMPTED_AT column
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'TB_AUTH_ATTEMPT'
              AND column_name = 'ATTEMPTED_AT'
        ) INTO v_attempted_at_exists;

        IF NOT v_attempted_at_exists THEN
            RAISE WARNING 'TB_AUTH_ATTEMPT.ATTEMPTED_AT column missing - retention cleanup may fail';
        ELSE
            RAISE NOTICE 'TB_AUTH_ATTEMPT validation: OK - ATTEMPTED_AT column exists';
        END IF;

        -- Check for EMAIL_HASH column
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'TB_AUTH_ATTEMPT'
              AND column_name = 'EMAIL_HASH'
        ) INTO v_email_hash_exists;

        IF v_email_hash_exists THEN
            RAISE NOTICE 'TB_AUTH_ATTEMPT validation: OK - EMAIL_HASH column exists';
        END IF;
    END IF;
END $$;

-- ============================================================================
-- Validation: Ensure TB_SESSION table is ready for retention
-- ============================================================================

DO $$
DECLARE
    v_table_exists BOOLEAN;
    v_created_at_exists BOOLEAN;
    v_deleted_at_exists BOOLEAN;
BEGIN
    -- Check if TB_SESSION exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'TB_SESSION'
    ) INTO v_table_exists;

    IF NOT v_table_exists THEN
        RAISE WARNING 'TB_SESSION table does not exist yet';
    ELSE
        -- Check for CREATED_AT column
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'TB_SESSION'
              AND column_name = 'CREATED_AT'
        ) INTO v_created_at_exists;

        IF NOT v_created_at_exists THEN
            RAISE WARNING 'TB_SESSION.CREATED_AT column missing - retention cleanup may fail';
        ELSE
            RAISE NOTICE 'TB_SESSION validation: OK - CREATED_AT column exists';
        END IF;

        -- Check for DELETED_AT column (for soft delete)
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'TB_SESSION'
              AND column_name = 'DELETED_AT'
        ) INTO v_deleted_at_exists;

        IF v_deleted_at_exists THEN
            RAISE NOTICE 'TB_SESSION validation: OK - DELETED_AT column exists (soft-delete ready)';
        ELSE
            RAISE WARNING 'TB_SESSION.DELETED_AT column missing - soft delete not possible';
        END IF;
    END IF;
END $$;

-- ============================================================================
-- Ensure cleanup indexes exist (if tables are present)
-- ============================================================================

-- Index for efficient cleanup queries on TB_AUTH_ATTEMPT
CREATE INDEX IF NOT EXISTS IX_TB_AUTH_ATTEMPT_ATTEMPTED_AT
    ON TB_AUTH_ATTEMPT (ATTEMPTED_AT DESC)
    WHERE ATTEMPTED_AT IS NOT NULL;

-- Index for efficient cleanup queries on TB_SESSION
CREATE INDEX IF NOT EXISTS IX_TB_SESSION_CREATED_AT_DELETED_AT
    ON TB_SESSION (CREATED_AT DESC)
    WHERE DELETED_AT IS NULL;

-- ============================================================================
-- Database Function: execute_log_retention_cleanup()
-- Purpose: Execute the full retention policy cleanup in a single transaction
-- LGPD Compliance: Implements Art. 7 data protection principle
-- ============================================================================

CREATE OR REPLACE FUNCTION execute_log_retention_cleanup(
    p_retention_days INT DEFAULT 90,
    p_operation_id VARCHAR(36) DEFAULT NULL
)
RETURNS TABLE (
    table_name VARCHAR,
    rows_affected INT,
    cutoff_date TIMESTAMPTZ,
    operation_id VARCHAR(36)
) AS $$
DECLARE
    v_cutoff_date TIMESTAMPTZ;
    v_auth_attempts_deleted INT := 0;
    v_sessions_updated INT := 0;
    v_operation_id VARCHAR(36);
BEGIN
    -- Use provided operation_id or generate one
    v_operation_id := COALESCE(p_operation_id, gen_random_uuid()::VARCHAR);
    
    -- Calculate cutoff date
    v_cutoff_date := NOW() AT TIME ZONE 'UTC' - MAKE_INTERVAL(days => p_retention_days);

    -- Log the cleanup start
    RAISE NOTICE 'Log Retention Cleanup started: operation_id=%, retention_days=%, cutoff_date=%',
                 v_operation_id, p_retention_days, v_cutoff_date;

    -- Clean up old auth attempts (HARD DELETE)
    DELETE FROM TB_AUTH_ATTEMPT
    WHERE ATTEMPTED_AT < v_cutoff_date;
    
    v_auth_attempts_deleted := ROW_COUNT;
    
    IF v_auth_attempts_deleted > 0 THEN
        RAISE NOTICE 'Deleted % old auth attempts (cutoff: %)', v_auth_attempts_deleted, v_cutoff_date;
    END IF;

    -- Soft-delete old sessions (UPDATE DELETED_AT)
    UPDATE TB_SESSION
    SET DELETED_AT = NOW() AT TIME ZONE 'UTC'
    WHERE DELETED_AT IS NULL
      AND CREATED_AT < v_cutoff_date;
    
    v_sessions_updated := ROW_COUNT;
    
    IF v_sessions_updated > 0 THEN
        RAISE NOTICE 'Soft-deleted % old sessions (cutoff: %)', v_sessions_updated, v_cutoff_date;
    END IF;

    -- Return results for each table
    RETURN QUERY SELECT 
        'TB_AUTH_ATTEMPT'::VARCHAR,
        v_auth_attempts_deleted::INT,
        v_cutoff_date::TIMESTAMPTZ,
        v_operation_id::VARCHAR;
    
    RETURN QUERY SELECT 
        'TB_SESSION'::VARCHAR,
        v_sessions_updated::INT,
        v_cutoff_date::TIMESTAMPTZ,
        v_operation_id::VARCHAR;

    -- Final log
    RAISE NOTICE 'Log Retention Cleanup completed: operation_id=%, total_rows_affected=%, auth_attempts_deleted=%, sessions_soft_deleted=%',
                 v_operation_id, (v_auth_attempts_deleted + v_sessions_updated), v_auth_attempts_deleted, v_sessions_updated;

END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Database Function: get_log_retention_dryrun()
-- Purpose: Preview what would be cleaned up without modifying data
-- LGPD Compliance: Validation before destructive operations
-- ============================================================================

CREATE OR REPLACE FUNCTION get_log_retention_dryrun(
    p_retention_days INT DEFAULT 90
)
RETURNS TABLE (
    table_name VARCHAR,
    would_delete_count INT,
    oldest_record TIMESTAMPTZ,
    cutoff_date TIMESTAMPTZ
) AS $$
DECLARE
    v_cutoff_date TIMESTAMPTZ;
    v_auth_count INT;
    v_session_count INT;
    v_auth_oldest TIMESTAMPTZ;
    v_session_oldest TIMESTAMPTZ;
BEGIN
    -- Calculate cutoff date
    v_cutoff_date := NOW() AT TIME ZONE 'UTC' - MAKE_INTERVAL(days => p_retention_days);

    -- Count and find oldest auth attempts
    SELECT 
        COUNT(*),
        MIN(ATTEMPTED_AT)
    INTO v_auth_count, v_auth_oldest
    FROM TB_AUTH_ATTEMPT
    WHERE ATTEMPTED_AT < v_cutoff_date;

    -- Count and find oldest sessions (not yet deleted)
    SELECT 
        COUNT(*),
        MIN(CREATED_AT)
    INTO v_session_count, v_session_oldest
    FROM TB_SESSION
    WHERE DELETED_AT IS NULL
      AND CREATED_AT < v_cutoff_date;

    -- Return results
    RETURN QUERY SELECT 
        'TB_AUTH_ATTEMPT'::VARCHAR,
        v_auth_count::INT,
        v_auth_oldest::TIMESTAMPTZ,
        v_cutoff_date::TIMESTAMPTZ;
    
    RETURN QUERY SELECT 
        'TB_SESSION'::VARCHAR,
        v_session_count::INT,
        v_session_oldest::TIMESTAMPTZ,
        v_cutoff_date::TIMESTAMPTZ;

END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Documentation and Metadata
-- ============================================================================

COMMENT ON FUNCTION execute_log_retention_cleanup IS
'Execute log retention cleanup according to LGPD policy.
 Deletes TB_AUTH_ATTEMPT records older than p_retention_days.
 Soft-deletes TB_SESSION records older than p_retention_days.
 Returns count of affected rows per table.
 LGPD Art. 7: Lawfulness and legitimacy of data processing.';

COMMENT ON FUNCTION get_log_retention_dryrun IS
'Preview log retention cleanup without modifying data.
 Shows count of records that would be deleted per table.
 Useful for validation and auditing before running cleanup.
 LGPD Art. 12: Right to access data.';

-- ============================================================================
-- Grant permissions for retention functions
-- Note: Adjust roles based on your actual role structure
-- ============================================================================

-- REVOKE ALL on function execute_log_retention_cleanup FROM PUBLIC;
-- GRANT EXECUTE on function execute_log_retention_cleanup TO db_admin;

-- REVOKE ALL on function get_log_retention_dryrun FROM PUBLIC;
-- GRANT EXECUTE on function get_log_retention_dryrun TO db_admin;

-- ============================================================================
-- Retention Policy Metadata (for documentation)
-- ============================================================================

/*
RETENTION POLICY SCOPE:

1. TB_AUTH_ATTEMPT - Authentication Attempt Logs
   - Timestamp Column: ATTEMPTED_AT
   - Operation: HARD DELETE
   - Rationale: Non-sensitive operation logs, safe to delete completely
   - Index: IX_TB_AUTH_ATTEMPT_ATTEMPTED_AT

2. TB_SESSION - User Sessions
   - Timestamp Column: CREATED_AT
   - Operation: SOFT DELETE (set DELETED_AT)
   - Rationale: Maintains referential integrity and audit trail
   - Index: IX_TB_SESSION_CREATED_AT_DELETED_AT

3. Future Tables Under Retention:
   - TB_LOG (if created): Operational audit logs
   - TB_ERROR_LOG (if created): Error tracking
   - TB_ACCESS_LOG (if created): API access logs
   
LGPD COMPLIANCE:

- Article 6, X (Accountability): All cleanup operations are logged
- Article 7 (Lawfulness): Retention period enforced automatically
- Article 12 (Right to Access): Dryrun function provided for validation
- Soft deletes preserve audit trail for legal defense (Art. 16)

SCHEDULING RECOMMENDATIONS (Choose one):

1. PostgreSQL pg_cron Extension (Built-in):
   SELECT cron.schedule('cleanup-logs', '0 2 * * *', 'SELECT execute_log_retention_cleanup(90)');

2. External Cron Job (OS-level):
   # /etc/cron.d/database-maintenance
   0 2 * * * postgres psql -d DB_NAME -c "SELECT execute_log_retention_cleanup(90)"

3. CI/CD Scheduled Pipeline:
   # .github/workflows/retention-cleanup.yml
   schedule:
     - cron: '0 2 * * *'

4. Python Background Worker (APScheduler):
   # In FastAPI lifespan or standalone worker
   scheduler.add_job(
       cleanup_logs_job,
       'cron',
       hour=2,
       minute=0,
   )

MONITORING:

- Monitor function execution time (expected: 1-10 seconds)
- Track rows deleted (should be stable after initial cleanup)
- Alert if deletion suddenly drops (may indicate data retention issue)
- Log all cleanup operations for compliance audit
*/
