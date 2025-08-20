"""
Environment Management Module

This module handles environment configuration and validation for the AICrewDev
system. It manages environment variables, API keys, and ensures all required
configurations are present and valid.

Functions:
    load_environment: Loads and returns environment variables
    validate_environment: Ensures all required variables are set
    get_env_var: Get an environment variable with a default value

Example:
    >>> from utils.environment import validate_environment
    >>> validate_environment()  # Raises error if configuration is invalid
"""

import os
from typing import Any, Optional
from dotenv import load_dotenv

def get_env_var(key: str, default: Any = None) -> Optional[str]:
    """
    Get an environment variable with a default value.
    
    Args:
        key: The environment variable name
        default: Default value if not found
        
    Returns:
        The environment variable value or default
    """
    return os.getenv(key, default)

def load_environment():
    """
    Load environment variables from .env file.
    
    This function loads environment variables from a .env file and
    returns them as a dictionary. It's used to configure the application
    with necessary API keys and settings.
    
    Returns:
        dict: Dictionary containing environment variables
        
    Example:
        >>> env = load_environment()
        >>> api_key = env.get("OPENAI_API_KEY")
    """
    load_dotenv()
    return {
        "LLM_PROVIDER": get_env_var("LLM_PROVIDER", "ollama"),
        "LLM_MODEL_NAME": get_env_var("LLM_MODEL_NAME", "llama2"),
        "LLM_API_BASE": get_env_var("LLM_API_BASE"),
        "LLM_API_KEY": get_env_var("LLM_API_KEY"),
        "LLM_TEMPERATURE": get_env_var("LLM_TEMPERATURE", "0.7"),
        "LLM_MAX_TOKENS": get_env_var("LLM_MAX_TOKENS"),
    }

def validate_environment():
    """Validate required environment variables"""
    env = load_environment()
    provider = env.get("LLM_PROVIDER", "").lower()
    
    if provider == "openai" and not env.get("LLM_API_KEY"):
        raise EnvironmentError("OpenAI provider requires LLM_API_KEY")
    elif provider == "other" and not (env.get("LLM_API_BASE") and env.get("LLM_API_KEY")):
        raise EnvironmentError("Other providers require both LLM_API_BASE and LLM_API_KEY")
    
    return True
