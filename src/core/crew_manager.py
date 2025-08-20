"""
Crew Manager - Core orchestration logic for AICrewDev.

This module provides the main business logic for managing AI crews,
including crew creation, task coordination, and execution management.
"""

from typing import List, Dict, Any, Optional, cast
from crewai import Crew, Agent, Task
from crewai.agent import BaseAgent
from src.core.settings import Settings
from src.config.llm_config import LLMConfig
from src.agents.agent_factory import AgentFactory
from src.tasks.task_factory import TaskFactory

class CrewManager:
    """
    Central manager for AI crew operations and orchestration.
    
    This class handles the high-level coordination of AI crews, including
    agent creation, task management, and execution flow control.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the CrewManager with configuration settings.
        
        Args:
            settings: Application settings instance. If None, uses default settings.
        """
        self.settings = settings or Settings()
        self.config = self.settings.llm_config
        self._current_crew: Optional[Crew] = None
        self._execution_history: List[Dict[str, Any]] = []
    
    def create_development_crew(self, project_type: str = "web") -> Crew:
        """
        Create a development-focused crew with specialized agents.
        
        Args:
            project_type: Type of project (web, mobile, api, etc.)
            
        Returns:
            Crew: Configured development crew
        """
        # Create role-specific agents
        tech_lead = AgentFactory.create_tech_lead(self.config)
        
        # Customize developer based on project type
        specialization_map = {
            "web": "fullstack",
            "mobile": "mobile", 
            "api": "backend",
            "frontend": "frontend",
            "data": "data"
        }
        specialization = specialization_map.get(project_type, "fullstack")
        developer = AgentFactory.create_developer(self.config, specialization=specialization)
        
        code_reviewer = AgentFactory.create_code_reviewer(self.config)
        project_manager = AgentFactory.create_project_manager(self.config)
        
        agents = [tech_lead, developer, code_reviewer, project_manager]
        
        # Create development tasks
        tasks = self._create_development_tasks(agents, project_type)
        
        # Apply settings to crew configuration
        crew_config = self.settings.get_crew_config()
        
        crew = Crew(
            agents=cast(List[BaseAgent], agents),
            tasks=tasks,
            **crew_config
        )
        
        self._current_crew = crew
        return crew
    
    def create_analysis_crew(self) -> Crew:
        """
        Create an analysis-focused crew for code review and assessment.
        
        Returns:
            Crew: Configured analysis crew
        """
        # Create analysis-focused agents
        tech_lead = AgentFactory.create_tech_lead(self.config)
        reviewer = AgentFactory.create_code_reviewer(self.config)
        
        agents = [tech_lead, reviewer]
        
        # Create analysis tasks
        tasks = self._create_analysis_tasks(agents)
        
        crew_config = self.settings.get_crew_config()
        
        crew = Crew(
            agents=cast(List[BaseAgent], agents),
            tasks=tasks,
            **crew_config
        )
        
        self._current_crew = crew
        return crew
    
    def execute_crew(self, crew: Optional[Crew] = None, input_data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a crew with optional input data and track execution.
        
        Args:
            crew: Crew to execute. If None, uses current crew.
            input_data: Optional input data for the crew execution.
            
        Returns:
            str: Execution result
            
        Raises:
            ValueError: If no crew is available for execution
        """
        target_crew = crew or self._current_crew
        if not target_crew:
            raise ValueError("No crew available for execution. Create a crew first.")
        
        print(f"🚀 Starting crew execution with {self.config.provider} provider")
        print(f"📋 Model: {self.config.model_name}")
        print(f"🌡️  Temperature: {self.config.temperature}")
        print(f"👥 Agents: {len(target_crew.agents)}")
        print(f"📝 Tasks: {len(target_crew.tasks)}")
        
        try:
            # Execute the crew
            if input_data:
                result = target_crew.kickoff(inputs=input_data)
            else:
                result = target_crew.kickoff()
            
            # Track execution
            execution_record = {
                "timestamp": self._get_timestamp(),
                "provider": self.config.provider,
                "model": self.config.model_name,
                "agents_count": len(target_crew.agents),
                "tasks_count": len(target_crew.tasks),
                "success": True,
                "result_length": len(str(result)) if result else 0
            }
            self._execution_history.append(execution_record)
            
            print("✅ Crew execution completed successfully")
            return result
            
        except Exception as e:
            # Track failed execution
            execution_record = {
                "timestamp": self._get_timestamp(),
                "provider": self.config.provider,
                "model": self.config.model_name,
                "agents_count": len(target_crew.agents),
                "tasks_count": len(target_crew.tasks),
                "success": False,
                "error": str(e)
            }
            self._execution_history.append(execution_record)
            
            print(f"❌ Crew execution failed: {e}")
            raise
    
    def _create_development_tasks(self, agents: List[Agent], project_type: str) -> List[Task]:
        """
        Create development-specific tasks for the crew.
        
        Args:
            agents: List of available agents
            project_type: Type of project being developed
            
        Returns:
            List[Task]: Development tasks
        """
        tech_lead, developer, reviewer, manager = agents
        
        # Create project-specific tasks
        planning_task = TaskFactory.create_design_task(tech_lead)
        
        development_task = TaskFactory.create_development_task(
            developer,
            f"Implement {project_type} application following the design specifications"
        )
        
        review_task = TaskFactory.create_review_task(
            reviewer,
            "Review implementation for code quality, security, and best practices"
        )
        
        coordination_task = Task(
            description="Coordinate project delivery and ensure all requirements are met",
            agent=manager,
            expected_output="Project delivery summary with quality assessment"
        )
        
        return [planning_task, development_task, review_task, coordination_task]
    
    def _create_analysis_tasks(self, agents: List[Agent]) -> List[Task]:
        """
        Create analysis-specific tasks for the crew.
        
        Args:
            agents: List of available agents
            
        Returns:
            List[Task]: Analysis tasks
        """
        tech_lead, reviewer = agents
        
        analysis_task = Task(
            description="Analyze codebase architecture and identify improvement opportunities",
            agent=tech_lead,
            expected_output="Architecture analysis report with recommendations"
        )
        
        quality_task = TaskFactory.create_review_task(
            reviewer,
            "Perform comprehensive code quality assessment"
        )
        
        return [analysis_task, quality_task]
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get the execution history for analysis and debugging.
        
        Returns:
            List[Dict[str, Any]]: Execution history records
        """
        return self._execution_history.copy()
    
    def get_current_crew_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current crew.
        
        Returns:
            Optional[Dict[str, Any]]: Current crew information
        """
        if not self._current_crew:
            return None
        
        return {
            "agents_count": len(self._current_crew.agents),
            "tasks_count": len(self._current_crew.tasks),
            "agents": [agent.role for agent in self._current_crew.agents],
            "provider": self.config.provider,
            "model": self.config.model_name
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for execution tracking."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def reset(self):
        """Reset the crew manager state."""
        self._current_crew = None
        self._execution_history.clear()

__all__ = ["CrewManager"]
