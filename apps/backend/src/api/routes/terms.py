from fastapi import APIRouter

from src.database.postgres import get_pg_connection
from src.repositories.terms_repository import list_current_terms


router = APIRouter(prefix="/terms", tags=["terms"])


@router.get("")
def get_terms():
    """
    Public endpoint used to display the current effective terms and clauses.

    No authentication is required here.
    """
    with get_pg_connection() as conn:
        rows = list_current_terms(conn)

    versions: dict[str, dict] = {}

    for row in rows:
        version_id = str(row["version_uuid"])

        if version_id not in versions:
            versions[version_id] = {
                "policy_version_id": version_id,
                "version": row["version"],
                "policy_type": row["policy_type"],
                "content": row["content"],
                "effective_from": row["effective_from"].isoformat(),
                "clauses": [],
            }

        if row["clause_uuid"] is not None:
            versions[version_id]["clauses"].append(
                {
                    "clause_uuid": str(row["clause_uuid"]),
                    "code": row["code"],
                    "title": row["title"],
                    "description": row["description"],
                    "mandatory": row["mandatory"],
                    "display_order": row["display_order"],
                }
            )

    return {"terms": list(versions.values())}