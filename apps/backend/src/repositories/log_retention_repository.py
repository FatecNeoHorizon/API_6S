"""
Repository for managing log retention policies and cleanup operations.

This module handles deletion of authentication and access logs older than the
configured retention period (LGPD Art. 7 compliance).

Tables covered:
- TB_AUTH_ATTEMPT: Authentication attempt logs
- TB_SESSION: User session records (soft delete via DELETED_AT)

Future extension points:
- TB_LOG: Operational audit logs (if added)
- TB_ERROR_LOG: Error tracking logs (if added)
- Other audit/access logs following the same pattern
"""

from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional

from psycopg2.extensions import connection as PgConnection
import structlog

log = structlog.get_logger()


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    table_name: str
    rows_deleted: int
    cutoff_date: datetime
    operation_id: str


class LogRetentionRepository:
    """
    Repository for log retention cleanup operations.
    
    Implements LGPD-compliant retention policy by deleting records older than
    the configured retention period. Uses parameterized queries to prevent
    SQL injection and ensure data safety.
    
    Extension pattern:
    - Add new retention methods following the same pattern
    - Use cutoff_date parameter instead of hardcoding intervals
    - Update TABLES_UNDER_RETENTION documentation
    """

    # Tables included in the retention policy
    TABLES_UNDER_RETENTION = {
        'TB_AUTH_ATTEMPT': {
            'timestamp_column': 'ATTEMPTED_AT',
            'description': 'Authentication attempt logs - LGPD Art. 7'
        },
        'TB_SESSION': {
            'timestamp_column': 'CREATED_AT',
            'description': 'User session records - LGPD Art. 7',
            'soft_delete': True,  # Uses DELETED_AT instead of hard delete
        }
    }

    @staticmethod
    def delete_old_auth_attempts(
        conn: PgConnection,
        cutoff_date: datetime,
        operation_id: str
    ) -> CleanupResult:
        """
        Delete authentication attempt records older than cutoff_date.
        
        This is a HARD DELETE operation suitable for non-sensitive attempt logs.
        Records are removed completely after retention period expires.
        
        Args:
            conn: PostgreSQL connection
            cutoff_date: Delete records with ATTEMPTED_AT < cutoff_date
            operation_id: Unique identifier for logging/tracking this operation
            
        Returns:
            CleanupResult with deletion count and execution details
            
        Raises:
            psycopg2.Error: Database operation failures
        """
        query = """
            DELETE FROM TB_AUTH_ATTEMPT
            WHERE ATTEMPTED_AT < %s
        """
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (cutoff_date,))
                rows_deleted = cursor.rowcount
                conn.commit()
                
                log.info(
                    "log_retention_auth_attempts_deleted",
                    operation_id=operation_id,
                    rows_deleted=rows_deleted,
                    cutoff_date=cutoff_date.isoformat(),
                    table="TB_AUTH_ATTEMPT"
                )
                
                return CleanupResult(
                    table_name="TB_AUTH_ATTEMPT",
                    rows_deleted=rows_deleted,
                    cutoff_date=cutoff_date,
                    operation_id=operation_id
                )
        except Exception as e:
            conn.rollback()
            log.error(
                "log_retention_auth_attempts_failed",
                operation_id=operation_id,
                error=str(e),
                cutoff_date=cutoff_date.isoformat(),
                table="TB_AUTH_ATTEMPT"
            )
            raise

    @staticmethod
    def soft_delete_old_sessions(
        conn: PgConnection,
        cutoff_date: datetime,
        operation_id: str
    ) -> CleanupResult:
        """
        Soft-delete old session records by setting DELETED_AT.
        
        Sessions are not hard-deleted to maintain referential integrity and
        audit trail. Instead, DELETED_AT is set, marking them as logically deleted.
        
        Note: This may be called during cleanup, but sessions may also be
        soft-deleted earlier due to invalidation or explicit logout.
        
        Args:
            conn: PostgreSQL connection
            cutoff_date: Soft-delete sessions with CREATED_AT < cutoff_date
            operation_id: Unique identifier for logging/tracking this operation
            
        Returns:
            CleanupResult with soft-delete count and execution details
            
        Raises:
            psycopg2.Error: Database operation failures
        """
        query = """
            UPDATE TB_SESSION
            SET DELETED_AT = %s
            WHERE DELETED_AT IS NULL
              AND CREATED_AT < %s
        """
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (datetime.now(timezone.utc), cutoff_date))
                rows_deleted = cursor.rowcount
                conn.commit()
                
                log.info(
                    "log_retention_sessions_soft_deleted",
                    operation_id=operation_id,
                    rows_deleted=rows_deleted,
                    cutoff_date=cutoff_date.isoformat(),
                    table="TB_SESSION"
                )
                
                return CleanupResult(
                    table_name="TB_SESSION",
                    rows_deleted=rows_deleted,
                    cutoff_date=cutoff_date,
                    operation_id=operation_id
                )
        except Exception as e:
            conn.rollback()
            log.error(
                "log_retention_sessions_soft_delete_failed",
                operation_id=operation_id,
                error=str(e),
                cutoff_date=cutoff_date.isoformat(),
                table="TB_SESSION"
            )
            raise

    @staticmethod
    def get_retention_tables_info() -> dict:
        """
        Get information about all tables under retention policy.
        
        Useful for documentation, auditing, and understanding the scope
        of the retention policy.
        
        Returns:
            Dictionary mapping table names to retention metadata
        """
        return LogRetentionRepository.TABLES_UNDER_RETENTION

    @staticmethod
    def get_auth_attempt_count(
        conn: PgConnection,
        days_old: int
    ) -> dict:
        """
        Get count of auth attempts older than specified days.
        
        Useful for dry-run validation before actual cleanup.
        
        Args:
            conn: PostgreSQL connection
            days_old: Count records older than this many days
            
        Returns:
            Dict with count and oldest timestamp
        """
        query = """
            SELECT 
                COUNT(*) as total_count,
                MIN(ATTEMPTED_AT) as oldest_record
            FROM TB_AUTH_ATTEMPT
            WHERE ATTEMPTED_AT < NOW() - INTERVAL '%s days'
        """
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (days_old,))
                result = cursor.fetchone()
                
                return {
                    'table': 'TB_AUTH_ATTEMPT',
                    'days_old': days_old,
                    'count': result[0] if result else 0,
                    'oldest_record': result[1] if result else None
                }
        except Exception as e:
            log.error(
                "log_retention_count_query_failed",
                error=str(e),
                table="TB_AUTH_ATTEMPT",
                days_old=days_old
            )
            raise

    @staticmethod
    def get_session_count(
        conn: PgConnection,
        days_old: int
    ) -> dict:
        """
        Get count of sessions older than specified days (not yet deleted).
        
        Useful for dry-run validation before actual cleanup.
        
        Args:
            conn: PostgreSQL connection
            days_old: Count records older than this many days
            
        Returns:
            Dict with count and oldest timestamp
        """
        query = """
            SELECT 
                COUNT(*) as total_count,
                MIN(CREATED_AT) as oldest_record
            FROM TB_SESSION
            WHERE DELETED_AT IS NULL
              AND CREATED_AT < NOW() - INTERVAL '%s days'
        """
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (days_old,))
                result = cursor.fetchone()
                
                return {
                    'table': 'TB_SESSION',
                    'days_old': days_old,
                    'count': result[0] if result else 0,
                    'oldest_record': result[1] if result else None
                }
        except Exception as e:
            log.error(
                "log_retention_count_query_failed",
                error=str(e),
                table="TB_SESSION",
                days_old=days_old
            )
            raise
