"""Email sending utilities."""
from typing import List, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from app.config import settings


async def send_email(
    to: List[str],
    subject: str,
    body: str,
    html: Optional[str] = None,
    from_email: Optional[str] = None,
) -> bool:
    """
    Send an email.

    Args:
        to: List of recipient email addresses
        subject: Email subject
        body: Plain text email body
        html: Optional HTML email body
        from_email: Optional sender email (defaults to SMTP_FROM)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email send")
        return False

    try:
        message = MIMEMultipart("alternative")
        message["From"] = from_email or settings.SMTP_FROM
        message["To"] = ", ".join(to)
        message["Subject"] = subject

        # Add plain text part
        text_part = MIMEText(body, "plain")
        message.attach(text_part)

        # Add HTML part if provided
        if html:
            html_part = MIMEText(html, "html")
            message.attach(html_part)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_TLS,
            start_tls=not settings.SMTP_SSL,
        )

        logger.info(f"Email sent successfully to {to}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
