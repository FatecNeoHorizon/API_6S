from fastapi import APIRouter

from src.database.postgres import get_pg_connection
from src.services.policy_service import get_current_terms


router = APIRouter(prefix="/terms", tags=["terms"])


@router.get("")
def get_terms():
    """
    Public endpoint used to display the current effective terms and clauses.
    """
    with get_pg_connection() as conn:
        return get_current_terms(conn)