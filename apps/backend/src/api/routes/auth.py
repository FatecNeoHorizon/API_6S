from fastapi import APIRouter, Depends, Request, Response

from src.api.dependencies.auth import AuthenticatedUser, get_current_user_no_consent_check
from src.api.schemas.user_schemas import (
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
from src.config.rate_limiter import limiter
from src.database.postgres import get_pg_connection
from src.services.auth_service import (
    first_access,
    forgot_password,
    login,
    logout,
    refresh_access_token,
    reset_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])


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
        logout(conn, user_id=current_user.user_id)
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
