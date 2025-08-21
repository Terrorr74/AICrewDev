"""
Agent Factory Module - Fixed Version

This module provides a factory for creating specialized AI agents with
specific roles and capabilities using CrewAI best practices. Updated
based on latest Context7 documentation.
"""

from typing import Optional, List, Dict, Any
from crewai import Agent

# Import from the fixed config
from src.config.llm_config import LLMConfig, LLMProvider

class AgentFactory:
    """
    Factory for creating specialized AI agents with role-specific configurations.
    
    This factory creates agents optimized for different roles by:
    - Using role-appropriate LLM configurations
    - Setting optimal temperature and parameters for each role
    - Applying CrewAI best practices for agent design
    """

    @staticmethod
    def _optimize_config_for_role(config: LLMConfig, role: str) -> LLMConfig:
        """
        Optimize LLM configuration for specific agent roles.
        
        Args:
            config: Base LLM configuration
            role: Agent role (manager, developer, reviewer, etc.)
            
        Returns:
            LLMConfig: Role-optimized configuration
        """
        # Create a copy of the config to avoid modifying the original
        optimized = LLMConfig(**config.model_dump())
        
        # Role-specific temperature optimization
        if role.lower() in ["manager", "lead", "coordinator"]:
            # Lower temperature for consistent, strategic thinking
            optimized.temperature = 0.1
        elif role.lower() in ["developer", "engineer", "programmer"]:
            # Balanced temperature for creative problem-solving
            optimized.temperature = 0.3
        elif role.lower() in ["reviewer", "analyst", "quality"]:
            # Lower temperature for accuracy and consistency
            optimized.temperature = 0.2
        elif role.lower() in ["writer", "content", "creative"]:
            # Higher temperature for creativity
            optimized.temperature = 0.7
        
        return optimized

    @staticmethod
    def create_tech_lead(
        config: LLMConfig,
        tools: Optional[List[Any]] = None
    ) -> Agent:
        """
        Create a Technical Lead agent optimized for strategic planning and coordination.
        
        Args:
            config: LLM configuration
            tools: Optional list of tools for the agent
            
        Returns:
            Agent: Configured Technical Lead agent
        """
        # Optimize configuration for management role
        optimized_config = AgentFactory._optimize_config_for_role(config, "manager")
        
        # Create CrewAI LLM instance
        llm = optimized_config.create_crewai_llm()
        
        # Fallback to string format if CrewAI LLM creation fails
        if llm is None:
            llm = optimized_config.to_crewai_format()
        
        agent_kwargs = {
            "role": "Technical Lead and Strategy Manager",
            "goal": "Provide strategic technical leadership, coordinate team efforts, and ensure project success through effective planning and decision-making",
            "backstory": """You are an experienced technical leader with deep expertise in software 
            architecture, team management, and strategic planning. You excel at breaking down complex 
            projects, identifying risks, and coordinating cross-functional teams to deliver high-quality 
            solutions on time.""",
            "llm": llm,
            "verbose": optimized_config.verbose,
            "allow_delegation": True,  # Enable collaboration tools
            "max_iter": 25,  # More iterations for complex strategic thinking
            "max_execution_time": None,  # No timeout for complex decisions
        }
        
        if tools:
            agent_kwargs["tools"] = tools
            
        return Agent(**agent_kwargs)

    @staticmethod
    def create_developer(
        config: LLMConfig,
        specialization: str = "fullstack",
        tools: Optional[List[Any]] = None
    ) -> Agent:
        """
        Create a Developer agent optimized for coding and implementation.
        
        Args:
            config: LLM configuration
            specialization: Developer specialization (frontend, backend, fullstack, etc.)
            tools: Optional list of tools for the agent
            
        Returns:
            Agent: Configured Developer agent
        """
        # Optimize configuration for development role
        optimized_config = AgentFactory._optimize_config_for_role(config, "developer")
        
        # Create CrewAI LLM instance
        llm = optimized_config.create_crewai_llm()
        
        # Fallback to string format if CrewAI LLM creation fails
        if llm is None:
            llm = optimized_config.to_crewai_format()
        
        # Customize role based on specialization
        specialization_mapping = {
            "frontend": "Frontend Developer",
            "backend": "Backend Developer", 
            "fullstack": "Full-Stack Developer",
            "mobile": "Mobile Developer",
            "devops": "DevOps Engineer",
            "data": "Data Engineer"
        }
        
        role = specialization_mapping.get(specialization.lower(), f"{specialization.title()} Developer")
        
        agent_kwargs = {
            "role": role,
            "goal": f"Write high-quality, maintainable code and implement features following best practices for {specialization} development",
            "backstory": f"""You are a skilled {specialization} developer with extensive experience in 
            modern development practices, testing, and code quality. You write clean, efficient code and 
            stay up-to-date with the latest technologies and frameworks in {specialization} development.""",
            "llm": llm,
            "verbose": optimized_config.verbose,
            "allow_delegation": False,  # Developers should focus on their expertise
            "allow_code_execution": True,
            "max_iter": 20,
            "max_execution_time": None,
        }
        
        if tools:
            agent_kwargs["tools"] = tools
            
        return Agent(**agent_kwargs)

    @staticmethod
    def create_code_reviewer(
        config: LLMConfig,
        tools: Optional[List[Any]] = None
    ) -> Agent:
        """
        Create a Code Reviewer agent optimized for quality assurance and analysis.
        
        Args:
            config: LLM configuration
            tools: Optional list of tools for the agent
            
        Returns:
            Agent: Configured Code Reviewer agent
        """
        # Optimize configuration for review role
        optimized_config = AgentFactory._optimize_config_for_role(config, "reviewer")
        
        # Create CrewAI LLM instance
        llm = optimized_config.create_crewai_llm()
        
        # Fallback to string format if CrewAI LLM creation fails
        if llm is None:
            llm = optimized_config.to_crewai_format()
        
        agent_kwargs = {
            "role": "Senior Code Quality Reviewer",
            "goal": "Ensure code quality, security, and maintainability through thorough reviews and constructive feedback",
            "backstory": """You are a meticulous code reviewer with a keen eye for detail, security 
            vulnerabilities, and best practices. You provide constructive feedback that helps improve 
            code quality while mentoring other developers to write better code.""",
            "llm": llm,
            "verbose": optimized_config.verbose,
            "allow_delegation": False,  # Reviewers should focus on their analysis
            "max_iter": 15,  # Focused iterations for detailed analysis
            "max_execution_time": None,
        }
        
        if tools:
            agent_kwargs["tools"] = tools
            
        return Agent(**agent_kwargs)

    @staticmethod  
    def create_project_manager(
        config: LLMConfig,
        tools: Optional[List[Any]] = None
    ) -> Agent:
        """
        Create a Project Manager agent optimized for planning and coordination.
        
        Args:
            config: LLM configuration
            tools: Optional list of tools for the agent
            
        Returns:
            Agent: Configured Project Manager agent
        """
        # Optimize configuration for management role
        optimized_config = AgentFactory._optimize_config_for_role(config, "manager")
        
        # Create CrewAI LLM instance
        llm = optimized_config.create_crewai_llm()
        
        # Fallback to string format if CrewAI LLM creation fails
        if llm is None:
            llm = optimized_config.to_crewai_format()
        
        agent_kwargs = {
            "role": "Project Manager and Coordinator",
            "goal": "Ensure project success through effective planning, resource allocation, and team coordination",
            "backstory": """You are an experienced project manager with a track record of delivering 
            complex projects on time and within budget. You excel at stakeholder communication, 
            risk management, and keeping teams focused on deliverables.""",
            "llm": llm,
            "verbose": optimized_config.verbose,
            "allow_delegation": True,  # Enable collaboration tools for coordination
            "max_iter": 20,
            "max_execution_time": None,
        }
        
        if tools:
            agent_kwargs["tools"] = tools
            
        return Agent(**agent_kwargs)

    @staticmethod
    def get_recommended_models_by_role() -> Dict[str, Dict[str, str]]:
        """
        Get recommended LLM models for different agent roles.
        
        Returns:
            Dict: Mapping of roles to recommended models by provider
        """
        return {
            "tech_lead": {
                "openai": "gpt-4o",           # Best reasoning for strategic decisions
                "anthropic": "claude-3-opus",  # Excellent for complex analysis
                "ollama": "llama3.1:70b"      # Good local alternative
            },
            "developer": {
                "openai": "gpt-4o-mini",      # Good balance of capability and cost
                "anthropic": "claude-3-sonnet", # Strong coding abilities
                "ollama": "llama3.1:8b"       # Efficient for coding tasks
            },
            "reviewer": {
                "openai": "gpt-4o",           # Precise analysis
                "anthropic": "claude-3-sonnet", # Good attention to detail
                "ollama": "llama3.1:8b"       # Reliable for code review
            },
            "manager": {
                "openai": "gpt-4o",           # Consistent strategic thinking
                "anthropic": "claude-3-opus",  # Excellent for planning
                "ollama": "llama3.1:70b"      # Good for coordination
            }
        }

# Export the main class
__all__ = ["AgentFactory"]
