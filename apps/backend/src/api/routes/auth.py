from fastapi import APIRouter, Request

from src.api.schemas.user_schemas import FirstAccessRequest, FirstAccessResponse
from src.database.postgres import get_pg_connection
from src.services.auth_service import first_access


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/first-access", response_model=FirstAccessResponse)
def post_first_access(payload: FirstAccessRequest, request: Request):
    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        return first_access(
            conn,
            payload=payload,
            source_ip=source_ip,
            user_agent=user_agent,
        )