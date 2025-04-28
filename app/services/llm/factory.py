from typing import Dict, Type
from .base import BaseLLMService
from .openai_service import OpenAIService
from .anthropic_service import AnthropicService

class LLMServiceFactory:
    """Factory for creating and managing LLM services"""
    
    _services: Dict[str, Type[BaseLLMService]] = {
        "openai": OpenAIService,
        "anthropic": AnthropicService
    }
    
    _instances: Dict[str, BaseLLMService] = {}
    
    @classmethod
    def get_service(cls, provider: str) -> BaseLLMService:
        """Get an instance of the specified LLM service
        
        Args:
            provider: The provider name (e.g., 'openai', 'anthropic')
            
        Returns:
            BaseLLMService: An instance of the requested service
            
        Raises:
            ValueError: If the provider is not supported
        """
        if provider not in cls._services:
            raise ValueError(f"Unsupported provider: {provider}")
            
        if provider not in cls._instances:
            cls._instances[provider] = cls._services[provider]()
            
        return cls._instances[provider]
    
    @classmethod
    def get_all_services(cls) -> Dict[str, BaseLLMService]:
        """Get all available LLM services
        
        Returns:
            Dict[str, BaseLLMService]: Dictionary of provider name to service instance
        """
        return {
            provider: cls.get_service(provider)
            for provider in cls._services
        }
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available providers
        
        Returns:
            list[str]: List of provider names
        """
        return list(cls._services.keys()) 