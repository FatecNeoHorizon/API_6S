from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ConsentAction(str, Enum):
    consent = "CONSENT"
    revocation = "REVOCATION"


class ConsentActionIn(BaseModel):
    clause_uuid: UUID
    policy_version_id: UUID
    action: ConsentAction

    @field_validator("clause_uuid", "policy_version_id", mode="before")
    @classmethod
    def convert_to_uuid(cls, v):
        if isinstance(v, UUID):
            return v
        if isinstance(v, str):
            try:
                return UUID(v)
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid UUID: {v}")
        raise ValueError(f"UUID must be a string or UUID object, got {type(v)}")

    @field_validator("action", mode="before")
    @classmethod
    def convert_action(cls, v):
        if isinstance(v, ConsentAction):
            return v
        if isinstance(v, str):
            v_upper = v.upper()
            if v_upper == "CONSENT":
                return ConsentAction.consent
            elif v_upper == "REVOCATION":
                return ConsentAction.revocation
            raise ValueError(f"Invalid action: {v}. Must be 'CONSENT' or 'REVOCATION'")
        raise ValueError(f"Action must be a string, got {type(v)}")


class ConsentRequest(BaseModel):
    actions: list[ConsentActionIn] = Field(default_factory=list)
