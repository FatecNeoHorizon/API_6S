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
    CurrentUserResponse,
    DataExportResponse,
    FirstAccessRequest,
    FirstAccessResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SessionResponse,
)
from src.config.rate_limiter import limiter
from src.database.postgres import get_pg_connection
from src.services.auth_service import (
    export_user_data,
    first_access,
    forgot_password,
    list_sessions_service,
    login,
    logout,
    refresh_access_token,
    reset_password,
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
        first_access_completed=current_user.first_access_completed,
        active=current_user.active,
    )

@router.post("/first-access", response_model=FirstAccessResponse)
@limiter.limit("5/minute")
def post_first_access(request: Request, payload: FirstAccessRequest):
    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        return first_access(
            conn,
            payload=payload,
            source_ip=source_ip,
            user_agent=user_agent,
        )


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def post_login(request: Request, payload: LoginRequest):
    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        return login(
            conn,
            payload=payload,
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


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def post_forgot_password(payload: ForgotPasswordRequest):
    with get_pg_connection() as conn:
        return forgot_password(conn, email=payload.email)


@router.post("/reset-password", response_model=ResetPasswordResponse)
def post_reset_password(payload: ResetPasswordRequest):
    with get_pg_connection() as conn:
        return reset_password(conn, payload=payload)


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
