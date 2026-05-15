from fastapi import APIRouter, Request

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
from src.database.postgres import get_pg_connection
from src.services.auth_service import (
    first_access,
    forgot_password,
    login,
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


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate user",
    description=(
        "Authenticates a user and records the authentication attempt in "
        "TB_AUTH_ATTEMPT using the deterministic email hash and masked source IP. "
        "The password, plain email and internal session data are never logged."
    ),
)
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
