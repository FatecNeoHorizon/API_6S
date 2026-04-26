from fastapi import APIRouter, Depends

from src.api.dependencies.auth import AuthenticatedUser, get_current_user
from src.database.postgres import get_pg_connection, set_current_user
from src.repositories.consent_repository import list_pending_clauses


router = APIRouter(prefix="/consent", tags=["consent"])


def format_pending_clauses(rows: list[dict]) -> list[dict]:
    return [
        {
            "clause_uuid": str(row["clause_uuid"]),
            "policy_version_id": str(row["policy_version_id"]),
            "policy_type": row["policy_type"],
            "version": row["version"],
            "code": row["clause_code"],
            "title": row["clause_title"],
            "description": row["clause_description"],
            "mandatory": row["mandatory"],
            "display_order": row["display_order"],
        }
        for row in rows
    ]


@router.get("/pending")
def get_pending_consent(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)
        pending = list_pending_clauses(conn, current_user.user_id)

    return {"pending_clauses": format_pending_clauses(pending)}