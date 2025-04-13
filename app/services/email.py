"""
Email service for Promptlane.

This module handles sending various types of emails to users, including:
- User invitations
- Password resets
- System notifications
"""

import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List, Optional

from app.services.template import render_template, render_text_template
from app.config import settings

# Email configuration
email_config = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL.USER,
    MAIL_PASSWORD=settings.EMAIL.PASSWORD,
    MAIL_FROM=settings.EMAIL.FROM,
    MAIL_PORT=settings.EMAIL.PORT,
    MAIL_SERVER=settings.EMAIL.HOST,
    MAIL_FROM_NAME=settings.APP.NAME,
    MAIL_TLS=settings.EMAIL.TLS,
    MAIL_SSL=settings.EMAIL.SSL,
    USE_CREDENTIALS=settings.EMAIL.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.EMAIL.VALIDATE_CERTS
)

# Initialize FastMail
fastmail = FastMail(email_config)

logger = logging.getLogger(__name__)


def send_email(recipient: str, subject: str, html_content: str, text_content: str) -> bool:
    """
    Generic function to send an email.
    
    In a production environment, this might use a third-party service
    like SendGrid, Mailgun, or Amazon SES instead of direct SMTP.
    
    Args:
        recipient: Email address of recipient
        subject: Email subject
        html_content: HTML version of email body
        text_content: Plain text version of email body
        
    Returns:
        Success status (True if sent successfully)
    """
    # Always log email info
    logger.info(f"Email processing: To={recipient}, Subject={subject}")
    
    # Check if we're in production mode
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    # If we're in development mode
    if not is_production:
        logger.info(f"Development mode: Email to {recipient} not actually sent")
        
        # Log text content for easy testing
        logger.debug(f"Text content preview:\n{text_content[:500]}...")
        
        # Save email to file if configured
        if settings.DEBUG:
            try:
                save_email_to_file(recipient, subject, html_content, text_content)
                logger.info(f"Email to {recipient} saved to files in {settings.EMAIL.DEV_DIR}")
            except Exception as e:
                logger.error(f"Failed to save email to file: {str(e)}")
            
        return True
    
    # In production, send the actual email
    try:
        logger.info(f"Production mode: Preparing to send email to {recipient} via SMTP")
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.EMAIL.FROM
        message["To"] = recipient
        
        # Add plain text and HTML versions
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))
        
        # Log SMTP connection details (without password)
        logger.info(f"Connecting to SMTP server: {settings.EMAIL.HOST}:{settings.EMAIL.PORT} with user {settings.EMAIL.USER}")
        
        # Connect to SMTP server
        with smtplib.SMTP(settings.EMAIL.HOST, settings.EMAIL.PORT) as server:
            server.starttls()
            server.login(settings.EMAIL.USER, settings.EMAIL.PASSWORD)
            server.sendmail(settings.EMAIL.FROM, recipient, message.as_string())
        
        logger.info(f"Email successfully sent to {recipient}")
        return True
    except Exception as e:
        logger.exception(f"Failed to send email to {recipient}: {str(e)}")
        # Log more details about the failure
        if 'Authentication' in str(e):
            logger.error("SMTP authentication error - check EMAIL_USER and EMAIL_PASSWORD")
        elif 'Connection refused' in str(e):
            logger.error(f"SMTP connection error - check if {settings.EMAIL.HOST}:{settings.EMAIL.PORT} is accessible")
        return False

def save_email_to_file(recipient: str, subject: str, html_content: str, text_content: str) -> None:
    """
    Save email content to files for development and testing.
    
    Args:
        recipient: Email address of recipient
        subject: Email subject
        html_content: HTML version of email body
        text_content: Plain text version of email body
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(settings.EMAIL.DEV_DIR, exist_ok=True)
        
        # Create a safe filename from the recipient and subject
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_subject = "".join([c if c.isalnum() else "_" for c in subject])
        filename_base = f"{timestamp}_{safe_subject}_{recipient.replace('@', '_at_')}"
        
        # Save HTML version
        with open(f"{settings.EMAIL.DEV_DIR}/{filename_base}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Save text version
        with open(f"{settings.EMAIL.DEV_DIR}/{filename_base}.txt", "w", encoding="utf-8") as f:
            f.write(text_content)
            
        logger.info(f"Email saved to {settings.EMAIL.DEV_DIR}/{filename_base}.html and .txt")
    except Exception as e:
        logger.error(f"Failed to save email to file: {str(e)}")

def send_invitation_email(
    recipient_email: str,
    recipient_name: str,
    invitation_url: str,
    inviter_name: str,
    is_admin: bool = False,
    expiry_hours: int = 48,
    personal_message: str = None
) -> bool:
    """
    Send an invitation email to a new user.
    
    Args:
        recipient_email: New user's email address
        recipient_name: New user's name
        invitation_url: URL to complete registration
        inviter_name: Name of admin who sent the invitation
        is_admin: Whether the new user will have admin privileges
        expiry_hours: Hours until the invitation expires
        personal_message: Optional personal message from the inviter
        
    Returns:
        Success status (True if sent successfully)
    """
    logger.info(f"Preparing invitation email for {recipient_name} <{recipient_email}>")
    
    # Calculate expiry time for display
    expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)
    expiry_date = expiry_time.strftime("%B %d, %Y at %I:%M %p UTC")
    
    # Determine account type
    account_type = "administrator" if is_admin else "standard user"
    logger.info(f"User {recipient_name} will be invited as {account_type}")
    
    # Create email subject
    subject = f"Invitation to join {settings.APP.NAME}"
    
    # Create full invitation URL
    if not invitation_url.startswith(('http://', 'https://')):
        full_invitation_url = f"{settings.APP.SITE_URL}{invitation_url}"
    else:
        full_invitation_url = invitation_url
    
    logger.info(f"Invitation URL: {full_invitation_url}, expires: {expiry_date}")
    
    # Common context for both HTML and text templates
    context = {
        'recipient_name': recipient_name,
        'inviter_name': inviter_name,
        'account_type': account_type,
        'invitation_url': full_invitation_url,
        'expiry_date': expiry_date,
        'personal_message': personal_message
    }
    
    try:
        # Render content from templates
        logger.info(f"Rendering email templates for invitation to {recipient_name}")
        html_content = render_template("email/invitation.html", **context)
        text_content = render_text_template("email/invitation.html", **context)
        
        # Send the email
        result = send_email(recipient_email, subject, html_content, text_content)
        if result:
            logger.info(f"Invitation email to {recipient_name} <{recipient_email}> processed successfully")
        else:
            logger.error(f"Failed to send invitation email to {recipient_name} <{recipient_email}>")
        return result
    
    except Exception as e:
        logger.exception(f"Error preparing invitation email for {recipient_name}: {str(e)}")
        return False

def send_password_reset_email(recipient_email: str, recipient_name: str, reset_url: str) -> bool:
    """
    Send a password reset email.
    
    Args:
        recipient_email: User's email address
        recipient_name: User's name
        reset_url: URL to reset password
        
    Returns:
        Success status (True if sent successfully)
    """
    # Create full reset URL
    if not reset_url.startswith(('http://', 'https://')):
        full_reset_url = f"{settings.APP.SITE_URL}{reset_url}"
    else:
        full_reset_url = reset_url
    
    # Create subject
    subject = f"Password Reset - {settings.APP.NAME}"
    
    # Common context for both HTML and text templates
    context = {
        'recipient_name': recipient_name,
        'reset_url': full_reset_url
    }
    
    # Render content from templates
    html_content = render_template("email/password_reset.html", **context)
    text_content = render_text_template("email/password_reset.html", **context)
    
    return send_email(recipient_email, subject, html_content, text_content)

def send_notification_email(
    recipient_email: str,
    recipient_name: str,
    notification_title: str,
    notification_message: str,
    action_url: str = None,
    action_text: str = None,
    additional_details: str = None
) -> bool:
    """
    Send a notification email.
    
    Args:
        recipient_email: User's email address
        recipient_name: User's name
        notification_title: Title of the notification
        notification_message: Main notification message
        action_url: Optional URL for a call-to-action button
        action_text: Optional text for the call-to-action button
        additional_details: Optional additional details to include
        
    Returns:
        Success status (True if sent successfully)
    """
    # Create full action URL if provided
    full_action_url = None
    if action_url:
        if not action_url.startswith(('http://', 'https://')):
            full_action_url = f"{settings.APP.SITE_URL}{action_url}"
        else:
            full_action_url = action_url
    
    # Create subject
    subject = f"{notification_title} - {settings.APP.NAME}"
    
    # Common context for both HTML and text templates
    context = {
        'recipient_name': recipient_name,
        'notification_title': notification_title,
        'notification_message': notification_message,
        'action_url': full_action_url,
        'action_text': action_text,
        'additional_details': additional_details
    }
    
    # Render content from templates
    html_content = render_template("email/notification.html", **context)
    text_content = render_text_template("email/notification.html", **context)
    
    return send_email(recipient_email, subject, html_content, text_content) 