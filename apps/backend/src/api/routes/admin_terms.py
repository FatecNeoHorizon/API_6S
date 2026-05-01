from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies.auth import AuthenticatedUser, require_admin
from src.api.schemas.admin_terms import CreateClauseIn, CreatePolicyVersionIn
from src.database.postgres import get_pg_connection, set_current_user
from src.services.policy_service import (
    create_clause,
    create_policy_version,
    list_clauses,
    list_policy_versions,
    get_policy_version,
)


router = APIRouter(prefix="/admin/terms", tags=["admin-terms"])


@router.post("/versions", status_code=201)
def post_policy_version(
    payload: CreatePolicyVersionIn,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        return create_policy_version(
            conn=conn,
            version=payload.version,
            policy_type=payload.policy_type.value,
            content=payload.content,
            effective_from=payload.effective_from,
        )


@router.get("/versions")
def get_policy_versions(
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        return list_policy_versions(conn)


@router.post("/versions/{version_id}/clauses", status_code=201)
def post_clause(
    version_id: UUID,
    payload: CreateClauseIn,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        return create_clause(
            conn=conn,
            version_id=str(version_id),
            code=payload.code,
            title=payload.title,
            description=payload.description,
            mandatory=payload.mandatory,
            display_order=payload.display_order,
        )


@router.get("/versions/{version_id}/clauses")
def get_clauses(
    version_id: UUID,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        return list_clauses(conn, str(version_id))



@router.get("/versions/{version_id}")
def get_policy_version_route(
    version_id: UUID,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        return get_policy_version(conn, str(version_id))