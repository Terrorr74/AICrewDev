"""
Environment Management Module

This module handles environment configuration and validation for the AICrewDev
system. It manages environment variables, API keys, and ensures all required
configurations are present and valid.

Functions:
    load_environment: Loads and returns environment variables
    validate_environment: Ensures all required variables are set

Example:
    >>> from utils.environment import validate_environment
    >>> validate_environment()  # Raises error if configuration is invalid
"""

import os
from dotenv import load_dotenv

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
        >>> api_key = env["OPENAI_API_KEY"]
    """
    load_dotenv()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        # Add other environment variables as needed
    }

def validate_environment():
    """Validate required environment variables"""
    required_vars = ["OPENAI_API_KEY"]
    env = load_environment()
    
    missing_vars = [var for var in required_vars if not env.get(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    return True
