from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PolicyType(str, Enum):
    privacy_policy = "PRIVACY_POLICY"
    terms_of_use = "TERMS_OF_USE"


class CreatePolicyVersionIn(BaseModel):
    version: str = Field(min_length=1, max_length=20)
    policy_type: PolicyType
    content: str = Field(min_length=1)
    effective_from: datetime


class CreateClauseIn(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    mandatory: bool
    display_order: int = Field(ge=1)