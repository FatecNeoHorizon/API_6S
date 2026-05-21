"""Service for LGPD Art. 48 incident notification dispatch."""

import logging
from typing import List

from psycopg2 import IntegrityError, OperationalError

from src.config.exception_handlers import handle_db_integrity_error, handle_db_operational_error
from src.config.settings import Settings
from src.database.postgres import get_pg_connection
from src.repositories.incident_notification_repository import list_active_user_email_enc
from src.services.email_service import send_bulk_incident_notification
from src.services.user_service import _decrypt_email


logger = logging.getLogger(__name__)

TEMPLATES = [
    {
        "template_id": "cyberattack_data_breach",
        "name": "Ataque Cibernético / Violação de Dados",
        "subject": "Notificação de Incidente de Segurança – Violação de Dados",
        "body": (
            "Prezado(a) usuário(a),\n\n"
            "Informamos que nossa plataforma sofreu um incidente de segurança envolvendo "
            "acesso não autorizado a dados pessoais. Identificamos a ocorrência e "
            "imediatamente adotamos medidas de contenção.\n\n"
            "Dados potencialmente afetados: nome, endereço de e-mail e informações de conta.\n\n"
            "Medidas adotadas:\n"
            "- Isolamento dos sistemas afetados\n"
            "- Alteração de credenciais de acesso\n"
            "- Notificação à Autoridade Nacional de Proteção de Dados (ANPD), "
            "conforme Art. 48 da LGPD\n\n"
            "Recomendamos que você altere sua senha imediatamente e permaneça atento "
            "a comunicações suspeitas.\n\n"
            "Você tem o direito de solicitar informações sobre o tratamento de seus dados, "
            "nos termos dos artigos 17 a 22 da Lei nº 13.709/2018 (LGPD). "
            "Para exercer seus direitos ou obter mais informações, entre em contato conosco.\n\n"
            "Atenciosamente,\nEquipe Zeus"
        ),
    },
    {
        "template_id": "infrastructure_failure",
        "name": "Falha de Infraestrutura / Perda de Dados",
        "subject": "Comunicado de Incidente – Falha de Infraestrutura",
        "body": (
            "Prezado(a) usuário(a),\n\n"
            "Comunicamos a ocorrência de uma falha de infraestrutura em nossos sistemas "
            "que pode ter resultado em perda parcial ou total de dados associados à sua conta.\n\n"
            "Medidas adotadas:\n"
            "- Recuperação dos sistemas a partir de backups disponíveis\n"
            "- Auditoria completa da integridade dos dados\n"
            "- Notificação à Autoridade Nacional de Proteção de Dados (ANPD), "
            "conforme Art. 48 da LGPD\n\n"
            "Caso identifique inconsistências nos seus dados, entre em contato imediatamente "
            "com nossa equipe de suporte.\n\n"
            "Você tem o direito de solicitar informações sobre o tratamento de seus dados, "
            "nos termos dos artigos 17 a 22 da Lei nº 13.709/2018 (LGPD).\n\n"
            "Atenciosamente,\nEquipe Zeus"
        ),
    },
    {
        "template_id": "accidental_exposure",
        "name": "Exposição Acidental de Dados",
        "subject": "Notificação de Incidente de Privacidade – Exposição Acidental de Dados",
        "body": (
            "Prezado(a) usuário(a),\n\n"
            "Informamos que, em virtude de uma falha de configuração identificada em nossos "
            "sistemas, dados pessoais de usuários da plataforma foram expostos de forma "
            "não intencional a terceiros não autorizados.\n\n"
            "Medidas adotadas:\n"
            "- Correção imediata da configuração inadequada\n"
            "- Auditoria dos acessos realizados durante o período de exposição\n"
            "- Notificação à Autoridade Nacional de Proteção de Dados (ANPD), "
            "conforme Art. 48 da LGPD\n\n"
            "Pedimos desculpas pelo ocorrido e reforçamos o nosso compromisso com a "
            "proteção dos seus dados pessoais.\n\n"
            "Você tem o direito de solicitar informações sobre o tratamento de seus dados, "
            "nos termos dos artigos 17 a 22 da Lei nº 13.709/2018 (LGPD). "
            "Para exercer seus direitos, entre em contato conosco.\n\n"
            "Atenciosamente,\nEquipe Zeus"
        ),
    },
]

_TEMPLATES_BY_ID = {t["template_id"]: t for t in TEMPLATES}


def get_templates_service() -> List[dict]:
    return [
        {
            "template_id": t["template_id"],
            "name": t["name"],
            "subject": t["subject"],
            "body": t["body"],
        }
        for t in TEMPLATES
    ]


def prepare_notification_service(
    admin_id: str,
    template_id: str,
    custom_subject: str | None,
    custom_body: str | None,
) -> tuple:
    """
    Resolves the template and decrypts recipient emails.
    Returns (emails, subject, body_html, body_text, recipient_count).
    """
    template = _TEMPLATES_BY_ID.get(template_id)
    if template is None:
        raise ValueError(f"Template '{template_id}' não encontrado.")

    subject = custom_subject.strip() if custom_subject else template["subject"]
    body_text = custom_body.strip() if custom_body else template["body"]
    body_html = _body_to_html(subject, body_text)

    try:
        with get_pg_connection() as conn:
            enc_emails = list_active_user_email_enc(conn)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="prepare_notification_service")
        raise
    except OperationalError as exc:
        handle_db_operational_error(exc, context="prepare_notification_service")
        raise

    settings = Settings()
    emails: List[str] = []
    for enc in enc_emails:
        try:
            emails.append(_decrypt_email(enc, settings))
        except Exception:
            logger.warning("Could not decrypt an email address; skipping.")

    return emails, subject, body_html, body_text, len(emails)


def dispatch_emails_task(emails: List[str], subject: str, body_html: str, body_text: str) -> None:
    """Background task: sends emails via SMTP."""
    result = send_bulk_incident_notification(emails, subject, body_html, body_text)
    logger.info(
        "incident.notification.dispatch_complete",
        extra={"sent": result["sent"], "failed": result["failed"]},
    )


def _body_to_html(subject: str, body: str) -> str:
    paragraphs = []
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped:
            paragraphs.append(f"<p style='margin: 0 0 10px 0;'>{stripped}</p>")
        else:
            paragraphs.append("<br>")

    body_html_content = "\n".join(paragraphs)

    return f"""
<html>
<head></head>
<body style="font-family: Arial, sans-serif; color: #333; background: #f9f9f9;">
  <div style="max-width: 600px; margin: 30px auto; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 32px;">
    <h2 style="color: #c0392b; margin-top: 0;">{subject}</h2>
    <div style="font-size: 15px; line-height: 1.6;">
      {body_html_content}
    </div>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="font-size: 12px; color: #999;">
      Esta mensagem foi enviada em cumprimento ao Art. 48 da Lei nº 13.709/2018 (LGPD).
    </p>
  </div>
</body>
</html>
"""
