"""
Agent Factory Module

This module provides a factory for creating specialized AI agents with
specific roles and capabilities. Each agent is configured with specific
goals and backstories relevant to their role in the development process.

Classes:
    AgentFactory: Creates and configures AI agents for different roles

Example:
    >>> from src.config import LLMConfig
    >>> config = LLMConfig.get_default_config()
    >>> tech_lead = AgentFactory.create_tech_lead(config)
"""

from typing import Optional
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatOllama

from src.config import LLMConfig, LLMProvider

class AgentFactory:
    """
    Factory class for creating specialized AI agents.
    
    This class provides static methods to create different types of AI agents,
    each with specific roles, goals, and capabilities. The factory ensures
    consistent agent creation with appropriate configurations.
    """
    
    @staticmethod
    def _create_llm(config: LLMConfig):
        """Create LLM based on configuration"""
        if config.provider == LLMProvider.OLLAMA:
            return ChatOllama(
                model=config.model_name,
                temperature=config.temperature
            )
        elif config.provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                api_key=config.api_key,
                max_tokens=config.max_tokens
            )
        else:
            return ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                api_key=config.api_key,
                api_base=config.api_base,
                max_tokens=config.max_tokens
            )
    
    @staticmethod
    def create_tech_lead(config: Optional[LLMConfig] = None):
        """Create a Tech Lead agent"""
        if config is None:
            config = LLMConfig.get_default_config()
            
        llm = AgentFactory._create_llm(config)
        return Agent(
            role='Tech Lead',
            goal='Ensure technical excellence and project success',
            backstory='Experienced technical leader with focus on architecture and code quality',
            llm=llm
        )
    
    @staticmethod
    def create_developer(config: Optional[LLMConfig] = None):
        """Create a Developer agent"""
        if config is None:
            config = LLMConfig.get_default_config()
            
        llm = AgentFactory._create_llm(config)
        return Agent(
            role='Developer',
            goal='Write clean, efficient, and maintainable code',
            backstory='Skilled developer with strong problem-solving abilities',
            llm=llm
        )
    
    @staticmethod
    def create_code_reviewer(config: Optional[LLMConfig] = None):
        """Create a Code Reviewer agent"""
        if config is None:
            config = LLMConfig.get_default_config()
            
        llm = AgentFactory._create_llm(config)
        return Agent(
            role='Code Reviewer',
            goal='Ensure code quality and best practices',
            backstory='Detail-oriented developer with extensive experience in code review',
            llm=llm
        )
