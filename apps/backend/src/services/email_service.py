"""Email service for sending first-access tokens."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config.settings import Settings


logger = logging.getLogger(__name__)


def send_first_access_email(to_address: str, first_access_url: str) -> None:
    """
    Send a first-access email with the given URL.
    
    Args:
        to_address: Recipient email address
        first_access_url: URL for first-access link
        
    Raises:
        Exception: If SMTP connection or sending fails
    """
    settings = Settings()
    
    # Validate SMTP settings
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password or not settings.smtp_from:
        logger.warning("SMTP settings not configured. Skipping email send.")
        return
    
    try:
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Bem-vindo! Complete seu acesso"
        msg["From"] = settings.smtp_from
        msg["To"] = to_address
        
        # Plain text version (fallback)
        text_content = f"""Bem-vindo!

Para completar seu acesso, clique no link abaixo:

{first_access_url}

Este link expira em 48 horas.

Se você não solicitou este acesso, ignore este email.
"""
        
        # HTML version
        html_content = f"""
        <html>
            <head></head>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2c3e50;">Bem-vindo!</h1>
                    <p style="font-size: 16px; line-height: 1.5;">
                        Para completar seu acesso, clique no botão abaixo:
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{first_access_url}" style="display: inline-block; padding: 12px 30px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Acessar Plataforma
                        </a>
                    </div>
                    <p style="font-size: 14px; color: #666;">
                        Ou copie e cole este link no seu navegador:
                    </p>
                    <p style="font-size: 12px; color: #888; word-break: break-all;">
                        {first_access_url}
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="font-size: 12px; color: #999;">
                        Este link expira em 48 horas.
                        <br>
                        Se você não solicitou este acesso, ignore este email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Attach both versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect and send via SMTP with TLS
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        
        logger.info(f"First-access email sent to {to_address}")
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        raise Exception("SMTP authentication failed") from e
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        raise Exception(f"SMTP error: {e}") from e
    except Exception as e:
        logger.error(f"Failed to send first-access email: {e}")
        raise


def send_bulk_incident_notification(
    to_addresses: list,
    subject: str,
    body_html: str,
    body_text: str,
) -> dict:
    """
    Send a notification email to all addresses in the list.
    Returns a dict with 'sent' and 'failed' counts.
    Failures per recipient are logged but do not abort the batch.
    """
    settings = Settings()

    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password or not settings.smtp_from:
        logger.warning("SMTP settings not configured. Skipping bulk incident notification.")
        return {"sent": 0, "failed": len(to_addresses)}

    sent = 0
    failed = 0

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)

            for address in to_addresses:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"] = settings.smtp_from
                    msg["To"] = address
                    msg.attach(MIMEText(body_text, "plain"))
                    msg.attach(MIMEText(body_html, "html"))
                    server.send_message(msg)
                    sent += 1
                except Exception as exc:
                    logger.error(f"Failed to send incident notification to {address}: {exc}")
                    failed += 1

    except smtplib.SMTPAuthenticationError as exc:
        logger.error(f"SMTP authentication failed for bulk send: {exc}")
        return {"sent": 0, "failed": len(to_addresses)}
    except smtplib.SMTPException as exc:
        logger.error(f"SMTP error in bulk send: {exc}")
        return {"sent": sent, "failed": failed + (len(to_addresses) - sent - failed)}
    except Exception as exc:
        logger.error(f"Unexpected error in bulk send: {exc}")
        return {"sent": sent, "failed": failed + (len(to_addresses) - sent - failed)}

    logger.info(f"Bulk incident notification complete. sent={sent}, failed={failed}")
    return {"sent": sent, "failed": failed}
