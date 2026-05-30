import structlog
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from src.api.dependencies.auth import AuthenticatedUser, require_admin
from src.api.schemas.admin_terms import CreateClauseIn, CreatePolicyVersionIn
from src.config.log_events import (
    POLICY_VERSION_CREATED,
    POLICY_CLAUSE_CREATED,
    POLICY_UPDATE_NOTIFICATION_SCHEDULED,
)
from src.database.postgres import get_pg_connection, set_current_user
from src.services.policy_service import (
    create_clause,
    create_policy_version,
    list_clauses,
    list_policy_versions,
    get_policy_version,
)
from src.services.policy_update_notification_service import (
    dispatch_policy_update_emails_task,
    prepare_policy_update_notification,
)


router = APIRouter(prefix="/admin/terms", tags=["admin-terms"])
log = structlog.get_logger()

@router.post("/versions", status_code=201)
def post_policy_version(
    payload: CreatePolicyVersionIn,
    background_tasks: BackgroundTasks,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        result = create_policy_version(
            conn=conn,
            version=payload.version,
            policy_type=payload.policy_type.value,
            content=payload.content,
            effective_from=payload.effective_from,
            description=payload.description,
        )

        log.info(
            POLICY_VERSION_CREATED,
            version_id=result["policy_version_id"],
            policy_type=result["policy_type"],
            effective_from=result["effective_from"],
        )

        emails, subject, body_html, body_text, recipient_count = prepare_policy_update_notification(
            conn,
            result,
        )
        background_tasks.add_task(
            dispatch_policy_update_emails_task,
            emails,
            subject,
            body_html,
            body_text,
        )

        log.info(
            POLICY_UPDATE_NOTIFICATION_SCHEDULED,
            version_id=result["policy_version_id"],
            recipient_count=recipient_count,
        )

        return result

@router.get("/versions")
def get_policy_versions(
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)
        return list_policy_versions(conn)

@router.get("/versions/{version_id}")
def get_version(
    version_id: UUID,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)
        return get_policy_version(conn, str(version_id))

@router.post("/versions/{version_id}/clauses", status_code=201)
def post_clause(
    version_id: UUID,
    payload: CreateClauseIn,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        result = create_clause(
            conn=conn,
            version_id=str(version_id),
            code=payload.code,
            title=payload.title,
            description=payload.description,
            mandatory=payload.mandatory,
            display_order=payload.display_order,
        )

        log.info(
            POLICY_CLAUSE_CREATED,
            clause_id=result["clause_uuid"],
            version_id=result["policy_version_id"],
            mandatory=result["mandatory"],
        )

        return result

@router.get("/versions/{version_id}/clauses")
def get_clauses(
    version_id: UUID,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)
        return list_clauses(conn, str(version_id))
