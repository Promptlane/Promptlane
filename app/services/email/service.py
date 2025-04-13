"""
Email service for managing multiple email providers.
"""
from typing import Dict, Any, Optional, TypeVar, Generic
import os
import asyncio
import time
from datetime import datetime

from app.logger import get_logger
from .exceptions import (
    EmailError,
    EmailProviderError,
    EmailConfigurationError,
    EmailAuthenticationError,
    EmailConnectionError,
    EmailSendError,
    EmailQuotaError
)
from .providers.base import BaseEmailProvider, EmailMessage
from .providers.smtp import SMTPProvider
from .providers.aws_ses import AWSSESProvider
from app.services.template import render_template

logger = get_logger(__name__)

# Configuration examples for documentation
CONFIG_EXAMPLES = {
    "smtp": {
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "user@gmail.com",
        "password": "app_password",
        "use_tls": True,
        "default_sender": "user@gmail.com"
    },
    "aws_ses": {
        "region": "us-east-1",
        "access_key": "AKIA...",
        "secret_key": "secret...",
        "default_sender": "verified@domain.com"
    }
}

class EmailService:
    """
    Email service for managing multiple email providers.
    
    Example:
        email_service = EmailService({
            "default_provider": "aws_ses",
            "dev_mode": True,
            "providers": {
                "aws_ses": {
                    "region": "us-east-1",
                    "access_key": "...",
                    "secret_key": "..."
                }
            }
        })
    """
    
    def __init__(self, config: Dict[str, Any]):
        self._validate_config(config)
        self.providers: Dict[str, BaseEmailProvider] = {}
        self.default_provider = config.get("default_provider", "smtp")
        self.dev_mode = config.get("dev_mode", False)
        self.dev_save_path = config.get("dev_save_path", "dev/emails")
        
        # Initialize providers
        for provider_type, provider_config in config.get("providers", {}).items():
            self.providers[provider_type] = self._create_provider(provider_type, provider_config)
        
        if not self.providers:
            raise EmailConfigurationError("No email providers configured")
        
        if self.default_provider not in self.providers:
            raise EmailConfigurationError(f"Default provider {self.default_provider} not configured")
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the email service configuration."""
        required_fields = ["providers"]
        for field in required_fields:
            if field not in config:
                raise EmailConfigurationError(f"Missing required field: {field}")
        
        if not isinstance(config["providers"], dict):
            raise EmailConfigurationError("Providers must be a dictionary")
        
        if not config["providers"]:
            raise EmailConfigurationError("At least one provider must be configured")
    
    def _create_provider(self, provider_type: str, config: Dict[str, Any]) -> BaseEmailProvider:
        """Create a provider instance based on type."""
        provider_map = {
            "smtp": SMTPProvider,
            "aws_ses": AWSSESProvider
        }
        
        if provider_type not in provider_map:
            raise EmailConfigurationError(f"Unknown provider type: {provider_type}")
        
        try:
            return provider_map[provider_type](config)
        except Exception as e:
            raise EmailConfigurationError(f"Failed to initialize {provider_type} provider: {str(e)}")
    
    async def send_email(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Send an email using the specified provider."""
        start_time = time.time()
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            logger.error(f"Email provider {provider_name} not configured")
            return False
        
        # Create email message
        message = EmailMessage(
            recipient=recipient,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            **kwargs
        )
        
        # In development mode, save email to file
        if self.dev_mode:
            try:
                await self._save_email_to_file(message)
                return True
            except Exception as e:
                logger.error(f"Failed to save email to file: {str(e)}")
                return False
        
        # Send email using provider
        try:
            success = await self.providers[provider_name].send_email(message)
            duration = time.time() - start_time
            
            if success:
                logger.info(f"Email sent successfully to {recipient} using {provider_name} (took {duration:.2f}s)")
            else:
                logger.error(f"Failed to send email to {recipient} using {provider_name}")
            
            return success
        except EmailAuthenticationError as e:
            logger.error(f"Authentication error with {provider_name}: {str(e)}")
            return False
        except EmailConnectionError as e:
            logger.error(f"Connection error with {provider_name}: {str(e)}")
            return False
        except EmailQuotaError as e:
            logger.error(f"Quota exceeded for {provider_name}: {str(e)}")
            return False
        except EmailSendError as e:
            logger.error(f"Failed to send email using {provider_name}: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error sending email: {str(e)}")
            return False
    
    async def send_email_with_retry(
        self,
        recipient: str,
        subject: str,
        html_content: str,
        text_content: str,
        max_retries: int = 3,
        delay: float = 1.0,
        provider: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Send an email with retry mechanism."""
        for attempt in range(max_retries):
            try:
                return await self.send_email(
                    recipient=recipient,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    provider=provider,
                    **kwargs
                )
            except EmailConnectionError:
                if attempt < max_retries - 1:
                    logger.warning(f"Retrying email send (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    continue
                raise
    
    async def send_template_email(
        self,
        template_name: str,
        recipient: str,
        context: Dict[str, Any],
        provider: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Send an email using a template."""
        try:
            html_content = render_template(f"{template_name}.html", **context)
            text_content = render_template(f"{template_name}.txt", **context)
            
            return await self.send_email(
                recipient=recipient,
                subject=context.get("subject", "No Subject"),
                html_content=html_content,
                text_content=text_content,
                provider=provider,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            return False
    
    async def _save_email_to_file(self, message: EmailMessage) -> None:
        """Save email to file in development mode."""
        try:
            os.makedirs(self.dev_save_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.dev_save_path}/email_{timestamp}_{message.recipient}.html"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"To: {message.recipient}\n")
                f.write(f"Subject: {message.subject}\n")
                f.write(f"HTML Content:\n{message.html_content}\n")
                f.write(f"Text Content:\n{message.text_content}\n")
            
            logger.info(f"Email saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save email to file: {str(e)}")
            raise
    
    async def validate_provider(self, provider_name: str) -> bool:
        """Validate provider credentials."""
        if provider_name not in self.providers:
            logger.error(f"Provider {provider_name} not configured")
            return False
        
        try:
            return await self.providers[provider_name].validate_credentials()
        except EmailAuthenticationError as e:
            logger.error(f"Authentication error with {provider_name}: {str(e)}")
            return False
        except EmailConnectionError as e:
            logger.error(f"Connection error with {provider_name}: {str(e)}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error validating {provider_name}: {str(e)}")
            return False
    
    async def get_provider_quota(self, provider_name: str) -> Dict[str, Any]:
        """Get provider quota information."""
        if provider_name not in self.providers:
            return {"error": f"Provider {provider_name} not configured"}
        
        try:
            return await self.providers[provider_name].get_quota()
        except EmailQuotaError as e:
            logger.error(f"Quota error with {provider_name}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.exception(f"Unexpected error getting quota for {provider_name}: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"} 