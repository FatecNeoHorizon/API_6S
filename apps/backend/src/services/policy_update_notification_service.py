"""Automatic user notice for scheduled policy version changes."""

import html
import logging
from typing import List

from src.config.settings import Settings
from src.repositories.incident_notification_repository import list_active_user_email_enc
from src.services.email_service import send_bulk_notification
from src.services.user_service import _decrypt_email


logger = logging.getLogger(__name__)

_POLICY_LABELS = {
    "PRIVACY_POLICY": "Pol\u00edtica de Privacidade",
    "TERMS_OF_USE": "Termos de Uso",
}


def prepare_policy_update_notification(conn, policy_version: dict) -> tuple:
    """Build a policy update notice and resolve active-user recipients."""
    policy_type = policy_version["policy_type"]
    policy_label = _POLICY_LABELS.get(policy_type, policy_type)
    version = policy_version["version"]
    effective_from = policy_version["effective_from"]

    subject = f"Atualiza\u00e7\u00e3o de {policy_label} - vers\u00e3o {version}"
    body_text = (
        f"Prezado(a) usu\u00e1rio(a),\n\n"
        f"Informamos que uma nova vers\u00e3o de {policy_label} (vers\u00e3o {version}) "
        f"foi publicada e entrar\u00e1 em vigor em {effective_from}.\n\n"
        "Antes da data de vig\u00eancia, acesse a plataforma para revisar o novo "
        "texto e decidir se deseja continuar utilizando os servi\u00e7os sob os "
        "termos atualizados.\n\n"
        "Caso n\u00e3o concorde com a altera\u00e7\u00e3o da base ou das condi\u00e7\u00f5es de "
        "tratamento de seus dados pessoais, voc\u00ea poder\u00e1 revogar seu "
        "consentimento na plataforma.\n\n"
        "Esta comunica\u00e7\u00e3o \u00e9 realizada em atendimento ao Art. 8, par\u00e1grafo 6, "
        "da Lei n\u00ba 13.709/2018 (LGPD).\n\n"
        "Atenciosamente,\nEquipe Zeus"
    )
    body_html = _body_to_html(subject, body_text)

    settings = Settings()
    emails: List[str] = []
    for encrypted_email in list_active_user_email_enc(conn):
        try:
            emails.append(_decrypt_email(encrypted_email, settings))
        except Exception:
            logger.warning("Could not decrypt an email address; skipping.")

    return emails, subject, body_html, body_text, len(emails)


def dispatch_policy_update_emails_task(
    emails: List[str],
    subject: str,
    body_html: str,
    body_text: str,
) -> None:
    """Background task that delivers a scheduled policy update notice."""
    result = send_bulk_notification(emails, subject, body_html, body_text)
    logger.info(
        "policy.update.notification.dispatch_complete",
        extra={"sent": result["sent"], "failed": result["failed"]},
    )


def _body_to_html(subject: str, body: str) -> str:
    paragraphs = []
    for line in body.split("\n"):
        escaped_line = html.escape(line.strip())
        paragraphs.append(f"<p style='margin: 0 0 10px 0;'>{escaped_line}</p>" if escaped_line else "<br>")

    return f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; background: #f9f9f9;">
  <div style="max-width: 600px; margin: 30px auto; background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 32px;">
    <h2 style="color: #2c3e50; margin-top: 0;">{html.escape(subject)}</h2>
    <div style="font-size: 15px; line-height: 1.6;">
      {"".join(paragraphs)}
    </div>
    <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;">
    <p style="font-size: 12px; color: #999;">
      Comunica\u00e7\u00e3o enviada em atendimento ao Art. 8, par\u00e1grafo 6, da LGPD.
    </p>
  </div>
</body>
</html>
"""
