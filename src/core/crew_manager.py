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
    
    def create_development_crew(self, project_type: str = "web", enable_delegation: bool = True) -> Crew:
        """
        Create a development-focused crew with specialized agents.
        
        Args:
            project_type: Type of project (web, mobile, api, etc.)
            enable_delegation: Whether to enable delegation features (default: True)
            
        Returns:
            Crew: Configured development crew
        """
        # Create role-specific agents
        if enable_delegation:
            tech_lead = AgentFactory.create_tech_lead(self.config)
            project_manager = AgentFactory.create_project_manager(self.config)
        else:
            # Create agents without delegation for testing
            tech_lead = self._create_simple_tech_lead()
            project_manager = self._create_simple_project_manager()
        
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
        
        agents = [tech_lead, developer, code_reviewer, project_manager]
        
        # Create development tasks
        if enable_delegation:
            tasks = self._create_development_tasks(agents, project_type)
        else:
            tasks = self._create_simple_development_tasks(agents, project_type)
        
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
        
        # Display agent collaboration settings
        for i, agent in enumerate(target_crew.agents):
            delegation_status = "✅ Can delegate" if getattr(agent, 'allow_delegation', False) else "❌ No delegation"
            print(f"   Agent {i+1}: {agent.role} ({delegation_status})")
        
        try:
            # Execute the crew with proper error handling
            if input_data:
                print(f"📊 Input data provided: {list(input_data.keys())}")
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
            
            # Provide specific guidance for common errors
            if "unhashable type" in str(e):
                print("💡 This error is often related to tool parameter formatting.")
                print("🔧 The crew will continue with available functionality.")
            elif "delegation" in str(e).lower():
                print("💡 This may be a delegation tool issue.")
                print("🔧 Try running without delegation features.")
            
            raise
    
    def _create_development_tasks(self, agents: List[Agent], project_type: str) -> List[Task]:
        """
        Create development-specific tasks for the crew that encourage collaboration.
        
        Args:
            agents: List of available agents
            project_type: Type of project being developed
            
        Returns:
            List[Task]: Development tasks designed for collaboration
        """
        tech_lead, developer, reviewer, manager = agents
        
        # Task 1: Strategic Planning - Led by Tech Lead with delegation capability
        planning_task = Task(
            description=f"""Create a comprehensive technical plan for building a {project_type} application.
            
            As the technical lead, you should:
            1. Define the system architecture and technology stack
            2. Break down the project into manageable components
            3. Identify potential risks and mitigation strategies
            4. Collaborate with the project manager on timeline and resource planning
            
            Feel free to ask questions to your teammates or delegate specific research tasks.""",
            agent=tech_lead,
            expected_output="A detailed technical architecture document with implementation roadmap",
        )
        
        # Task 2: Implementation - Developer with context from planning
        development_task = Task(
            description=f"""Implement the {project_type} application based on the technical specifications.
            
            Focus on:
            1. Writing clean, maintainable code following best practices
            2. Implementing core features and functionality
            3. Adding proper error handling and logging
            4. Creating basic tests for key functionality
            
            If you need clarification on any requirements, ask the tech lead or project manager.""",
            agent=developer,
            expected_output="Complete application code with core features implemented",
            context=[planning_task],  # Gets context from planning task
        )
        
        # Task 3: Quality Review - Reviewer with context from development
        review_task = Task(
            description="""Review the implemented code for quality, security, and best practices.
            
            Provide feedback on:
            1. Code quality and maintainability
            2. Security vulnerabilities and fixes
            3. Performance optimization opportunities
            4. Testing coverage and suggestions
            
            If you find issues that need developer input, ask specific questions.""",
            agent=reviewer,
            expected_output="Code review report with specific feedback and improvement recommendations",
            context=[development_task],  # Gets context from development task
        )
        
        # Task 4: Project Coordination - Manager with full context
        coordination_task = Task(
            description="""Coordinate the final project delivery and ensure all requirements are met.
            
            Your responsibilities:
            1. Review all deliverables for completeness
            2. Ensure the project meets the original requirements
            3. Coordinate any remaining work between team members
            4. Prepare the final project summary and next steps
            
            Delegate any final tasks that need to be completed and ask questions to clarify any gaps.""",
            agent=manager,
            expected_output="Project delivery summary with quality assessment and completion status",
            context=[planning_task, development_task, review_task],  # Gets context from all previous tasks
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
    
    def _create_simple_tech_lead(self) -> Agent:
        """Create a tech lead without delegation for testing."""
        llm = self.config.create_crewai_llm()
        if llm is None:
            llm = self.config.to_crewai_format()
            
        return Agent(
            role="Technical Lead",
            goal="Provide technical leadership and create system architecture",
            backstory="You are an experienced technical leader with expertise in software architecture.",
            llm=llm,
            verbose=self.config.verbose,
            allow_delegation=False,  # Disable delegation for testing
            max_iter=15,
        )
    
    def _create_simple_project_manager(self) -> Agent:
        """Create a project manager without delegation for testing."""
        llm = self.config.create_crewai_llm()
        if llm is None:
            llm = self.config.to_crewai_format()
            
        return Agent(
            role="Project Manager",
            goal="Coordinate project delivery and ensure quality",
            backstory="You are an experienced project manager focused on successful delivery.",
            llm=llm,
            verbose=self.config.verbose,
            allow_delegation=False,  # Disable delegation for testing
            max_iter=15,
        )
    
    def _create_simple_development_tasks(self, agents: List[Agent], project_type: str) -> List[Task]:
        """
        Create simple development tasks without complex collaboration.
        
        Args:
            agents: List of available agents
            project_type: Type of project being developed
            
        Returns:
            List[Task]: Simple development tasks
        """
        tech_lead, developer, reviewer, manager = agents
        
        # Simple tasks without delegation requirements
        planning_task = Task(
            description=f"Create a technical plan for a {project_type} application including architecture and technology choices.",
            agent=tech_lead,
            expected_output="Technical architecture document with implementation plan",
        )
        
        development_task = Task(
            description=f"Implement a {project_type} application with core functionality, following best practices.",
            agent=developer,
            expected_output="Complete application code with main features implemented",
            context=[planning_task],
        )
        
        review_task = Task(
            description="Review the implemented code for quality, security, and best practices.",
            agent=reviewer,
            expected_output="Code review report with feedback and recommendations",
            context=[development_task],
        )
        
        coordination_task = Task(
            description="Review all deliverables and prepare project summary.",
            agent=manager,
            expected_output="Project completion summary with quality assessment",
            context=[planning_task, development_task, review_task],
        )
        
        return [planning_task, development_task, review_task, coordination_task]
    
    def reset(self):
        """Reset the crew manager state."""
        self._current_crew = None
        self._execution_history.clear()

__all__ = ["CrewManager"]
