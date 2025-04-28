import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from .base import BaseLLMService, LLMResponse
from ...managers.llm_model_manager import LLMModelManager

class OpenAIService(BaseLLMService):
    """OpenAI LLM service implementation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self._available_models = None
        self.model_manager = LLMModelManager()
    
    def get_provider_name(self) -> str:
        return "OpenAI"
    
    async def get_available_models(self) -> list[Dict[str, Any]]:
        if self._available_models is None:
            # Get models using the manager
            models = self.model_manager.get_models_by_provider("OpenAI")
            
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
        presence_penalty: float,
        frequency_penalty: float,
        response_format: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_format_dict = {"type": response_format} if response_format else None
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            response_format=response_format_dict,
            **kwargs
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            model=model,
            provider="OpenAI"
        ) 