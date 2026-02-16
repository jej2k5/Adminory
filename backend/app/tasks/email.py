"""Email-related Celery tasks."""
from typing import List
from app.celery_app import celery_app
from app.utils.email import send_email
from loguru import logger


@celery_app.task(name="app.tasks.email.send_email_task")
def send_email_task(
    to: List[str],
    subject: str,
    body: str,
    html: str = None,
) -> bool:
    """
    Celery task to send an email.

    Args:
        to: List of recipient email addresses
        subject: Email subject
        body: Plain text email body
        html: Optional HTML email body

    Returns:
        bool: True if email sent successfully
    """
    import asyncio

    logger.info(f"Sending email to {to} with subject: {subject}")

    # Run async send_email in sync context
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(send_email(to, subject, body, html))

    return result


@celery_app.task(name="app.tasks.email.send_verification_email")
def send_verification_email(email: str, verification_token: str) -> bool:
    """
    Send email verification email.

    Args:
        email: User email address
        verification_token: Email verification token

    Returns:
        bool: True if email sent successfully
    """
    subject = "Verify your Adminory account"
    body = f"""
    Welcome to Adminory!

    Please verify your email address by clicking the link below:
    http://localhost:3000/auth/verify?token={verification_token}

    If you didn't create an account, you can safely ignore this email.
    """

    return send_email_task([email], subject, body)


@celery_app.task(name="app.tasks.email.send_password_reset_email")
def send_password_reset_email(email: str, reset_token: str) -> bool:
    """
    Send password reset email.

    Args:
        email: User email address
        reset_token: Password reset token

    Returns:
        bool: True if email sent successfully
    """
    subject = "Reset your Adminory password"
    body = f"""
    You requested to reset your password for your Adminory account.

    Click the link below to reset your password:
    http://localhost:3000/auth/reset-password?token={reset_token}

    This link will expire in 1 hour.

    If you didn't request a password reset, you can safely ignore this email.
    """

    return send_email_task([email], subject, body)


@celery_app.task(name="app.tasks.email.send_workspace_invite")
def send_workspace_invite(email: str, workspace_name: str, invite_token: str) -> bool:
    """
    Send workspace invitation email.

    Args:
        email: Invitee email address
        workspace_name: Name of the workspace
        invite_token: Invitation token

    Returns:
        bool: True if email sent successfully
    """
    subject = f"You've been invited to join {workspace_name}"
    body = f"""
    You've been invited to join the workspace "{workspace_name}" on Adminory.

    Click the link below to accept the invitation:
    http://localhost:3000/invites/accept?token={invite_token}

    If you don't have an account, you'll be able to create one after accepting the invitation.
    """

    return send_email_task([email], subject, body)
