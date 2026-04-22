from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
from uuid import UUID
from datetime import datetime
import re

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
    password: str = Field(..., min_length=8)
    profile_id: Optional[UUID] = None

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        return password_validator(v)

class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    profile_id: Optional[UUID] = None

class UserResponse(UserBase):
    user_uuid: UUID
    active: bool
    created_at: datetime

    class Config:
        orm_mode = True