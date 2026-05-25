"""
Example script demonstrating log retention cleanup execution.

This script shows how to run log retention cleanup using the service layer,
including dry-run validation and actual cleanup operations.

Usage:
    # Dry-run only (no changes):
    python examples/retention_cleanup_example.py --dry-run

    # Execute cleanup:
    python examples/retention_cleanup_example.py --execute

    # Custom retention period:
    python examples/retention_cleanup_example.py --execute --days 60
    
    # Show policy info:
    python examples/retention_cleanup_example.py --info

Note: This script is intended for manual execution, scheduled jobs, or integration
with background worker systems. For production, consider scheduled execution via
pg_cron, external cron, or APScheduler.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent / "apps" / "backend"
sys.path.insert(0, str(backend_path))

import structlog
from src.config.settings import Settings
from src.services.log_retention_service import LogRetentionService
from src.database.postgres import init_postgres_pool, close_postgres_pool


def setup_logging():
    """Configure structlog for this script."""
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )


def print_separator(title: str = ""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*80}\n{title}\n{'='*80}\n")
    else:
        print("\n" + "="*80 + "\n")


def print_policy_info():
    """Display the current retention policy configuration."""
    print_separator("Retention Policy Information")
    
    service = LogRetentionService()
    policy = service.get_policy_summary()
    
    print(f"Retention Period: {policy['retention_days']} days")
    print(f"Compliance Standard: {policy['compliance_standard']}")
    print(f"Operation Mode: {policy['operation_mode']}")
    
    print("\nTables Under Retention:")
    for table_name, table_info in policy['tables_under_retention'].items():
        print(f"\n  {table_name}:")
        print(f"    Timestamp Column: {table_info['timestamp_column']}")
        print(f"    Description: {table_info['description']}")
        if 'soft_delete' in table_info:
            print(f"    Soft Delete: {table_info['soft_delete']}")
    
    cutoff = service.calculate_cutoff_date()
    print(f"\nCurrent Cutoff Date: {cutoff.isoformat()}")
    print(f"  (Records older than this will be cleaned up)")


def run_dry_run():
    """Perform a dry-run cleanup without making changes."""
    print_separator("DRY-RUN: Log Retention Cleanup")
    
    service = LogRetentionService()
    
    try:
        print(f"Retention Period: {service.retention_days} days")
        print("Querying database for records that would be deleted...")
        print()
        
        results = service.dry_run_cleanup()
        
        print(f"Cutoff Date: {results['cutoff_date'].isoformat()}\n")
        
        total_would_delete = 0
        
        for table_name, table_data in results['tables'].items():
            count = table_data.get('count', 0)
            oldest = table_data.get('oldest_record')
            
            total_would_delete += count
            
            print(f"{table_name}:")
            print(f"  Records that would be deleted: {count}")
            if oldest:
                print(f"  Oldest record timestamp: {oldest}")
            else:
                print(f"  No records to delete")
            print()
        
        print(f"TOTAL RECORDS TO DELETE: {total_would_delete}")
        
        if total_would_delete == 0:
            print("\n✓ No records need cleanup at this time.")
        else:
            print(f"\n⚠ {total_would_delete} records are eligible for cleanup.")
            print("  Run with --execute flag to perform actual cleanup.")
        
        return True
        
    except Exception as e:
        print(f"✗ Dry-run failed with error: {str(e)}", file=sys.stderr)
        return False


def run_cleanup():
    """Execute the actual log retention cleanup."""
    print_separator("EXECUTING: Log Retention Cleanup")
    
    service = LogRetentionService()
    
    try:
        print(f"Retention Period: {service.retention_days} days")
        print("Starting cleanup operation...")
        print()
        
        results = service.execute_cleanup()
        
        print(f"Operation ID: {results['operation_id']}")
        print(f"Status: {results['status'].upper()}")
        print(f"Cutoff Date: {results['cutoff_date'].isoformat()}\n")
        
        for result in results['results']:
            print(f"{result.table_name}:")
            print(f"  Rows deleted/updated: {result.rows_deleted}")
            print()
        
        print(f"TOTAL ROWS PROCESSED: {results['total_rows_deleted']}")
        
        if results['errors']:
            print(f"\nWarnings/Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  - {error}")
        
        if results['status'] == 'success':
            print("\n✓ Cleanup completed successfully!")
        elif results['status'] == 'partial_failure':
            print("\n⚠ Cleanup partially completed. Some tables had errors.")
        else:
            print("\n✗ Cleanup failed. Please check logs above.")
        
        return results['status'] in ['success', 'partial_failure']
        
    except Exception as e:
        print(f"✗ Cleanup failed with error: {str(e)}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Log Retention Cleanup Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python examples/retention_cleanup_example.py --info
    Show current retention policy
    
  python examples/retention_cleanup_example.py --dry-run
    Preview what would be deleted (no changes)
    
  python examples/retention_cleanup_example.py --execute
    Perform actual cleanup
    
  python examples/retention_cleanup_example.py --execute --days 60
    Cleanup records older than 60 days
        """
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show retention policy information'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview cleanup without making changes'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute actual cleanup'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=None,
        help='Override retention period (default: from settings)'
    )
    
    args = parser.parse_args()
    
    # If no action specified, show help
    if not (args.info or args.dry_run or args.execute):
        parser.print_help()
        return 0
    
    # Setup
    setup_logging()
    init_postgres_pool()
    
    try:
        success = True
        
        # Execute requested actions
        if args.info:
            print_policy_info()
        
        if args.dry_run:
            success = run_dry_run() and success
        
        if args.execute:
            success = run_cleanup() and success
        
        print_separator()
        
        return 0 if success else 1
        
    finally:
        close_postgres_pool()


if __name__ == '__main__':
    exit(main())
