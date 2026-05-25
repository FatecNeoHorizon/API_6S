"""
Service for managing log retention and cleanup operations.

This module orchestrates the cleanup of authentication and access logs
according to LGPD Art. 7 requirements (90-day retention period).

Responsibilities:
- Calculate cutoff dates based on configured retention period
- Execute cleanup operations against all retention tables
- Provide dry-run capabilities for validation
- Log and report cleanup results
- Handle transaction safety and rollback scenarios
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import structlog

from src.config.settings import Settings
from src.database.postgres import get_pg_connection
from src.repositories.log_retention_repository import (
    LogRetentionRepository,
    CleanupResult,
)


settings = Settings()
log = structlog.get_logger()


class LogRetentionService:
    """
    Service for executing log retention policies.
    
    This service coordinates cleanup operations for all tables under
    the retention policy, ensuring LGPD compliance by deleting records
    older than the configured retention period.
    
    Usage:
        service = LogRetentionService()
        results = service.execute_cleanup()
        # or
        validation = service.dry_run_cleanup()
    """

    def __init__(self, retention_days: int = None):
        """
        Initialize the retention service.
        
        Args:
            retention_days: Override default retention period (defaults to settings)
        """
        self.retention_days = retention_days or settings.access_log_retention_days
        
        if self.retention_days <= 0:
            raise ValueError(
                f"retention_days must be positive, got {self.retention_days}"
            )

    def calculate_cutoff_date(self) -> datetime:
        """
        Calculate the cutoff date for cleanup.
        
        Records older than this date should be deleted/archived.
        
        Returns:
            datetime: cutoff_date = now() - retention_days
        """
        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=self.retention_days)
        return cutoff_date

    def dry_run_cleanup(self) -> dict:
        """
        Perform a dry-run validation without deleting any data.
        
        This is useful for understanding what would be deleted and
        verifying the cleanup operation before running it for real.
        
        Returns:
            Dictionary with cleanup summary:
            {
                'retention_days': 90,
                'cutoff_date': <datetime>,
                'tables': {
                    'TB_AUTH_ATTEMPT': {
                        'would_delete_count': 1234,
                        'oldest_record': <datetime>
                    },
                    'TB_SESSION': {
                        'would_delete_count': 567,
                        'oldest_record': <datetime>
                    }
                }
            }
        """
        try:
            cutoff_date = self.calculate_cutoff_date()
            
            with get_pg_connection() as conn:
                auth_attempts_count = LogRetentionRepository.get_auth_attempt_count(
                    conn,
                    self.retention_days
                )
                
                sessions_count = LogRetentionRepository.get_session_count(
                    conn,
                    self.retention_days
                )
            
            log.info(
                "log_retention_dry_run_completed",
                retention_days=self.retention_days,
                cutoff_date=cutoff_date.isoformat(),
                auth_attempts_count=auth_attempts_count['count'],
                sessions_count=sessions_count['count']
            )
            
            return {
                'retention_days': self.retention_days,
                'cutoff_date': cutoff_date,
                'tables': {
                    'TB_AUTH_ATTEMPT': auth_attempts_count,
                    'TB_SESSION': sessions_count,
                }
            }
        except Exception as e:
            log.error(
                "log_retention_dry_run_failed",
                error=str(e),
                retention_days=self.retention_days
            )
            raise

    def execute_cleanup(self) -> dict:
        """
        Execute the full cleanup operation.
        
        This deletes authentication attempts older than the retention period
        and soft-deletes session records following the same cutoff.
        
        The operation is atomic per table (each table commit is separate,
        but individual operations don't affect others if one fails).
        
        Returns:
            Dictionary with cleanup results:
            {
                'operation_id': <uuid>,
                'retention_days': 90,
                'cutoff_date': <datetime>,
                'results': [
                    CleanupResult(...),
                    CleanupResult(...),
                ],
                'total_rows_deleted': 1801,
                'status': 'success' | 'partial_failure' | 'failure'
            }
        """
        operation_id = str(uuid4())
        cutoff_date = self.calculate_cutoff_date()
        results = []
        errors = []

        log.info(
            "log_retention_cleanup_started",
            operation_id=operation_id,
            retention_days=self.retention_days,
            cutoff_date=cutoff_date.isoformat()
        )

        # Execute cleanup for each table
        try:
            with get_pg_connection() as conn:
                # Clean up authentication attempts
                try:
                    result = LogRetentionRepository.delete_old_auth_attempts(
                        conn,
                        cutoff_date,
                        operation_id
                    )
                    results.append(result)
                except Exception as e:
                    error_msg = f"TB_AUTH_ATTEMPT cleanup failed: {str(e)}"
                    errors.append(error_msg)
                    log.error(
                        "log_retention_table_cleanup_failed",
                        operation_id=operation_id,
                        table="TB_AUTH_ATTEMPT",
                        error=str(e)
                    )

                # Soft-delete old sessions
                try:
                    result = LogRetentionRepository.soft_delete_old_sessions(
                        conn,
                        cutoff_date,
                        operation_id
                    )
                    results.append(result)
                except Exception as e:
                    error_msg = f"TB_SESSION soft-delete failed: {str(e)}"
                    errors.append(error_msg)
                    log.error(
                        "log_retention_table_cleanup_failed",
                        operation_id=operation_id,
                        table="TB_SESSION",
                        error=str(e)
                    )

        except Exception as e:
            log.error(
                "log_retention_cleanup_connection_failed",
                operation_id=operation_id,
                error=str(e)
            )
            errors.append(f"Database connection failed: {str(e)}")

        # Determine overall status
        total_deleted = sum(r.rows_deleted for r in results)
        
        if not errors:
            status = "success"
        elif len(results) == len(LogRetentionRepository.TABLES_UNDER_RETENTION):
            status = "partial_failure"  # Some operations succeeded
        else:
            status = "failure"

        log.info(
            "log_retention_cleanup_completed",
            operation_id=operation_id,
            status=status,
            total_rows_deleted=total_deleted,
            errors=errors,
            retention_days=self.retention_days
        )

        return {
            'operation_id': operation_id,
            'retention_days': self.retention_days,
            'cutoff_date': cutoff_date,
            'results': results,
            'total_rows_deleted': total_deleted,
            'status': status,
            'errors': errors if errors else None
        }

    def get_retention_tables_info(self) -> dict:
        """
        Get information about all tables under this service's retention policy.
        
        Returns:
            Dictionary of tables and their retention metadata
        """
        return LogRetentionRepository.get_retention_tables_info()

    def get_policy_summary(self) -> dict:
        """
        Get a summary of the current retention policy configuration.
        
        Useful for documentation and audit purposes.
        
        Returns:
            Dictionary describing the retention policy
        """
        return {
            'retention_days': self.retention_days,
            'cutoff_date_formula': 'NOW() - INTERVAL "X days"',
            'compliance_standard': 'LGPD Art. 7 (Data Protection)',
            'tables_under_retention': self.get_retention_tables_info(),
            'operation_mode': 'HARD DELETE for TB_AUTH_ATTEMPT | SOFT DELETE for TB_SESSION',
        }
