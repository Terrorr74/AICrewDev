#!/usr/bin/env python3
"""
Fixed LLM Configuration Module

This module provides configuration settings for different LLM providers
using CrewAI best practices. Updated based on latest Context7 documentation.
"""

from enum import Enum
from typing import Dict, Optional, Any, Union
import os
from pydantic import BaseModel, Field

# Import CrewAI's LLM class for better integration
CREWAI_AVAILABLE = False
CrewAI_LLM = None

try:
    from crewai import LLM as CrewAI_LLM
    CREWAI_AVAILABLE = True
except ImportError:
    pass

class LLMProvider(str, Enum):
    """Supported LLM providers for CrewAI integration"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class LLMConfig(BaseModel):
    """
    Configuration class for LLM settings with CrewAI integration.
    
    This class now prioritizes CrewAI's native LLM class for better integration
    while maintaining backward compatibility.
    """
    
    provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    model_name: str = Field(default="gpt-4o-mini")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    api_key: Optional[str] = Field(default=None)
    base_url: Optional[str] = Field(default=None)
    max_retries: int = Field(default=3, ge=0)
    max_rpm: Optional[int] = Field(default=None, gt=0)
    verbose: bool = Field(default=True)

    class Config:
        """Pydantic configuration"""
        use_enum_values = True

    @classmethod
    def get_default_config(cls) -> "LLMConfig":
        """
        Get default configuration from environment variables.
        
        Returns:
            LLMConfig: Configuration instance with environment-based values
        """
        # Get provider from environment with fallback
        provider_str = os.getenv("LLM_PROVIDER", "openai").lower()
        try:
            provider = LLMProvider(provider_str)
        except ValueError:
            print(f"Warning: Unknown provider '{provider_str}', falling back to OpenAI")
            provider = LLMProvider.OPENAI

        # Get model name with provider-specific defaults
        model_defaults = {
            LLMProvider.OPENAI: "gpt-4o-mini",
            LLMProvider.ANTHROPIC: "claude-3-haiku-20240307",
            LLMProvider.OLLAMA: "llama3.1:8b"
        }
        
        model_name = os.getenv("LLM_MODEL_NAME", model_defaults[provider])
        
        # Parse temperature with bounds checking
        try:
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
            temperature = max(0.0, min(2.0, temperature))  # Clamp between 0 and 2
        except (ValueError, TypeError):
            temperature = 0.7

        # Parse max_tokens
        max_tokens = None
        max_tokens_str = os.getenv("LLM_MAX_TOKENS")
        if max_tokens_str:
            try:
                max_tokens = int(max_tokens_str)
            except (ValueError, TypeError):
                pass

        # Get API keys from environment
        api_key = None
        if provider == LLMProvider.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider == LLMProvider.ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        # Parse other parameters
        verbose = os.getenv("LLM_VERBOSE", "true").lower() == "true"
        
        return cls(
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            verbose=verbose
        )

    def create_crewai_llm(self) -> Optional[Any]:
        """
        Create a CrewAI LLM instance using the new LLM class.
        This is the recommended approach for CrewAI integration.
        """
        if not CREWAI_AVAILABLE or CrewAI_LLM is None:
            return None
        
        try:
            # Build the model string in CrewAI format (provider/model)
            provider_str = self.provider if isinstance(self.provider, str) else self.provider.value
            model_string = f"{provider_str}/{self.model_name}"
            
            # Create configuration parameters
            llm_kwargs = {}
            
            if self.temperature is not None:
                llm_kwargs["temperature"] = self.temperature
            
            if self.max_tokens is not None:
                llm_kwargs["max_tokens"] = self.max_tokens
                
            if self.base_url is not None:
                llm_kwargs["base_url"] = self.base_url
                
            if self.api_key is not None:
                llm_kwargs["api_key"] = self.api_key
            
            # Create CrewAI LLM instance
            return CrewAI_LLM(
                model=model_string,
                **llm_kwargs
            )
        except Exception as e:
            print(f"Warning: Failed to create CrewAI LLM: {e}")
            return None

    def to_crewai_format(self) -> str:
        """
        Convert configuration to CrewAI LLM format string.
        
        Returns:
            str: Model string in format 'provider/model_name'
        """
        # provider is already a string when use_enum_values=True
        provider_str = self.provider if isinstance(self.provider, str) else self.provider.value
        return f"{provider_str}/{self.model_name}"

    def get_model_params_for_crewai(self) -> Dict[str, Any]:
        """
        Get model parameters in a format suitable for CrewAI Agent configuration.
        
        Returns:
            Dict[str, Any]: Parameters for CrewAI Agent LLM configuration
        """
        params = {}
        
        if self.temperature is not None:
            params["temperature"] = self.temperature
        
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        
        if self.max_rpm is not None:
            params["max_rpm"] = self.max_rpm
            
        if self.verbose is not None:
            params["verbose"] = self.verbose
            
        return params

    def get_provider_specific_config(self) -> Dict[str, Any]:
        """
        Get provider-specific configuration for advanced use cases.
        
        Returns:
            Dict[str, Any]: Provider-specific configuration parameters
        """
        config = {
            "provider": self.provider if isinstance(self.provider, str) else self.provider.value,
            "model": self.model_name,
            "temperature": self.temperature,
        }
        
        if self.api_key:
            config["api_key"] = self.api_key
            
        if self.base_url:
            config["base_url"] = self.base_url
            
        return config

# Export the main class and enum
__all__ = ["LLMConfig", "LLMProvider"]
