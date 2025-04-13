"""
Base email provider interface for Promptlane.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime

T = TypeVar('T')

@dataclass
class EmailMessage:
    """Email message data class"""
    recipient: str
    subject: str
    html_content: str
    text_content: str
    sender: Optional[str] = None
    cc: Optional[list[str]] = None
    bcc: Optional[list[str]] = None
    reply_to: Optional[str] = None
    attachments: Optional[list[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.utcnow()

class BaseEmailProvider(ABC, Generic[T]):
    """
    Abstract base class for email providers.
    
    This class defines the interface that all email providers must implement.
    It uses generics to allow providers to specify their configuration type.
    
    Example:
        class MyProvider(BaseEmailProvider[MyConfig]):
            def __init__(self, config: MyConfig):
                self.config = config
    """
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        """
        Send an email message.
        
        Args:
            message: The email message to send
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
            
        Raises:
            EmailSendError: If there was an error sending the email
            EmailAuthenticationError: If there was an authentication error
            EmailConnectionError: If there was a connection error
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate the provider's credentials.
        
        Returns:
            bool: True if the credentials are valid, False otherwise
            
        Raises:
            EmailAuthenticationError: If the credentials are invalid
            EmailConnectionError: If there was a connection error
        """
        pass
    
    @abstractmethod
    async def get_quota(self) -> Dict[str, Any]:
        """
        Get the provider's quota information.
        
        Returns:
            Dict[str, Any]: Dictionary containing quota information
            
        Raises:
            EmailQuotaError: If there was an error getting quota information
        """
        pass 