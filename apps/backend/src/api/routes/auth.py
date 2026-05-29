from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response
from fastapi import status
from src.api.dependencies.auth import (
    AuthenticatedUser,
    get_current_user,
    get_current_user_no_consent_check,
)
from src.api.schemas.user_schemas import (
    CallbackRequest,
    CurrentUserResponse,
    DataExportResponse,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    SessionResponse,
)
from src.config.rate_limiter import limiter
from src.database.postgres import get_pg_connection
from src.services.auth_service import (
    export_user_data,
    list_sessions_service,
    logout,
    oauth_callback,
    refresh_access_token,
    revoke_session_service,
)


router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=CurrentUserResponse)
def get_auth_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return CurrentUserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        profile=current_user.profile_name,
        active=current_user.active,
    )


@router.post("/callback", response_model=LoginResponse)
@limiter.limit("20/minute")
def post_callback(request: Request, payload: CallbackRequest):
    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        return oauth_callback(
            conn,
            code=payload.code,
            code_verifier=payload.code_verifier,
            redirect_uri=payload.redirect_uri,
            source_ip=source_ip,
            user_agent=user_agent,
        )


@router.post("/logout", status_code=204)
def post_logout(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    with get_pg_connection() as conn:
        logout(
            conn,
            user_id=current_user.user_id,
            session_id=current_user.session_id,
        )
    return Response(status_code=204)


@router.post("/refresh", response_model=RefreshTokenResponse)
def post_refresh(payload: RefreshTokenRequest):
    with get_pg_connection() as conn:
        return refresh_access_token(conn, payload=payload)



@router.get("/me/export", response_model=DataExportResponse)
def get_my_data_export(
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    with get_pg_connection() as conn:
        result = export_user_data(conn, user_id=current_user.user_id)

    return Response(
        content=result.model_dump_json(indent=2),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="my-data-export.json"'},
    )


@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    with get_pg_connection() as conn:
        return list_sessions_service(conn, user_id=current_user.user_id)


@router.delete("/sessions/{session_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_uuid: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    with get_pg_connection() as conn:
        revoke_session_service(
            conn,
            session_uuid=str(session_uuid),
            current_session_id=current_user.session_id,
            acting_user_id=current_user.user_id,
        )
