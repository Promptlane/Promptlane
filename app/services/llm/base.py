from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Response from LLM service"""
    content: str
    usage: Dict[str, int]
    model: str
    provider: str

class BaseLLMService(ABC):
    """Base interface for LLM services"""
    
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        presence_penalty: float,
        frequency_penalty: float,
        response_format: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM
        
        Args:
            system_prompt: The system prompt to use
            user_prompt: The user prompt to use
            model: The model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            presence_penalty: Presence penalty parameter
            frequency_penalty: Frequency penalty parameter
            response_format: Optional response format (e.g., 'json')
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse: The response from the LLM
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> list[Dict[str, Any]]:
        """Get list of available models and their capabilities
        
        Returns:
            list[Dict[str, Any]]: List of available models
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider
        
        Returns:
            str: Provider name
        """
        pass 