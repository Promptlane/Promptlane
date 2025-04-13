"""
SMTP email provider implementation
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
import os

from ..exceptions import (
    EmailConfigurationError,
    EmailAuthenticationError,
    EmailConnectionError,
    EmailSendError
)
from .base import BaseEmailProvider, EmailMessage

class SMTPProvider(BaseEmailProvider):
    """SMTP email provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        try:
            self.host = config.get("host", os.getenv("SMTP_HOST"))
            if not self.host:
                raise EmailConfigurationError("SMTP host not configured")
            
            self.port = int(config.get("port", os.getenv("SMTP_PORT", "587")))
            self.username = config.get("username", os.getenv("SMTP_USERNAME"))
            if not self.username:
                raise EmailConfigurationError("SMTP username not configured")
            
            self.password = config.get("password", os.getenv("SMTP_PASSWORD"))
            if not self.password:
                raise EmailConfigurationError("SMTP password not configured")
            
            self.use_tls = config.get("use_tls", True)
            self.default_sender = config.get("default_sender", os.getenv("SMTP_DEFAULT_SENDER"))
            if not self.default_sender:
                raise EmailConfigurationError("SMTP default sender not configured")
        except ValueError as e:
            raise EmailConfigurationError(f"Invalid SMTP configuration: {str(e)}")
    
    async def send_email(self, message: EmailMessage) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = message.sender or self.default_sender
            msg["To"] = message.recipient
            
            if message.reply_to:
                msg["Reply-To"] = message.reply_to
            if message.cc:
                msg["Cc"] = message.cc
            if message.bcc:
                msg["Bcc"] = message.bcc
            
            msg.attach(MIMEText(message.text_content, "plain"))
            msg.attach(MIMEText(message.html_content, "html"))
            
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except smtplib.SMTPAuthenticationError as e:
            raise EmailAuthenticationError("smtp", f"Authentication failed: {str(e)}")
        except smtplib.SMTPConnectError as e:
            raise EmailConnectionError("smtp", f"Connection failed: {str(e)}")
        except smtplib.SMTPException as e:
            raise EmailSendError("smtp", message.recipient, str(e))
        except Exception as e:
            raise EmailSendError("smtp", message.recipient, f"Unexpected error: {str(e)}")
    
    async def validate_credentials(self) -> bool:
        """Validate SMTP credentials"""
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
            return True
        except smtplib.SMTPAuthenticationError:
            raise EmailAuthenticationError("smtp", "Invalid credentials")
        except smtplib.SMTPConnectError:
            raise EmailConnectionError("smtp", "Could not connect to SMTP server")
        except Exception as e:
            raise EmailConnectionError("smtp", f"Unexpected error: {str(e)}")
    
    async def get_quota(self) -> Dict[str, Any]:
        """SMTP doesn't typically provide quota information"""
        return {
            "provider": "smtp",
            "quota_available": True
        } 