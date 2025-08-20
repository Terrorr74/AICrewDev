"""
Task Service - Business logic for task management and workflow operations.

This service provides high-level operations for creating, configuring,
and managing tasks within the AICrewDev system.
"""

from typing import List, Dict, Any, Optional
from crewai import Task, Agent
from src.models.task_models import TaskSpecification, TaskType, TaskPriority
from src.tasks.task_factory import TaskFactory

class TaskService:
    """
    Service class for managing task lifecycle and workflow operations.
    
    This service provides business logic for task creation, configuration,
    and workflow management, abstracting the complexity of task coordination.
    """
    
    def __init__(self):
        """Initialize the task service."""
        self._created_tasks: List[Task] = []
        self._task_specs: Dict[str, TaskSpecification] = {}
        self._workflow_templates: Dict[str, List[TaskSpecification]] = {}
        self._initialize_workflow_templates()
    
    def create_task_from_spec(self, spec: TaskSpecification, agent: Agent) -> Task:
        """
        Create a task from a specification and assign it to an agent.
        
        Args:
            spec: Task specification defining the task's configuration
            agent: Agent to assign the task to
            
        Returns:
            Task: Created CrewAI task
        """
        # Convert specification to task kwargs
        task_kwargs = spec.to_task_kwargs()
        task_kwargs["agent"] = agent
        
        # Create the task
        task = Task(**task_kwargs)
        
        # Store task and specification
        task_id = f"{spec.task_type.value}_{len(self._created_tasks)}"
        self._created_tasks.append(task)
        self._task_specs[task_id] = spec
        
        return task
    
    def create_development_workflow(self, agents: List[Agent], project_type: str = "web") -> List[Task]:
        """
        Create a complete development workflow with appropriate tasks.
        
        Args:
            agents: List of available agents
            project_type: Type of project being developed
            
        Returns:
            List[Task]: Development workflow tasks
        """
        if len(agents) < 3:
            raise ValueError("Development workflow requires at least 3 agents (tech lead, developer, reviewer)")
        
        tech_lead = agents[0]  # Assuming first agent is tech lead
        developer = agents[1]  # Assuming second agent is developer
        reviewer = agents[2]   # Assuming third agent is reviewer
        
        # Create workflow tasks
        tasks = []
        
        # 1. Planning and Design
        design_spec = TaskSpecification.for_design_task()
        design_task = self.create_task_from_spec(design_spec, tech_lead)
        tasks.append(design_task)
        
        # 2. Development
        dev_spec = TaskSpecification.for_development_task(f"{project_type} application")
        dev_task = self.create_task_from_spec(dev_spec, developer)
        tasks.append(dev_task)
        
        # 3. Code Review
        review_spec = TaskSpecification.for_review_task("implementation code")
        review_task = self.create_task_from_spec(review_spec, reviewer)
        tasks.append(review_task)
        
        # 4. Integration (if project manager available)
        if len(agents) > 3:
            manager = agents[3]
            integration_spec = TaskSpecification(
                task_type=TaskType.PLANNING,
                title="Project Integration and Delivery",
                description="Coordinate final integration and prepare for project delivery",
                expected_output="Integration report with delivery readiness assessment",
                priority=TaskPriority.HIGH
            )
            integration_task = self.create_task_from_spec(integration_spec, manager)
            tasks.append(integration_task)
        
        return tasks
    
    def create_analysis_workflow(self, agents: List[Agent], analysis_target: str) -> List[Task]:
        """
        Create an analysis workflow for code/system analysis.
        
        Args:
            agents: List of available agents
            analysis_target: What is being analyzed
            
        Returns:
            List[Task]: Analysis workflow tasks
        """
        if len(agents) < 2:
            raise ValueError("Analysis workflow requires at least 2 agents")
        
        tech_lead = agents[0]
        reviewer = agents[1]
        
        tasks = []
        
        # 1. System Analysis
        analysis_spec = TaskSpecification.for_analysis_task(analysis_target)
        analysis_task = self.create_task_from_spec(analysis_spec, tech_lead)
        tasks.append(analysis_task)
        
        # 2. Quality Review
        review_spec = TaskSpecification.for_review_task(analysis_target)
        review_task = self.create_task_from_spec(review_spec, reviewer)
        tasks.append(review_task)
        
        return tasks
    
    def create_testing_workflow(self, agents: List[Agent], test_scope: str) -> List[Task]:
        """
        Create a testing workflow for comprehensive testing.
        
        Args:
            agents: List of available agents
            test_scope: Scope of testing to be performed
            
        Returns:
            List[Task]: Testing workflow tasks
        """
        if not agents:
            raise ValueError("Testing workflow requires at least 1 agent")
        
        # Use developer for testing if available, otherwise use first agent
        tester = agents[1] if len(agents) > 1 else agents[0]
        
        tasks = []
        
        # 1. Test Planning
        test_plan_spec = TaskSpecification(
            task_type=TaskType.PLANNING,
            title="Test Planning and Strategy",
            description=f"Create comprehensive test plan for {test_scope}",
            expected_output="Detailed test plan with strategy, scope, and test cases",
            priority=TaskPriority.HIGH
        )
        test_plan_task = self.create_task_from_spec(test_plan_spec, tester)
        tasks.append(test_plan_task)
        
        # 2. Test Implementation
        test_impl_spec = TaskSpecification.for_testing_task(test_scope)
        test_impl_task = self.create_task_from_spec(test_impl_spec, tester)
        tasks.append(test_impl_task)
        
        # 3. Test Review (if reviewer available)
        if len(agents) > 2:
            reviewer = agents[2]
            test_review_spec = TaskSpecification.for_review_task("test implementation")
            test_review_task = self.create_task_from_spec(test_review_spec, reviewer)
            tasks.append(test_review_task)
        
        return tasks
    
    def get_workflow_template(self, workflow_name: str) -> Optional[List[TaskSpecification]]:
        """
        Get a predefined workflow template.
        
        Args:
            workflow_name: Name of the workflow template
            
        Returns:
            Optional[List[TaskSpecification]]: Workflow template specifications
        """
        return self._workflow_templates.get(workflow_name)
    
    def get_available_workflows(self) -> List[str]:
        """
        Get list of available workflow templates.
        
        Returns:
            List[str]: Names of available workflow templates
        """
        return list(self._workflow_templates.keys())
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all created tasks.
        
        Returns:
            List[Task]: List of all created tasks
        """
        return self._created_tasks.copy()
    
    def get_task_specifications(self) -> Dict[str, TaskSpecification]:
        """
        Get all task specifications.
        
        Returns:
            Dict[str, TaskSpecification]: Mapping of task IDs to specifications
        """
        return self._task_specs.copy()
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current workflow.
        
        Returns:
            Dict[str, Any]: Workflow summary with statistics
        """
        task_type_counts = {}
        priority_counts = {}
        
        for spec in self._task_specs.values():
            # Count task types
            task_type = spec.task_type.value
            task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
            
            # Count priorities
            priority = spec.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "total_tasks": len(self._created_tasks),
            "task_type_distribution": task_type_counts,
            "priority_distribution": priority_counts,
            "available_templates": len(self._workflow_templates)
        }
    
    def _initialize_workflow_templates(self):
        """Initialize predefined workflow templates."""
        
        # Agile Development Workflow
        self._workflow_templates["agile_development"] = [
            TaskSpecification.for_design_task(),
            TaskSpecification.for_development_task("user story features"),
            TaskSpecification.for_testing_task("implemented features"),
            TaskSpecification.for_review_task("completed implementation")
        ]
        
        # Code Review Workflow
        self._workflow_templates["code_review"] = [
            TaskSpecification.for_analysis_task("codebase structure"),
            TaskSpecification.for_review_task("code quality and security"),
            TaskSpecification(
                task_type=TaskType.DOCUMENTATION,
                title="Document Review Findings",
                description="Create comprehensive documentation of review findings and recommendations",
                expected_output="Review report with actionable recommendations"
            )
        ]
        
        # Research and Development Workflow
        self._workflow_templates["research_development"] = [
            TaskSpecification(
                task_type=TaskType.RESEARCH,
                title="Technology Research",
                description="Research and evaluate technology options and approaches",
                expected_output="Technology evaluation report with recommendations"
            ),
            TaskSpecification.for_design_task(),
            TaskSpecification(
                task_type=TaskType.DEVELOPMENT,
                title="Prototype Development",
                description="Develop proof-of-concept prototype",
                expected_output="Working prototype with documentation"
            ),
            TaskSpecification.for_analysis_task("prototype performance")
        ]
        
        # Performance Optimization Workflow
        self._workflow_templates["performance_optimization"] = [
            TaskSpecification.for_analysis_task("system performance"),
            TaskSpecification(
                task_type=TaskType.OPTIMIZATION,
                title="Performance Optimization",
                description="Implement performance improvements based on analysis",
                expected_output="Optimized system with performance metrics"
            ),
            TaskSpecification.for_testing_task("performance improvements"),
            TaskSpecification.for_review_task("optimization implementation")
        ]
    
    def reset(self):
        """Reset the service state."""
        self._created_tasks.clear()
        self._task_specs.clear()

__all__ = ["TaskService"]
