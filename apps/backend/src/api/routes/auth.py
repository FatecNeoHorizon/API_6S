from fastapi import APIRouter, Depends, Request

from src.api.schemas.user_schemas import (
    FirstAccessRequest,
    FirstAccessResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from src.database.postgres import get_pg_connection
from src.api.dependencies.auth import AuthenticatedUser, get_current_user_no_consent_check
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

@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout authenticated user",
    description=(
        "Invalidates the current authenticated server-side session by setting "
        "TB_SESSION.INVALIDATED_AT. The endpoint requires a valid Bearer token, "
        "does not expose sensitive data and can be used even when the user has "
        "pending consent."
    ),
)
def post_logout(
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    with get_pg_connection() as conn:
        return logout(
            conn,
            user_id=current_user.user_id,
            session_id=current_user.session_id,
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
