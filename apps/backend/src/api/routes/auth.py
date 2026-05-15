from fastapi import APIRouter, Request, Depends

from src.api.schemas.user_schemas import (
    CurrentUserResponse,
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
)
from src.api.dependencies.auth import AuthenticatedUser, get_current_user
from src.database.postgres import get_pg_connection
from src.services.auth_service import (
    first_access,
    forgot_password,
    login,
    refresh_access_token,
    reset_password,
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


@router.post("/login", response_model=LoginResponse)
def post_login(payload: LoginRequest, request: Request):
    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        return login(
            conn,
            payload=payload,
            source_ip=source_ip,
            user_agent=user_agent,
        )


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
