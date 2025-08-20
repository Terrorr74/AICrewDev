"""
Agent data models and specifications for AICrewDev.

This module defines the data structures and specifications used for
agent configuration, role definitions, and agent management.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class AgentRole(str, Enum):
    """Enumeration of available agent roles in the development crew."""
    TECH_LEAD = "tech_lead"
    DEVELOPER = "developer"
    CODE_REVIEWER = "code_reviewer"
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    TESTER = "tester"
    DEVOPS = "devops"
    PRODUCT_OWNER = "product_owner"

class DeveloperSpecialization(str, Enum):
    """Enumeration of developer specializations."""
    FULLSTACK = "fullstack"
    FRONTEND = "frontend"
    BACKEND = "backend"
    MOBILE = "mobile"
    DEVOPS = "devops"
    DATA = "data"
    ML = "machine_learning"

class AgentSpecification(BaseModel):
    """
    Specification for creating an AI agent with specific capabilities and configuration.
    
    This model defines all the parameters needed to create and configure
    an AI agent within the CrewAI framework.
    """
    
    # Basic Agent Information
    role: AgentRole = Field(description="Primary role of the agent")
    name: Optional[str] = Field(default=None, description="Custom name for the agent")
    
    # Agent Behavior Configuration
    goal: str = Field(description="Primary goal or objective of the agent")
    backstory: str = Field(description="Background story and context for the agent")
    
    # Technical Configuration
    specialization: Optional[DeveloperSpecialization] = Field(
        default=None, 
        description="Specialization for developer agents"
    )
    temperature: Optional[float] = Field(
        default=None, 
        ge=0.0, 
        le=2.0, 
        description="Temperature override for this agent"
    )
    
    # Agent Capabilities
    allow_delegation: bool = Field(default=True, description="Whether agent can delegate tasks")
    allow_code_execution: bool = Field(default=False, description="Whether agent can execute code")
    verbose: bool = Field(default=True, description="Enable verbose output")
    
    # Performance Configuration
    max_iterations: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=100, 
        description="Maximum iterations for agent tasks"
    )
    max_execution_time: Optional[int] = Field(
        default=None, 
        ge=30, 
        le=3600, 
        description="Maximum execution time in seconds"
    )
    
    # Tools and Resources
    tools: List[str] = Field(default_factory=list, description="List of tools available to the agent")
    memory_enabled: bool = Field(default=True, description="Enable agent memory")
    
    # Custom Properties
    custom_properties: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Custom properties for specialized configurations"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
    
    @classmethod
    def for_tech_lead(cls, **kwargs) -> "AgentSpecification":
        """
        Create a specification for a Technical Lead agent.
        
        Returns:
            AgentSpecification: Configured tech lead specification
        """
        defaults = {
            "role": AgentRole.TECH_LEAD,
            "goal": "Ensure technical excellence and project success through strategic leadership",
            "backstory": """You are an experienced technical leader with deep expertise in software 
            architecture, team management, and strategic planning. You excel at breaking down complex 
            projects, identifying risks, and coordinating cross-functional teams.""",
            "temperature": 0.1,  # Low temperature for consistent strategic thinking
            "allow_delegation": True,
            "max_iterations": 25,
            "tools": ["code_analysis", "architecture_review", "project_planning"]
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_developer(cls, specialization: DeveloperSpecialization = DeveloperSpecialization.FULLSTACK, **kwargs) -> "AgentSpecification":
        """
        Create a specification for a Developer agent.
        
        Args:
            specialization: Developer specialization
            
        Returns:
            AgentSpecification: Configured developer specification
        """
        defaults = {
            "role": AgentRole.DEVELOPER,
            "specialization": specialization,
            "goal": f"Write high-quality, maintainable code for {specialization.value} development",
            "backstory": f"""You are a skilled {specialization.value} developer with extensive experience in 
            modern development practices, testing, and code quality. You write clean, efficient code and 
            stay up-to-date with the latest technologies.""",
            "temperature": 0.3,  # Balanced temperature for creativity
            "allow_code_execution": True,
            "max_iterations": 20,
            "tools": ["code_editor", "debugger", "testing_framework", "documentation"]
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_code_reviewer(cls, **kwargs) -> "AgentSpecification":
        """
        Create a specification for a Code Reviewer agent.
        
        Returns:
            AgentSpecification: Configured code reviewer specification
        """
        defaults = {
            "role": AgentRole.CODE_REVIEWER,
            "goal": "Ensure code quality, security, and maintainability through thorough reviews",
            "backstory": """You are a meticulous code reviewer with a keen eye for detail, security 
            vulnerabilities, and best practices. You provide constructive feedback that helps improve 
            code quality while mentoring other developers.""",
            "temperature": 0.2,  # Low temperature for accuracy
            "allow_delegation": False,
            "max_iterations": 15,
            "tools": ["static_analysis", "security_scanner", "code_metrics", "documentation_checker"]
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def for_project_manager(cls, **kwargs) -> "AgentSpecification":
        """
        Create a specification for a Project Manager agent.
        
        Returns:
            AgentSpecification: Configured project manager specification
        """
        defaults = {
            "role": AgentRole.PROJECT_MANAGER,
            "goal": "Ensure project success through effective planning, resource allocation, and coordination",
            "backstory": """You are an experienced project manager with a track record of delivering 
            complex projects on time and within budget. You excel at stakeholder communication, 
            risk management, and keeping teams focused on deliverables.""",
            "temperature": 0.1,  # Consistent strategic thinking
            "allow_delegation": True,
            "max_iterations": 20,
            "tools": ["project_tracking", "resource_planning", "communication", "reporting"]
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    def get_display_name(self) -> str:
        """
        Get a human-readable display name for the agent.
        
        Returns:
            str: Display name
        """
        if self.name:
            return self.name
        
        role_names = {
            AgentRole.TECH_LEAD: "Technical Lead",
            AgentRole.DEVELOPER: f"{self.specialization.value.title()} Developer" if self.specialization else "Developer",
            AgentRole.CODE_REVIEWER: "Code Reviewer",
            AgentRole.PROJECT_MANAGER: "Project Manager",
            AgentRole.ARCHITECT: "Software Architect",
            AgentRole.TESTER: "Quality Assurance Tester",
            AgentRole.DEVOPS: "DevOps Engineer",
            AgentRole.PRODUCT_OWNER: "Product Owner"
        }
        
        return role_names.get(self.role, self.role.value.replace("_", " ").title())
    
    def to_agent_kwargs(self) -> Dict[str, Any]:
        """
        Convert specification to kwargs suitable for CrewAI Agent creation.
        
        Returns:
            Dict[str, Any]: Agent creation parameters
        """
        kwargs = {
            "role": self.get_display_name(),
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": self.verbose,
            "allow_delegation": self.allow_delegation,
        }
        
        if self.max_iterations:
            kwargs["max_iter"] = self.max_iterations
        
        if self.allow_code_execution:
            kwargs["allow_code_execution"] = True
        
        if self.memory_enabled:
            kwargs["memory"] = True
        
        return kwargs

__all__ = ["AgentRole", "DeveloperSpecialization", "AgentSpecification"]
