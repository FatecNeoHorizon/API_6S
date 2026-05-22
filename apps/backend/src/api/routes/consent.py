from fastapi import APIRouter, Depends, Request
from uuid import UUID

from src.api.dependencies.auth import (
    AuthenticatedUser,
    get_current_user_no_consent_check,
    require_admin,
)
from src.api.schemas.consent import ConsentHistoryResponse, ConsentRequest
from src.database.postgres import get_pg_connection, set_current_user
from src.services.consent_service import (
    get_pending_consent,
    get_user_consent_history,
    submit_consent_batch,
)


router = APIRouter(prefix="/consent", tags=["consent"])


@router.get("")
def get_consent(
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)
        pending_clauses = get_pending_consent(conn, current_user.user_id)

    return {"pending_clauses": pending_clauses}


@router.get("/pending")
def get_pending_consent_route(
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)
        pending_clauses = get_pending_consent(conn, current_user.user_id)

    return {"pending_clauses": pending_clauses}


@router.get(
    "/history/{user_id}",
    response_model=ConsentHistoryResponse,
    summary="Consultar historico de consentimento de um usuario",
    description=(
        "Endpoint administrativo para auditoria LGPD. "
        "Retorna os eventos imutaveis de aceite e revogacao de termos "
        "registrados para o usuario informado. Requer perfil ADMIN."
    ),
)
def get_user_consent_history_for_audit(
    user_id: UUID,
    admin: AuthenticatedUser = Depends(require_admin),
):
    with get_pg_connection() as conn:
        set_current_user(conn, admin.user_id)
        history = get_user_consent_history(conn, str(user_id))

    return {
        "user_id": user_id,
        "history": history,
    }


@router.post("")
def post_consent(
    payload: ConsentRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)

        pending_clauses = submit_consent_batch(
            conn=conn,
            user_id=current_user.user_id,
            actions=payload.actions,
            source_ip=source_ip,
            user_agent=user_agent,
        )

    return {
        "status": "ok",
        "pending_clauses": pending_clauses,
    }
