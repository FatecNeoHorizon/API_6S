from typing import Optional

from pydantic import BaseModel, field_validator


class SendNotificationRequest(BaseModel):
    template_id: str
    custom_subject: Optional[str] = None
    custom_body: Optional[str] = None

    @field_validator("custom_subject")
    @classmethod
    def subject_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("custom_subject não pode ser uma string vazia.")
        return v

    @field_validator("custom_body")
    @classmethod
    def body_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("custom_body não pode ser uma string vazia.")
        return v


class SendNotificationResponse(BaseModel):
    recipient_count: int
    message: str


class TemplateResponse(BaseModel):
    template_id: str
    name: str
    subject: str
    body: str
