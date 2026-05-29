from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


VALID_PROFILES = Literal["ADMIN", "MANAGER", "ANALYST"]


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    profile_name: VALID_PROFILES

    @field_validator("email")
    def validate_email_format(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class UserCreateResponse(BaseModel):
    user_uuid: UUID
    username: str
    profile_name: str
    active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    profile_uuid: UUID
    profile_name: str


class UserResult(BaseModel):
    user_uuid: UUID
    username: str
    profile_name: str
    active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    profile_name: VALID_PROFILES


class UserSetActiveRequest(BaseModel):
    active: bool


class UserMeResponse(BaseModel):
    user_uuid: UUID
    username: str
    email: EmailStr
    profile_name: str
    active: bool
    created_at: datetime
    updated_at: datetime


class UserMeUpdateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

    @field_validator("email")
    def normalize_email(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class CurrentUserResponse(BaseModel):
    user_id: UUID
    username: str
    profile: str
    active: bool


class CallbackRequest(BaseModel):
    code: str = Field(..., min_length=1)
    code_verifier: str = Field(..., min_length=1)
    redirect_uri: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
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


class LogoutResponse(BaseModel):
    detail: str


class IdentityExport(BaseModel):
    user_id: UUID
    username: str
    email: str
    profile: str
    active: bool
    created_at: datetime
    updated_at: datetime


class ConsentExportItem(BaseModel):
    consent_log_id: UUID
    clause_id: UUID
    clause_code: str
    clause_title: str
    policy_version_id: UUID
    policy_type: str
    policy_version: str
    action: str
    timestamp: datetime
    source_ip: str
    user_agent: str
    channel: str | None


class SessionExportItem(BaseModel):
    session_id: UUID
    source_ip: str
    user_agent: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None
    invalidated_at: datetime | None = None


class DataExportResponse(BaseModel):
    export_version: str = "1.0"
    exported_at: datetime
    identity: IdentityExport
    consent_history: list[ConsentExportItem]
    session_history: list[SessionExportItem]


class SessionResponse(BaseModel):
    session_uuid: UUID
    created_at: datetime
    source_ip: str | None
    user_agent: str | None
    expires_at: datetime
