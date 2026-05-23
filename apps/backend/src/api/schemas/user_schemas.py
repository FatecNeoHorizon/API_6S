from datetime import datetime
from uuid import UUID
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def password_validator(password: str) -> str:
    if len(password) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("A senha deve conter pelo menos uma letra maiúscula.")
    if not re.search(r"\d", password):
        raise ValueError("A senha deve conter pelo menos um número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("A senha deve conter pelo menos um caractere especial.")
    return password


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    profile_id: UUID


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    profile_id: UUID

    @field_validator("email")
    def validate_email_format(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class UserCreateResponse(UserBase):
    user_uuid: UUID
    active: bool
    first_access_completed: bool = False
    created_at: datetime
    dev_first_access_token: str | None = None
    dev_first_access_url: str | None = None
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserCreateResponse):
    pass


class ProfileResponse(BaseModel):
    profile_uuid: UUID
    profile_name: str


class UserResult(BaseModel):
    user_uuid: UUID
    username: str
    profile_id: UUID
    active: bool
    first_access_completed: bool = False
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MyProfileResponse(UserResult):
    email: EmailStr
    profile_name: str


class MyProfileUpdateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

    @field_validator("email")
    def normalize_email(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class UserUpdateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    profile_id: UUID


class UserMeResponse(BaseModel):
    user_uuid: UUID
    username: str
    email: EmailStr
    profile_name: str
    active: bool
    first_access_completed: bool
    created_at: datetime
    updated_at: datetime


class UserMeUpdateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

    @field_validator("email")
    def normalize_email(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class UserSetActiveRequest(BaseModel):
    active: bool

class CurrentUserResponse(BaseModel):
    user_id: UUID
    username: str
    profile: str
    first_access_completed: bool
    active: bool

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    def normalize_email(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    pending_consent: bool
    pending_clauses: list[dict]


class FirstAccessRequest(BaseModel):
    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    def validate_new_password(cls, v: str) -> str:
        return password_validator(v)


class FirstAccessResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    pending_consent: bool
    pending_clauses: list[dict]


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    def normalize_email(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class ForgotPasswordResponse(BaseModel):
    detail: str
    dev_reset_token: str | None = None
    dev_reset_url: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    def validate_new_password(cls, v: str) -> str:
        return password_validator(v)


class ResetPasswordResponse(BaseModel):
    detail: str


class SessionResponse(BaseModel):
    session_uuid: UUID
    created_at: datetime
    source_ip: str | None
    user_agent: str | None
    expires_at: datetime
