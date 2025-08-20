"""
Centralized settings management for AICrewDev.

This module provides a centralized configuration system that integrates
with the enhanced LLM configuration and environment management.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from src.config.llm_config import LLMConfig, LLMProvider

class Settings(BaseModel):
    """
    Centralized application settings using Pydantic BaseModel.
    
    This class manages all configuration aspects of the AICrewDev application,
    including LLM configuration, application behavior, and environment settings.
    """
    
    # Application Settings
    app_name: str = Field(default="AICrewDev", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")
    
    # Environment Settings
    environment: str = Field(default="development", description="Current environment")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Crew Configuration
    crew_verbose: bool = Field(default=True, description="Enable verbose crew output")
    max_agents: int = Field(default=10, ge=1, le=50, description="Maximum number of agents")
    max_tasks: int = Field(default=20, ge=1, le=100, description="Maximum number of tasks")
    
    # Performance Settings
    max_iterations: int = Field(default=25, ge=1, le=100, description="Maximum iterations per task")
    timeout_seconds: int = Field(default=300, ge=30, le=3600, description="Task timeout in seconds")
    
    # Feature Flags
    enable_code_execution: bool = Field(default=False, description="Enable code execution for agents")
    enable_delegation: bool = Field(default=True, description="Enable agent delegation")
    enable_memory: bool = Field(default=True, description="Enable agent memory")
    
    class Config:
        """Pydantic configuration."""
        env_prefix = "AICREWDEV_"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        """Initialize settings with environment variable loading."""
        # Load from environment variables with prefix
        env_data = {}
        for key in kwargs.keys():
            env_key = f"AICREWDEV_{key.upper()}"
            if env_key in os.environ:
                env_data[key] = os.environ[env_key]
        
        # Merge environment data with kwargs
        kwargs.update(env_data)
        super().__init__(**kwargs)
        self._llm_config: Optional[LLMConfig] = None
    
    @property
    def llm_config(self) -> LLMConfig:
        """
        Get the enhanced LLM configuration.
        
        Returns:
            LLMConfig: Configured LLM instance
        """
        if self._llm_config is None:
            self._llm_config = LLMConfig.get_default_config()
        return self._llm_config
    
    @llm_config.setter
    def llm_config(self, config: LLMConfig):
        """Set a custom LLM configuration."""
        self._llm_config = config
    
    def get_crew_config(self) -> dict:
        """
        Get configuration parameters for CrewAI Crew initialization.
        
        Returns:
            dict: Configuration parameters for Crew
        """
        return {
            "verbose": self.crew_verbose,
            "max_iterations": self.max_iterations,
            "memory": self.enable_memory,
        }
    
    def get_agent_defaults(self) -> dict:
        """
        Get default configuration parameters for agent creation.
        
        Returns:
            dict: Default agent configuration parameters
        """
        return {
            "verbose": self.crew_verbose,
            "allow_delegation": self.enable_delegation,
            "max_iter": self.max_iterations,
            "allow_code_execution": self.enable_code_execution,
        }
    
    def validate_environment(self) -> bool:
        """
        Validate that all required environment variables are set.
        
        Returns:
            bool: True if environment is valid
            
        Raises:
            ValueError: If required environment variables are missing
        """
        required_vars = []
        
        # Check LLM-specific requirements
        if self.llm_config.provider == LLMProvider.OPENAI:
            if not self.llm_config.api_key and not os.getenv("OPENAI_API_KEY"):
                required_vars.append("OPENAI_API_KEY")
        elif self.llm_config.provider == LLMProvider.ANTHROPIC:
            if not self.llm_config.api_key and not os.getenv("ANTHROPIC_API_KEY"):
                required_vars.append("ANTHROPIC_API_KEY")
        
        if required_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(required_vars)}")
        
        return True
    
    def get_info(self) -> dict:
        """
        Get application information summary.
        
        Returns:
            dict: Application information
        """
        return {
            "app_name": self.app_name,
            "version": self.version,
            "environment": self.environment,
            "debug": self.debug,
            "llm_provider": self.llm_config.provider,
            "llm_model": self.llm_config.model_name,
            "crew_verbose": self.crew_verbose,
            "max_agents": self.max_agents,
            "max_tasks": self.max_tasks,
        }
    
    @classmethod
    def for_development(cls) -> "Settings":
        """
        Create settings optimized for development environment.
        
        Returns:
            Settings: Development-optimized settings
        """
        return cls(
            environment="development",
            debug=True,
            log_level="DEBUG",
            crew_verbose=True,
            enable_code_execution=False,  # Safer for development
            timeout_seconds=600,  # Longer timeout for debugging
        )
    
    @classmethod
    def for_production(cls) -> "Settings":
        """
        Create settings optimized for production environment.
        
        Returns:
            Settings: Production-optimized settings
        """
        return cls(
            environment="production",
            debug=False,
            log_level="INFO",
            crew_verbose=False,  # Less verbose in production
            enable_code_execution=True,
            timeout_seconds=300,
            max_iterations=20,  # More conservative limits
        )

# Global settings instance
settings = Settings()

__all__ = ["Settings", "settings"]
