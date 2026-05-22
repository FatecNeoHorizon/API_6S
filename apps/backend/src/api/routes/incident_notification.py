import structlog

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from typing import List

from src.api.dependencies.auth import AuthenticatedUser, require_admin
from src.api.schemas.incident_notification_schemas import (
    SendNotificationRequest,
    SendNotificationResponse,
    TemplateResponse,
)
from src.config.log_events import INCIDENT_NOTIFICATION_SENT
from src.services.incident_notification_service import (
    dispatch_emails_task,
    get_templates_service,
    prepare_notification_service,
)


router = APIRouter(
    prefix="/admin/incident-notification",
    tags=["incident-notification"],
    dependencies=[Depends(require_admin)],
)
log = structlog.get_logger()


@router.get("/templates", response_model=List[TemplateResponse], status_code=status.HTTP_200_OK)
def list_templates():
    return get_templates_service()


@router.post("/send", response_model=SendNotificationResponse, status_code=status.HTTP_202_ACCEPTED)
def send_notification(
    payload: SendNotificationRequest,
    background_tasks: BackgroundTasks,
    admin: AuthenticatedUser = Depends(require_admin),
):
    try:
        emails, subject, body_html, body_text, recipient_count = prepare_notification_service(
            admin_id=admin.user_id,
            template_id=payload.template_id,
            custom_subject=payload.custom_subject,
            custom_body=payload.custom_body,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao preparar o envio da notificação.",
        ) from exc

    background_tasks.add_task(dispatch_emails_task, emails, subject, body_html, body_text)

    log.info(
        INCIDENT_NOTIFICATION_SENT,
        admin_id=admin.user_id,
        template_id=payload.template_id,
        recipient_count=recipient_count,
    )

    return SendNotificationResponse(
        recipient_count=recipient_count,
        message="Notificação agendada para envio.",
    )
