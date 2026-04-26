from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies.auth import AuthenticatedUser, require_admin
from src.api.schemas.admin_terms import CreateClauseIn, CreatePolicyVersionIn
from src.database.postgres import get_pg_connection, set_current_user
from src.repositories.admin_terms_repository import (
    clause_code_exists,
    create_clause,
    create_policy_version,
    get_policy_version,
    list_clauses,
    list_policy_versions,
    policy_version_exists,
)


router = APIRouter(prefix="/admin/terms", tags=["admin-terms"])


def normalize_datetime(value: datetime) -> datetime:
    """
    Ensures datetime comparison is timezone-safe.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def format_policy_version(row: dict) -> dict:
    return {
        "policy_version_id": str(row["version_uuid"]),
        "version": row["version"],
        "policy_type": row["policy_type"],
        "content": row.get("content"),
        "effective_from": row["effective_from"].isoformat(),
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }


def format_policy_version_summary(row: dict) -> dict:
    return {
        "policy_version_id": str(row["version_uuid"]),
        "version": row["version"],
        "policy_type": row["policy_type"],
        "effective_from": row["effective_from"].isoformat(),
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
        "clause_count": int(row["clause_count"]),
    }


def format_clause(row: dict) -> dict:
    return {
        "clause_uuid": str(row["clause_uuid"]),
        "policy_version_id": str(row["policy_version_id"]),
        "code": row["code"],
        "title": row["title"],
        "description": row["description"],
        "mandatory": row["mandatory"],
        "display_order": row["display_order"],
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }


@router.post("/versions", status_code=201)
def post_policy_version(
    payload: CreatePolicyVersionIn,
    admin: AuthenticatedUser = Depends(require_admin),
):
    effective_from = normalize_datetime(payload.effective_from)
    now = datetime.now(timezone.utc)

    if effective_from <= now:
        raise HTTPException(
            status_code=422,
            detail="effective_from_must_be_future",
        )

    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        if policy_version_exists(
            conn,
            version=payload.version,
            policy_type=payload.policy_type.value,
        ):
            raise HTTPException(
                status_code=409,
                detail="policy_version_already_exists",
            )

        created = create_policy_version(
            conn=conn,
            version=payload.version,
            policy_type=payload.policy_type.value,
            content=payload.content,
            effective_from=effective_from,
        )

    return format_policy_version(created)


@router.get("/versions")
def get_policy_versions(
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)
        versions = list_policy_versions(conn)

    return {
        "versions": [
            format_policy_version_summary(version)
            for version in versions
        ]
    }


@router.post("/versions/{version_id}/clauses", status_code=201)
def post_clause(
    version_id: UUID,
    payload: CreateClauseIn,
    admin: AuthenticatedUser = Depends(require_admin),
):
    now = datetime.now(timezone.utc)

    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        version = get_policy_version(conn, str(version_id))

        if not version:
            raise HTTPException(
                status_code=404,
                detail="policy_version_not_found",
            )

        effective_from = normalize_datetime(version["effective_from"])

        if effective_from <= now:
            raise HTTPException(
                status_code=422,
                detail="cannot_add_clause_to_effective_version",
            )

        if clause_code_exists(conn, str(version_id), payload.code):
            raise HTTPException(
                status_code=409,
                detail="clause_code_already_exists_for_this_version",
            )

        created = create_clause(
            conn=conn,
            version_id=str(version_id),
            code=payload.code,
            title=payload.title,
            description=payload.description,
            mandatory=payload.mandatory,
            display_order=payload.display_order,
        )

    return format_clause(created)


@router.get("/versions/{version_id}/clauses")
def get_clauses(
    version_id: UUID,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)

        version = get_policy_version(conn, str(version_id))

        if not version:
            raise HTTPException(
                status_code=404,
                detail="policy_version_not_found",
            )

        clauses = list_clauses(conn, str(version_id))

    return {
        "clauses": [
            format_clause(clause)
            for clause in clauses
        ]
    }