"""
AICrewDev Main Module

This module serves as the entry point for the AI development crew system.
It orchestrates the creation and execution of AI agents and their tasks using
the enhanced configuration system.

Classes:
    AICrewDev: Main class that coordinates AI agents and tasks

Example:
    >>> ai_crew = AICrewDev()
    >>> result = ai_crew.run()
    >>> print(result)
"""

from crewai import Crew
from typing import List, cast, Any, Optional
from crewai.agent import BaseAgent
from src.utils.environment import validate_environment
from src.core.settings import Settings
from src.core.crew_manager import CrewManager
from src.services.agent_service import AgentService
from src.services.task_service import TaskService
from src.monitoring.logger import AICrewLogger
from src.monitoring.metrics_collector import MetricsCollector, PerformanceTracker
from src.monitoring.health_checker import HealthChecker

class AICrewDev:
    """
    Main class for managing AI development crew operations using enhanced architecture.
    
    This class now leverages the enhanced service layer, centralized settings,
    and improved crew management for better scalability and maintainability.
    
    Attributes:
        settings (Settings): Application settings and configuration
        crew_manager (CrewManager): Core crew orchestration manager
        agent_service (AgentService): Service for agent lifecycle management
        task_service (TaskService): Service for task and workflow management
        logger (AICrewLogger): Structured logger for monitoring
        metrics (MetricsCollector): Performance metrics collector
        health_checker (HealthChecker): System health monitoring
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the AICrewDev instance with enhanced architecture.
        
        Args:
            settings: Application settings. If None, uses default settings.
            
        Raises:
            EnvironmentError: If required environment variables are missing
        """
        validate_environment()
        
        # Initialize enhanced architecture components
        self.settings = settings or Settings()
        
        # Initialize monitoring components
        self.logger = AICrewLogger(
            service_name="aicrewdev",
            environment=self.settings.environment,
            log_level=self.settings.log_level,
            enable_console=True,
            enable_file=True
        )
        
        self.metrics = MetricsCollector(
            retention_hours=24,
            max_datapoints=10000
        )
        
        self.health_checker = HealthChecker(
            check_interval_seconds=60,
            timeout_seconds=10
        )
        
        # Add context to logger
        provider_str = self.settings.llm_config.provider
        if hasattr(provider_str, 'value'):
            provider_str = provider_str.value
        
        self.logger.add_context(
            version=self.settings.version,
            llm_provider=provider_str,
            llm_model=self.settings.llm_config.model_name
        )
        
        # Initialize core components
        self.crew_manager = CrewManager(self.settings)
        self.agent_service = AgentService(self.settings.llm_config)
        self.task_service = TaskService()
        
        # Validate configuration
        self.settings.validate_environment()
        
        # Log initialization
        self.logger.info("AICrewDev initialized with enhanced architecture", 
                        component="initialization",
                        provider=provider_str,
                        model=self.settings.llm_config.model_name)
        
    def create_agents(self, project_type: str = "web"):
        """
        Create specialized AI agents using the enhanced service layer.
        
        Args:
            project_type: Type of project (web, mobile, api, etc.)
            
        Returns:
            list[Agent]: List of specialized AI agents
        """
        return self.agent_service.create_development_team(project_type)
    
    def create_tasks(self, agents, project_type: str = "web"):
        """
        Define development tasks using the enhanced task service.
        
        Args:
            agents: List of available agents
            project_type: Type of project being developed
            
        Returns:
            list[Task]: List of tasks to be executed by the AI agents
        """
        return self.task_service.create_development_workflow(agents, project_type)
    
    def run(self, project_type: str = "web", use_crew_manager: bool = True) -> Any:
        """
        Execute the AI development workflow using enhanced architecture.
        
        Args:
            project_type: Type of project to develop
            use_crew_manager: Whether to use the crew manager for orchestration
            
        Returns:
            Any: Result of the crew execution
        """
        # Track operation performance
        with PerformanceTracker(self.metrics, f"crew_execution_{project_type}"):
            # Get provider string for logging
            provider_str = self.settings.llm_config.provider
            if hasattr(provider_str, 'value'):
                provider_str = provider_str.value
                
            self.logger.info(
                f"Starting crew execution",
                operation="crew_execution",
                project_type=project_type,
                use_crew_manager=use_crew_manager
            )
            
            try:
                if use_crew_manager:
                    # Use the enhanced crew manager for better orchestration
                    crew = self.crew_manager.create_development_crew(project_type)
                    result = self.crew_manager.execute_crew(crew)
                else:
                    # Use the traditional approach with enhanced services
                    agents = self.create_agents(project_type)
                    tasks = self.create_tasks(agents, project_type)
                    
                    # Track agent and task creation
                    self.metrics.track_crew_execution(
                        crew_id=f"traditional_{project_type}",
                        agents_count=len(agents),
                        tasks_count=len(tasks),
                        duration_ms=0,  # Will be updated after execution
                        success=True
                    )
                    
                    # Create crew with enhanced configuration
                    crew_config = self.settings.get_crew_config()
                    crew = Crew(
                        agents=cast(List[BaseAgent], agents),
                        tasks=tasks,
                        **crew_config
                    )
                    
                    self.logger.info(
                        "Starting crew execution",
                        agents_count=len(agents),
                        tasks_count=len(tasks),
                        provider=provider_str,
                        model=self.settings.llm_config.model_name,
                        temperature=self.settings.llm_config.temperature
                    )
                    
                    result = crew.kickoff()
                
                self.logger.info(
                    "Crew execution completed successfully",
                    operation="crew_execution",
                    project_type=project_type,
                    result_length=len(str(result)) if result else 0
                )
                
                return result
                
            except Exception as e:
                self.logger.error(
                    "Crew execution failed",
                    operation="crew_execution",
                    project_type=project_type,
                    error=e
                )
                raise
    
    def run_analysis(self, analysis_target: str = "codebase") -> Any:
        """
        Run analysis workflow using the enhanced architecture.
        
        Args:
            analysis_target: What to analyze
            
        Returns:
            Any: Analysis results
        """
        with PerformanceTracker(self.metrics, "analysis_execution"):
            self.logger.info(
                "Starting analysis workflow",
                operation="analysis_execution",
                target=analysis_target
            )
            
            try:
                crew = self.crew_manager.create_analysis_crew()
                result = self.crew_manager.execute_crew(crew, {"analysis_target": analysis_target})
                
                self.logger.info(
                    "Analysis workflow completed",
                    operation="analysis_execution",
                    target=analysis_target,
                    result_length=len(str(result)) if result else 0
                )
                
                return result
                
            except Exception as e:
                self.logger.error(
                    "Analysis workflow failed",
                    operation="analysis_execution",
                    target=analysis_target,
                    error=e
                )
                raise
    
    def get_status(self) -> dict:
        """
        Get comprehensive status of the AICrewDev system including monitoring data.
        
        Returns:
            dict: System status information with performance metrics
        """
        # Get provider string for health checks
        provider_str = self.settings.llm_config.provider
        if hasattr(provider_str, 'value'):
            provider_str = provider_str.value
            
        # Run health checks
        health_results = self.health_checker.run_all_health_checks(
            config=self.settings.model_dump(),
            check_llm_providers=[provider_str],
        )
        
        return {
            "application": self.settings.get_info(),
            "crew_manager": self.crew_manager.get_current_crew_info(),
            "agent_service": self.agent_service.get_team_summary(),
            "task_service": self.task_service.get_workflow_summary(),
            "execution_history": len(self.crew_manager.get_execution_history()),
            "monitoring": {
                "performance_dashboard": self.metrics.get_performance_dashboard(),
                "health_status": self.health_checker.get_system_status(),
                "health_checks": {
                    name: {
                        "status": check.status.value,
                        "message": check.message,
                        "duration_ms": check.duration_ms
                    }
                    for name, check in health_results.items()
                }
            }
        }
    
    def reset(self):
        """Reset all services and managers to initial state."""
        self.crew_manager.reset()
        self.agent_service.reset()
        self.task_service.reset()
        print("🔄 AICrewDev system reset completed")
if __name__ == "__main__":
    # Example usage with enhanced architecture
    print("🚀 AICrewDev - Enhanced Architecture Demo")
    
    # Create AICrewDev instance with default settings
    ai_crew = AICrewDev()
    
    # Display system status
    status = ai_crew.get_status()
    print(f"\n📊 System Status:")
    print(f"   App: {status['application']['app_name']} v{status['application']['version']}")
    print(f"   Environment: {status['application']['environment']}")
    print(f"   LLM: {status['application']['llm_provider']}/{status['application']['llm_model']}")
    
    # Run development workflow
    print(f"\n🔨 Running development workflow...")
    try:
        result = ai_crew.run(project_type="web", use_crew_manager=True)
        print(f"✅ Development workflow completed successfully!")
        print(f"📄 Result: {str(result)[:200]}..." if len(str(result)) > 200 else f"📄 Result: {result}")
        
        # Show execution history
        history = ai_crew.crew_manager.get_execution_history()
        print(f"\n📈 Execution History: {len(history)} executions")
        
    except Exception as e:
        print(f"❌ Development workflow failed: {e}")
    
    # Run analysis workflow
    print(f"\n🔍 Running analysis workflow...")
    try:
        analysis_result = ai_crew.run_analysis("project codebase")
        print(f"✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Analysis workflow failed: {e}")
    
    # Final status
    final_status = ai_crew.get_status()
    print(f"\n📊 Final Status:")
    print(f"   Total Executions: {final_status['execution_history']}")
    print(f"   Agents Created: {final_status['agent_service']['total_agents']}")
    print(f"   Tasks Created: {final_status['task_service']['total_tasks']}")
    
    print(f"\n🎉 AICrewDev Enhanced Architecture Demo Complete!")
