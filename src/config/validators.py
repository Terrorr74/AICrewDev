#!/usr/bin/env python3
"""
Enhanced Configuration Validation Module

This module provides comprehensive validation for AICrewDev configurations
using Pydantic v2 with custom validators and error handling.
"""

import re
import os
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum
from pathlib import Path

# Try to import optional dependencies
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class ValidationError(Exception):
    """Custom validation error for AICrewDev configurations"""
    pass


class LLMProviderError(ValidationError):
    """Raised when LLM provider configuration is invalid"""
    pass


class DockerError(ValidationError):
    """Raised when Docker configuration is invalid"""
    pass


class EnvironmentError(ValidationError):
    """Raised when environment configuration is invalid"""
    pass


class LLMProvider(str, Enum):
    """Supported LLM providers for CrewAI integration"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    GEMINI = "gemini"


class ProjectType(str, Enum):
    """Supported project types"""
    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATA = "data"
    FULLSTACK = "fullstack"


class AgentRole(str, Enum):
    """Supported agent roles"""
    TECH_LEAD = "tech_lead"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    MANAGER = "manager"
    ANALYST = "analyst"


class LLMConfigValidator(BaseModel):
    """Enhanced LLM configuration validator with comprehensive checks"""
    
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    model_name: str = Field(min_length=1, max_length=100)
    temperature: float = Field(ge=0.0, le=2.0, default=0.7)
    max_tokens: Optional[int] = Field(gt=0, le=100000, default=None)
    api_key: Optional[str] = Field(min_length=10, default=None)
    base_url: Optional[str] = Field(default=None)
    max_retries: int = Field(ge=0, le=10, default=3)
    max_rpm: Optional[int] = Field(gt=0, le=10000, default=None)
    timeout: int = Field(gt=0, le=300, default=60)
    verbose: bool = Field(default=True)

    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v: str, info) -> str:
        """Validate model name based on provider"""
        # Get provider from values if available
        provider = info.data.get('provider') if info.data else None
        
        # Provider-specific model validation
        valid_models = {
            LLMProvider.OPENAI: [
                'gpt-4', 'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 
                'gpt-4-turbo', 'gpt-4-turbo-preview'
            ],
            LLMProvider.ANTHROPIC: [
                'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku',
                'claude-3-5-sonnet', 'claude-2'
            ],
            LLMProvider.OLLAMA: [
                'llama2', 'llama3.1:8b', 'llama3.1:70b', 'codellama',
                'mistral', 'mixtral'
            ],
            LLMProvider.GROQ: [
                'llama-3.1-70b-versatile', 'llama-3.1-8b-instant',
                'mixtral-8x7b-32768'
            ]
        }
        
        if provider and provider in valid_models:
            # Check if it's an exact match or pattern match
            valid_patterns = valid_models[provider]
            is_valid = any(
                v == pattern or v.startswith(pattern.split(':')[0]) 
                for pattern in valid_patterns
            )
            
            if not is_valid:
                raise ValueError(
                    f"Invalid model '{v}' for provider '{provider}'. "
                    f"Valid models: {valid_patterns}"
                )
        
        return v

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: Optional[str], info) -> Optional[str]:
        """Validate API key format and requirements"""
        provider = info.data.get('provider') if info.data else None
        
        # Check if API key is required for the provider
        if provider in ['openai', 'anthropic', 'groq']:
            if not v:
                # Try to get from environment
                env_keys = {
                    'openai': 'OPENAI_API_KEY',
                    'anthropic': 'ANTHROPIC_API_KEY',
                    'groq': 'GROQ_API_KEY'
                }
                env_key_name = env_keys.get(str(provider), '')
                env_key = os.getenv(env_key_name) if env_key_name else None
                if not env_key:
                    raise ValueError(f"API key is required for provider '{provider}'")
                return env_key
            
            # Basic format validation
            if provider == 'openai' and not v.startswith('sk-'):
                raise ValueError("OpenAI API key must start with 'sk-'")
            
            if provider == 'anthropic' and len(v) < 20:
                raise ValueError("Anthropic API key seems too short")
        
        return v

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate base URL format"""
        if v:
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE
            )
            
            if not url_pattern.match(v):
                raise ValueError(f"Invalid URL format: {v}")
        
        return v

    @model_validator(mode='after')
    def validate_provider_config(self):
        """Cross-field validation for provider-specific configurations"""
        provider = self.provider
        
        # Ollama-specific validation
        if provider == LLMProvider.OLLAMA:
            if not self.base_url:
                self.base_url = "http://localhost:11434"
            elif "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
                raise ValueError("Ollama typically runs on localhost")
        
        return self


class AgentConfigValidator(BaseModel):
    """Agent configuration validator"""
    
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True
    )
    
    role: AgentRole
    goal: str = Field(min_length=10, max_length=500)
    backstory: str = Field(min_length=20, max_length=1000)
    allow_delegation: bool = Field(default=False)
    allow_code_execution: bool = Field(default=False)
    code_execution_mode: str = Field(default="safe", pattern="^(safe|unsafe)$")
    max_iter: int = Field(ge=1, le=100, default=20)
    max_execution_time: Optional[int] = Field(gt=0, le=3600, default=None)
    max_retry_limit: int = Field(ge=0, le=10, default=2)
    verbose: bool = Field(default=True)
    memory: bool = Field(default=False)
    reasoning: bool = Field(default=False)
    max_reasoning_attempts: Optional[int] = Field(ge=1, le=10, default=None)

    @field_validator('goal')
    @classmethod
    def validate_goal(cls, v: str) -> str:
        """Validate goal contains action verbs"""
        action_verbs = [
            'analyze', 'create', 'develop', 'implement', 'design', 
            'review', 'test', 'coordinate', 'manage', 'research',
            'write', 'build', 'optimize', 'monitor', 'evaluate'
        ]
        
        if not any(verb in v.lower() for verb in action_verbs):
            raise ValueError(
                f"Goal should contain at least one action verb: {action_verbs}"
            )
        
        return v

    @field_validator('backstory')
    @classmethod
    def validate_backstory(cls, v: str) -> str:
        """Validate backstory provides sufficient context"""
        # Check for experience indicators
        experience_words = [
            'experience', 'expert', 'skilled', 'specialist', 'veteran',
            'seasoned', 'proficient', 'years', 'background'
        ]
        
        if not any(word in v.lower() for word in experience_words):
            raise ValueError(
                "Backstory should include experience or expertise indicators"
            )
        
        return v

    @model_validator(mode='after')
    def validate_code_execution(self):
        """Validate code execution configuration"""
        if self.allow_code_execution and self.code_execution_mode == "unsafe":
            raise ValueError(
                "Unsafe code execution mode is not recommended. Use 'safe' mode."
            )
        
        if self.allow_code_execution and DOCKER_AVAILABLE:
            # Check if Docker is available
            try:
                import docker as docker_lib
                docker_client = docker_lib.from_env()
                docker_client.ping()
            except Exception as e:
                raise ValidationError(
                    f"Docker is required for code execution but is not available: {e}"
                )
        
        return self


class ProjectConfigValidator(BaseModel):
    """Project configuration validator"""
    
    model_config = ConfigDict(validate_assignment=True)
    
    name: str = Field(min_length=1, max_length=100, pattern="^[a-zA-Z0-9_-]+$")
    type: ProjectType
    description: str = Field(min_length=10, max_length=500)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$", default="1.0.0")
    environment: str = Field(pattern="^(development|staging|production)$", default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", default="INFO")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate project name follows conventions"""
        if v.startswith('-') or v.endswith('-'):
            raise ValueError("Project name cannot start or end with hyphen")
        
        if '__' in v:
            raise ValueError("Project name cannot contain double underscores")
        
        return v


class DockerConfigValidator(BaseModel):
    """Docker configuration validator"""
    
    model_config = ConfigDict(validate_assignment=True)
    
    enabled: bool = Field(default=True)
    image: str = Field(default="python:3.11-slim")
    timeout: int = Field(ge=30, le=600, default=300)
    memory_limit: str = Field(pattern=r"^\d+[mMgG]$", default="512m")
    cpu_limit: float = Field(ge=0.1, le=8.0, default=1.0)

    @field_validator('image')
    @classmethod
    def validate_image(cls, v: str) -> str:
        """Validate Docker image format"""
        image_pattern = re.compile(
            r'^(?:[a-z0-9]+(?:[._-][a-z0-9]+)*\/)?'  # optional registry
            r'[a-z0-9]+(?:[._-][a-z0-9]+)*'  # repository
            r'(?::[a-z0-9]+(?:[._-][a-z0-9]+)*)?$'  # optional tag
        )
        
        if not image_pattern.match(v):
            raise ValueError(f"Invalid Docker image format: {v}")
        
        return v

    @model_validator(mode='after')
    def validate_docker_availability(self):
        """Check if Docker is available when enabled"""
        if self.enabled and DOCKER_AVAILABLE:
            try:
                import docker as docker_lib
                docker_client = docker_lib.from_env()
                docker_client.ping()
            except Exception as e:
                raise DockerError(
                    f"Docker is enabled but not available: {e}. "
                    "Please install and start Docker Desktop."
                )
        elif self.enabled and not DOCKER_AVAILABLE:
            raise DockerError(
                "Docker is enabled but docker library is not installed. "
                "Run: pip install docker"
            )
        
        return self


class EnvironmentConfigValidator(BaseModel):
    """Environment configuration validator"""
    
    model_config = ConfigDict(validate_assignment=True)
    
    required_env_vars: List[str] = Field(default_factory=list)
    optional_env_vars: List[str] = Field(default_factory=list)
    check_disk_space: bool = Field(default=True)
    min_disk_space_gb: float = Field(ge=1.0, le=1000.0, default=5.0)
    check_memory: bool = Field(default=True)
    min_memory_gb: float = Field(ge=1.0, le=64.0, default=4.0)

    @field_validator('required_env_vars')
    @classmethod
    def validate_required_env_vars(cls, v: List[str]) -> List[str]:
        """Check that required environment variables are set"""
        missing_vars = []
        
        for var in v:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {missing_vars}"
            )
        
        return v

    @model_validator(mode='after')
    def validate_system_resources(self):
        """Validate system resources"""
        if not PSUTIL_AVAILABLE:
            return self
            
        import psutil
        
        # Check disk space
        if self.check_disk_space:
            try:
                disk_usage = psutil.disk_usage('/')
                free_gb = disk_usage.free / (1024**3)
                
                if free_gb < self.min_disk_space_gb:
                    raise EnvironmentError(
                        f"Insufficient disk space: {free_gb:.1f}GB available, "
                        f"{self.min_disk_space_gb}GB required"
                    )
            except Exception:
                # Ignore disk space check errors on some systems
                pass
        
        # Check memory
        if self.check_memory:
            try:
                memory = psutil.virtual_memory()
                available_gb = memory.available / (1024**3)
                
                if available_gb < self.min_memory_gb:
                    raise EnvironmentError(
                        f"Insufficient memory: {available_gb:.1f}GB available, "
                        f"{self.min_memory_gb}GB required"
                    )
            except Exception:
                # Ignore memory check errors on some systems
                pass
        
        return self


class ComprehensiveConfigValidator(BaseModel):
    """Comprehensive configuration validator that combines all validators"""
    
    model_config = ConfigDict(validate_assignment=True)
    
    llm: LLMConfigValidator
    project: ProjectConfigValidator
    docker: DockerConfigValidator = Field(default_factory=DockerConfigValidator)
    environment: EnvironmentConfigValidator = Field(default_factory=EnvironmentConfigValidator)
    agents: Dict[str, AgentConfigValidator] = Field(default_factory=dict)

    @model_validator(mode='after')
    def validate_overall_config(self):
        """Perform cross-validator checks"""
        # Check if any agent requires code execution but Docker is disabled
        if not self.docker.enabled:
            code_execution_agents = [
                name for name, config in self.agents.items() 
                if config.allow_code_execution
            ]
            
            if code_execution_agents:
                raise ValidationError(
                    f"Agents {code_execution_agents} require code execution "
                    "but Docker is disabled"
                )
        
        # Check LLM provider compatibility with agent roles
        provider = self.llm.provider
        
        # Some providers might not be suitable for certain roles
        if provider == LLMProvider.OLLAMA:
            # Ollama might be slower for time-sensitive operations
            manager_agents = [
                name for name, config in self.agents.items()
                if config.role == AgentRole.MANAGER
            ]
            
            if manager_agents and len(manager_agents) > 2:
                # This is a warning, not an error
                print(
                    f"Warning: Using Ollama with many manager agents "
                    f"({manager_agents}) might be slower"
                )
        
        return self


# Utility functions for validation
def validate_config_file(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate a configuration file (YAML or JSON)
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict containing validated configuration
        
    Raises:
        ValidationError: If configuration is invalid
    """
    try:
        import yaml
    except ImportError:
        raise ValidationError("PyYAML is required for YAML configuration files")
    
    import json
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise ValidationError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                raise ValidationError(f"Unsupported file format: {config_path.suffix}")
        
        # Validate using comprehensive validator
        validator = ComprehensiveConfigValidator(**config_data)
        return validator.model_dump()
        
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML format: {e}")
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValidationError(f"Configuration validation failed: {e}")


def create_default_config() -> Dict[str, Any]:
    """
    Create a default configuration with all validators
    
    Returns:
        Dict containing default configuration
    """
    return {
        "llm": {
            "provider": "openai",
            "model_name": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 2048,
            "verbose": True
        },
        "project": {
            "name": "aicrewdev-project",
            "type": "web",
            "description": "AI-powered development team project",
            "version": "1.0.0",
            "environment": "development"
        },
        "docker": {
            "enabled": True,
            "image": "python:3.11-slim",
            "timeout": 300,
            "memory_limit": "512m"
        },
        "environment": {
            "required_env_vars": [],
            "check_disk_space": True,
            "min_disk_space_gb": 5.0,
            "check_memory": True,
            "min_memory_gb": 4.0
        },
        "agents": {
            "tech_lead": {
                "role": "tech_lead",
                "goal": "Provide strategic technical leadership and coordinate development efforts",
                "backstory": "Expert technical leader with 10+ years of experience in software architecture and team management",
                "allow_delegation": True,
                "verbose": True
            },
            "developer": {
                "role": "developer", 
                "goal": "Implement high-quality code following best practices",
                "backstory": "Skilled developer with extensive experience in modern programming practices",
                "allow_code_execution": True,
                "verbose": True
            }
        }
    }


# Export main classes and functions
__all__ = [
    'LLMConfigValidator',
    'AgentConfigValidator', 
    'ProjectConfigValidator',
    'DockerConfigValidator',
    'EnvironmentConfigValidator',
    'ComprehensiveConfigValidator',
    'ValidationError',
    'LLMProviderError',
    'DockerError',
    'EnvironmentError',
    'validate_config_file',
    'create_default_config'
]
