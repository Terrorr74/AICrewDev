"""
Agent Service - Business logic for agent management and operations.

This service provides high-level operations for creating, configuring,
and managing AI agents within the AICrewDev system.
"""

from typing import List, Dict, Any, Optional
from crewai import Agent
from src.config.llm_config import LLMConfig
from src.models.agent_models import AgentSpecification, AgentRole, DeveloperSpecialization
from src.agents.agent_factory import AgentFactory

class AgentService:
    """
    Service class for managing AI agent lifecycle and operations.
    
    This service provides business logic for agent creation, configuration,
    and management, abstracting the complexity of the underlying agent factory.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Initialize the agent service.
        
        Args:
            llm_config: LLM configuration. If None, uses default configuration.
        """
        self.llm_config = llm_config or LLMConfig.get_default_config()
        self._created_agents: List[Agent] = []
        self._agent_specs: Dict[str, AgentSpecification] = {}
    
    def create_agent_from_spec(self, spec: AgentSpecification) -> Agent:
        """
        Create an agent from a specification.
        
        Args:
            spec: Agent specification defining the agent's configuration
            
        Returns:
            Agent: Created CrewAI agent
        """
        # Apply specification-specific LLM configuration if needed
        config = self.llm_config
        if spec.temperature is not None:
            # Create a modified config with custom temperature
            config_dict = config.model_dump()
            config_dict['temperature'] = spec.temperature
            config = LLMConfig(**config_dict)
        
        # Create agent based on role
        if spec.role == AgentRole.TECH_LEAD:
            agent = AgentFactory.create_tech_lead(config)
        elif spec.role == AgentRole.DEVELOPER:
            specialization = spec.specialization or DeveloperSpecialization.FULLSTACK
            agent = AgentFactory.create_developer(config, specialization=specialization.value)
        elif spec.role == AgentRole.CODE_REVIEWER:
            agent = AgentFactory.create_code_reviewer(config)
        elif spec.role == AgentRole.PROJECT_MANAGER:
            agent = AgentFactory.create_project_manager(config)
        else:
            # Create a generic agent for other roles
            agent = self._create_generic_agent(spec, config)
        
        # Store agent and specification
        role_str = spec.role if isinstance(spec.role, str) else spec.role.value
        agent_id = f"{role_str}_{len(self._created_agents)}"
        self._created_agents.append(agent)
        self._agent_specs[agent_id] = spec
        
        return agent
    
    def create_development_team(self, project_type: str = "web") -> List[Agent]:
        """
        Create a complete development team with role-optimized agents.
        
        Args:
            project_type: Type of project (web, mobile, api, etc.)
            
        Returns:
            List[Agent]: Complete development team
        """
        # Define team composition based on project type
        team_specs = self._get_team_specs_for_project(project_type)
        
        team = []
        for spec in team_specs:
            agent = self.create_agent_from_spec(spec)
            team.append(agent)
        
        return team
    
    def create_analysis_team(self) -> List[Agent]:
        """
        Create a team focused on code analysis and review.
        
        Returns:
            List[Agent]: Analysis-focused team
        """
        specs = [
            AgentSpecification.for_tech_lead(temperature=0.1),
            AgentSpecification.for_code_reviewer(temperature=0.2)
        ]
        
        team = []
        for spec in specs:
            agent = self.create_agent_from_spec(spec)
            team.append(agent)
        
        return team
    
    def get_agent_by_role(self, role: AgentRole) -> Optional[Agent]:
        """
        Get the first agent with the specified role.
        
        Args:
            role: Agent role to search for
            
        Returns:
            Optional[Agent]: Agent with the specified role, if found
        """
        for agent_id, spec in self._agent_specs.items():
            if spec.role == role:
                # Find corresponding agent
                index = list(self._agent_specs.keys()).index(agent_id)
                if index < len(self._created_agents):
                    return self._created_agents[index]
        return None
    
    def get_all_agents(self) -> List[Agent]:
        """
        Get all created agents.
        
        Returns:
            List[Agent]: List of all created agents
        """
        return self._created_agents.copy()
    
    def get_agent_specifications(self) -> Dict[str, AgentSpecification]:
        """
        Get all agent specifications.
        
        Returns:
            Dict[str, AgentSpecification]: Mapping of agent IDs to specifications
        """
        return self._agent_specs.copy()
    
    def get_team_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current team composition.
        
        Returns:
            Dict[str, Any]: Team summary with statistics
        """
        role_counts = {}
        specializations = {}
        
        for spec in self._agent_specs.values():
            # Count roles
            role = spec.role.value
            role_counts[role] = role_counts.get(role, 0) + 1
            
            # Count specializations for developers
            if spec.role == AgentRole.DEVELOPER and spec.specialization:
                spec_name = spec.specialization.value
                specializations[spec_name] = specializations.get(spec_name, 0) + 1
        
        return {
            "total_agents": len(self._created_agents),
            "role_distribution": role_counts,
            "developer_specializations": specializations,
            "llm_provider": self.llm_config.provider,
            "llm_model": self.llm_config.model_name
        }
    
    def _create_generic_agent(self, spec: AgentSpecification, config: LLMConfig) -> Agent:
        """
        Create a generic agent from specification.
        
        Args:
            spec: Agent specification
            config: LLM configuration
            
        Returns:
            Agent: Created generic agent
        """
        llm = config.create_crewai_llm()
        if llm is None:
            llm = config.to_crewai_format()
        
        agent_kwargs = spec.to_agent_kwargs()
        agent_kwargs["llm"] = llm
        
        return Agent(**agent_kwargs)
    
    def _get_team_specs_for_project(self, project_type: str) -> List[AgentSpecification]:
        """
        Get team specifications based on project type.
        
        Args:
            project_type: Type of project
            
        Returns:
            List[AgentSpecification]: Team specifications
        """
        # Base team for most projects
        specs = [
            AgentSpecification.for_tech_lead(),
            AgentSpecification.for_project_manager()
        ]
        
        # Add specialized developers based on project type
        if project_type == "web":
            specs.extend([
                AgentSpecification.for_developer(DeveloperSpecialization.FRONTEND),
                AgentSpecification.for_developer(DeveloperSpecialization.BACKEND)
            ])
        elif project_type == "mobile":
            specs.append(
                AgentSpecification.for_developer(DeveloperSpecialization.MOBILE)
            )
        elif project_type == "api":
            specs.append(
                AgentSpecification.for_developer(DeveloperSpecialization.BACKEND)
            )
        elif project_type == "data":
            specs.append(
                AgentSpecification.for_developer(DeveloperSpecialization.DATA)
            )
        else:
            # Default to fullstack developer
            specs.append(
                AgentSpecification.for_developer(DeveloperSpecialization.FULLSTACK)
            )
        
        # Always add a code reviewer
        specs.append(AgentSpecification.for_code_reviewer())
        
        return specs
    
    def reset(self):
        """Reset the service state."""
        self._created_agents.clear()
        self._agent_specs.clear()

__all__ = ["AgentService"]
