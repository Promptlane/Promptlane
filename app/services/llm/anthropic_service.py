import os
from typing import Dict, Any, Optional
import anthropic
from .base import BaseLLMService, LLMResponse
from ...managers.llm_model_manager import LLMModelManager

class AnthropicService(BaseLLMService):
    """Anthropic LLM service implementation"""
    
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self._available_models = None
        self.model_manager = LLMModelManager()
    
    def get_provider_name(self) -> str:
        return "Anthropic"
    
    async def get_available_models(self) -> list[Dict[str, Any]]:
        if self._available_models is None:
            # Get models using the manager
            models = self.model_manager.get_models_by_provider("Anthropic")
            
            self._available_models = [
                {
                    "model_id": model.model_id,
                    "name": model.name,
                    "provider": model.provider,
                    "description": model.description,
                    "context_length": model.context_length,
                    "completion_length": model.completion_length,
                    "prompt_price": model.prompt_price,
                    "completion_price": model.completion_price
                }
                for model in models
            ]
        return self._available_models
    
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        response_format: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            system=system_prompt,
            messages=messages,
            **kwargs
        )
        
        return LLMResponse(
            content=response.content[0].text,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            model=model,
            provider="Anthropic"
        ) 