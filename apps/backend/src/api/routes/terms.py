from fastapi import APIRouter, Depends
from src.api.dependencies.auth import AuthenticatedUser, get_current_user_no_consent_check

from src.database.postgres import get_pg_connection
from src.services.policy_service import get_current_terms


router = APIRouter(prefix="/terms", tags=["terms"])


@router.get("")
def get_terms(current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check)):
    """
    Public endpoint used to display the current effective terms and clauses.
    """
    with get_pg_connection() as conn:
        return get_current_terms(conn)