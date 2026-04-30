from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ConsentAction(str, Enum):
    consent = "CONSENT"
    revocation = "REVOCATION"


class ConsentActionIn(BaseModel):
    clause_uuid: UUID
    policy_version_id: UUID
    action: ConsentAction


class ConsentRequest(BaseModel):
    actions: list[ConsentActionIn] = Field(min_length=1)