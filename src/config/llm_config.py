"""
LLM Configuration Module

This module provides configuration settings for different LLM providers
(Ollama, OpenAI, or other hosted models).
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel

class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    OTHER = "other"

class LLMConfig(BaseModel):
    """LLM Configuration settings"""
    provider: LLMProvider
    model_name: str
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.5
    max_tokens: Optional[int] = None

    @classmethod
    def get_default_config(cls) -> 'LLMConfig':
        """Get default LLM configuration from environment variables"""
        from src.utils.environment import get_env_var
        
        provider = get_env_var("LLM_PROVIDER", "ollama")
        model_name = get_env_var("LLM_MODEL_NAME", "llama2")
        api_base = get_env_var("LLM_API_BASE", None)
        api_key = get_env_var("LLM_API_KEY", None)
        temperature = float(get_env_var("LLM_TEMPERATURE", "0.5"))
        max_tokens = get_env_var("LLM_MAX_TOKENS", None)
        
        if max_tokens:
            max_tokens = int(max_tokens)
        
        return cls(
            provider=provider,
            model_name=model_name,
            api_base=api_base,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
