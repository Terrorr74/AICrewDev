#!/usr/bin/env python3
"""
Async Agent Factory Module

This module provides asynchronous capabilities for creating and managing
AI agents with concurrent operations and improved performance.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dataclasses import dataclass
from enum import Enum

from crewai import Agent, Task, Crew
from crewai.agent import BaseAgent
from src.config.llm_config import LLMConfig, LLMProvider
from src.agents.agent_factory import AgentFactory
from src.config.validators import AgentConfigValidator, ValidationError


class AsyncOperationStatus(Enum):
    """Status of async operations"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AsyncOperationResult:
    """Result of an async operation"""
    operation_id: str
    status: AsyncOperationStatus
    result: Any = None
    error: Optional[Exception] = None
    start_time: float = 0.0
    end_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.start_time == 0.0:
            self.start_time = time.time()

    @property
    def duration(self) -> Optional[float]:
        """Get operation duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def is_complete(self) -> bool:
        """Check if operation is complete"""
        return self.status in [AsyncOperationStatus.COMPLETED, AsyncOperationStatus.FAILED]


class AsyncAgentFactory:
    """
    Asynchronous agent factory for concurrent agent creation and management
    """

    def __init__(self, max_workers: int = 4):
        """
        Initialize async agent factory
        
        Args:
            max_workers: Maximum number of concurrent operations
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_operations: Dict[str, AsyncOperationResult] = {}
        self.operation_counter = 0

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        self.operation_counter += 1
        return f"async_op_{self.operation_counter}_{int(time.time())}"

    async def create_agent_async(
        self,
        config: LLMConfig,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        **kwargs
    ) -> AsyncOperationResult:
        """
        Create an agent asynchronously
        
        Args:
            config: LLM configuration
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            tools: Optional tools list
            **kwargs: Additional agent parameters
            
        Returns:
            AsyncOperationResult with the created agent
        """
        operation_id = self._generate_operation_id()
        operation = AsyncOperationResult(
            operation_id=operation_id,
            status=AsyncOperationStatus.PENDING,
            metadata={
                "operation_type": "agent_creation",
                "role": role,
                "provider": config.provider
            }
        )
        
        self.active_operations[operation_id] = operation

        try:
            operation.status = AsyncOperationStatus.RUNNING
            
            # Run agent creation in thread pool
            loop = asyncio.get_event_loop()
            agent = await loop.run_in_executor(
                self.executor,
                self._create_agent_sync,
                config, role, goal, backstory, tools, kwargs
            )
            
            operation.result = agent
            operation.status = AsyncOperationStatus.COMPLETED
            operation.end_time = time.time()
            
        except Exception as e:
            operation.error = e
            operation.status = AsyncOperationStatus.FAILED
            operation.end_time = time.time()

        return operation

    def _create_agent_sync(
        self,
        config: LLMConfig,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]],
        kwargs: Dict[str, Any]
    ) -> Agent:
        """Synchronous agent creation for thread pool execution"""
        # Map roles to factory methods
        role_methods = {
            "tech_lead": AgentFactory.create_tech_lead,
            "developer": AgentFactory.create_developer,
            "reviewer": AgentFactory.create_code_reviewer,
            "manager": AgentFactory.create_project_manager
        }

        if role.lower() in role_methods:
            return role_methods[role.lower()](config, tools=tools)
        else:
            # Create custom agent
            optimized_config = AgentFactory._optimize_config_for_role(config, role)
            llm = optimized_config.create_crewai_llm()
            
            if llm is None:
                llm = optimized_config.to_crewai_format()

            agent_kwargs = {
                "role": role,
                "goal": goal,
                "backstory": backstory,
                "llm": llm,
                "verbose": optimized_config.verbose,
                **kwargs
            }
            
            if tools:
                agent_kwargs["tools"] = tools

            return Agent(**agent_kwargs)

    async def create_agents_batch_async(
        self,
        agent_configs: List[Dict[str, Any]],
        config: LLMConfig
    ) -> List[AsyncOperationResult]:
        """
        Create multiple agents concurrently
        
        Args:
            agent_configs: List of agent configuration dictionaries
            config: Base LLM configuration
            
        Returns:
            List of AsyncOperationResult objects
        """
        # Validate configurations first
        validated_configs = []
        for agent_config in agent_configs:
            try:
                validator = AgentConfigValidator(**agent_config)
                validated_configs.append(validator.model_dump())
            except Exception as e:
                raise ValidationError(f"Invalid agent configuration: {e}")

        # Create agents concurrently
        tasks = []
        for agent_config in validated_configs:
            task = self.create_agent_async(
                config=config,
                role=agent_config["role"],
                goal=agent_config["goal"],
                backstory=agent_config["backstory"],
                allow_delegation=agent_config.get("allow_delegation", False),
                allow_code_execution=agent_config.get("allow_code_execution", False),
                verbose=agent_config.get("verbose", True)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        operations = []
        for result in results:
            if isinstance(result, Exception):
                # Create failed operation for exceptions
                operation_id = self._generate_operation_id()
                operations.append(AsyncOperationResult(
                    operation_id=operation_id,
                    status=AsyncOperationStatus.FAILED,
                    error=result,
                    end_time=time.time()
                ))
            else:
                operations.append(result)

        return operations

    async def create_development_team_async(
        self,
        config: LLMConfig,
        project_type: str = "web",
        team_size: str = "standard"
    ) -> AsyncOperationResult:
        """
        Create a complete development team asynchronously
        
        Args:
            config: LLM configuration
            project_type: Type of project
            team_size: Size of team (minimal, standard, large)
            
        Returns:
            AsyncOperationResult with team agents
        """
        operation_id = self._generate_operation_id()
        operation = AsyncOperationResult(
            operation_id=operation_id,
            status=AsyncOperationStatus.PENDING,
            metadata={
                "operation_type": "team_creation",
                "project_type": project_type,
                "team_size": team_size
            }
        )
        
        self.active_operations[operation_id] = operation

        try:
            operation.status = AsyncOperationStatus.RUNNING
            
            # Define team configurations based on size
            team_configs = {
                "minimal": [
                    {
                        "role": "developer",
                        "goal": f"Implement {project_type} application features",
                        "backstory": f"Skilled {project_type} developer with full-stack capabilities",
                        "allow_code_execution": True
                    }
                ],
                "standard": [
                    {
                        "role": "tech_lead",
                        "goal": "Provide technical leadership and architecture guidance",
                        "backstory": "Senior technical leader with expertise in system design",
                        "allow_delegation": True
                    },
                    {
                        "role": "developer",
                        "goal": f"Implement {project_type} application features",
                        "backstory": f"Experienced {project_type} developer",
                        "allow_code_execution": True
                    },
                    {
                        "role": "reviewer",
                        "goal": "Review code quality and ensure best practices",
                        "backstory": "Quality-focused code reviewer with attention to detail",
                        "allow_code_execution": False
                    }
                ],
                "large": [
                    {
                        "role": "tech_lead",
                        "goal": "Provide strategic technical leadership",
                        "backstory": "Senior technical leader with architecture expertise",
                        "allow_delegation": True
                    },
                    {
                        "role": "developer",
                        "goal": f"Develop frontend for {project_type} application",
                        "backstory": "Frontend developer specialized in user interfaces",
                        "allow_code_execution": True
                    },
                    {
                        "role": "developer",
                        "goal": f"Develop backend for {project_type} application",
                        "backstory": "Backend developer specialized in server-side logic",
                        "allow_code_execution": True
                    },
                    {
                        "role": "reviewer",
                        "goal": "Review code quality and security",
                        "backstory": "Security-focused code reviewer",
                        "allow_code_execution": False
                    },
                    {
                        "role": "manager",
                        "goal": "Manage project timeline and coordination",
                        "backstory": "Project manager with technical background",
                        "allow_delegation": True
                    }
                ]
            }

            agent_configs = team_configs.get(team_size, team_configs["standard"])
            team_results = await self.create_agents_batch_async(agent_configs, config)
            
            # Extract successful agents
            agents = []
            errors = []
            
            for result in team_results:
                if result.status == AsyncOperationStatus.COMPLETED:
                    agents.append(result.result)
                else:
                    errors.append(result.error)

            if errors:
                operation.error = Exception(f"Some agents failed to create: {errors}")
                operation.status = AsyncOperationStatus.FAILED
            else:
                operation.result = agents
                operation.status = AsyncOperationStatus.COMPLETED
                
            operation.end_time = time.time()
            if operation.metadata is None:
                operation.metadata = {}
            operation.metadata.update({
                "agents_created": len(agents),
                "errors_count": len(errors)
            })

        except Exception as e:
            operation.error = e
            operation.status = AsyncOperationStatus.FAILED
            operation.end_time = time.time()

        return operation

    async def execute_tasks_async(
        self,
        tasks: List[Task],
        agents: List[Agent],
        execution_mode: str = "parallel"
    ) -> AsyncOperationResult:
        """
        Execute tasks asynchronously
        
        Args:
            tasks: List of tasks to execute
            agents: List of agents to execute tasks
            execution_mode: "parallel" or "sequential"
            
        Returns:
            AsyncOperationResult with execution results
        """
        operation_id = self._generate_operation_id()
        operation = AsyncOperationResult(
            operation_id=operation_id,
            status=AsyncOperationStatus.PENDING,
            metadata={
                "operation_type": "task_execution",
                "execution_mode": execution_mode,
                "task_count": len(tasks)
            }
        )
        
        self.active_operations[operation_id] = operation

        try:
            operation.status = AsyncOperationStatus.RUNNING
            
            if execution_mode == "parallel":
                # Execute tasks in parallel
                loop = asyncio.get_event_loop()
                tasks_futures = [
                    loop.run_in_executor(
                        self.executor,
                        self._execute_task_sync,
                        task, agents
                    )
                    for task in tasks
                ]
                
                results = await asyncio.gather(*tasks_futures, return_exceptions=True)
                
            else:  # sequential
                results = []
                for task in tasks:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.executor,
                        self._execute_task_sync,
                        task, agents
                    )
                    results.append(result)

            operation.result = results
            operation.status = AsyncOperationStatus.COMPLETED
            operation.end_time = time.time()

        except Exception as e:
            operation.error = e
            operation.status = AsyncOperationStatus.FAILED
            operation.end_time = time.time()

        return operation

    def _execute_task_sync(self, task: Task, agents: List[Agent]) -> Any:
        """Synchronous task execution for thread pool"""
        # Create a simple crew for task execution
        # Cast agents to the expected type for Crew
        base_agents: List[BaseAgent] = list(agents)
        crew = Crew(
            agents=base_agents,
            tasks=[task],
            verbose=True
        )
        return crew.kickoff()

    async def get_operation_status(self, operation_id: str) -> Optional[AsyncOperationResult]:
        """Get status of an async operation"""
        return self.active_operations.get(operation_id)

    async def wait_for_operation(
        self,
        operation_id: str,
        timeout: Optional[float] = None
    ) -> AsyncOperationResult:
        """
        Wait for an operation to complete
        
        Args:
            operation_id: ID of operation to wait for
            timeout: Optional timeout in seconds
            
        Returns:
            Completed AsyncOperationResult
            
        Raises:
            asyncio.TimeoutError: If timeout is reached
            KeyError: If operation ID not found
        """
        if operation_id not in self.active_operations:
            raise KeyError(f"Operation {operation_id} not found")

        start_time = time.time()
        
        while True:
            operation = self.active_operations[operation_id]
            
            if operation.is_complete:
                return operation
            
            if timeout and (time.time() - start_time) > timeout:
                operation.status = AsyncOperationStatus.CANCELLED
                operation.end_time = time.time()
                raise asyncio.TimeoutError(f"Operation {operation_id} timed out")
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

    async def cancel_operation(self, operation_id: str) -> bool:
        """
        Cancel an async operation
        
        Args:
            operation_id: ID of operation to cancel
            
        Returns:
            True if operation was cancelled, False if not found or already complete
        """
        operation = self.active_operations.get(operation_id)
        
        if not operation or operation.is_complete:
            return False
        
        operation.status = AsyncOperationStatus.CANCELLED
        operation.end_time = time.time()
        return True

    def get_active_operations(self) -> Dict[str, AsyncOperationResult]:
        """Get all active operations"""
        return {
            op_id: op for op_id, op in self.active_operations.items()
            if not op.is_complete
        }

    def get_completed_operations(self) -> Dict[str, AsyncOperationResult]:
        """Get all completed operations"""
        return {
            op_id: op for op_id, op in self.active_operations.items()
            if op.is_complete
        }

    def cleanup_operations(self, max_age_hours: float = 24.0) -> int:
        """
        Cleanup old completed operations
        
        Args:
            max_age_hours: Maximum age in hours for keeping operations
            
        Returns:
            Number of operations cleaned up
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        to_remove = []
        for op_id, operation in self.active_operations.items():
            if (operation.is_complete and 
                operation.end_time and 
                (current_time - operation.end_time) > max_age_seconds):
                to_remove.append(op_id)
        
        for op_id in to_remove:
            del self.active_operations[op_id]
        
        return len(to_remove)

    async def shutdown(self):
        """Shutdown the async factory and cleanup resources"""
        # Cancel all pending operations
        for operation in self.active_operations.values():
            if not operation.is_complete:
                operation.status = AsyncOperationStatus.CANCELLED
                operation.end_time = time.time()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)

    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.executor.shutdown(wait=False)
        except:
            pass


class AsyncCrewManager:
    """
    Asynchronous crew manager for managing multiple crews concurrently
    """
    
    def __init__(self, agent_factory: AsyncAgentFactory):
        """
        Initialize async crew manager
        
        Args:
            agent_factory: Async agent factory instance
        """
        self.agent_factory = agent_factory
        self.active_crews: Dict[str, Dict[str, Any]] = {}

    async def create_and_run_crew_async(
        self,
        config: LLMConfig,
        project_type: str = "web",
        team_size: str = "standard",
        task_descriptions: Optional[List[str]] = None
    ) -> AsyncOperationResult:
        """
        Create and run a crew asynchronously
        
        Args:
            config: LLM configuration
            project_type: Type of project
            team_size: Size of team
            task_descriptions: Optional custom task descriptions
            
        Returns:
            AsyncOperationResult with crew execution results
        """
        operation_id = self.agent_factory._generate_operation_id()
        operation = AsyncOperationResult(
            operation_id=operation_id,
            status=AsyncOperationStatus.PENDING,
            metadata={
                "operation_type": "crew_execution",
                "project_type": project_type,
                "team_size": team_size
            }
        )
        
        self.agent_factory.active_operations[operation_id] = operation

        try:
            operation.status = AsyncOperationStatus.RUNNING
            
            # Create team asynchronously
            team_result = await self.agent_factory.create_development_team_async(
                config, project_type, team_size
            )
            
            if team_result.status != AsyncOperationStatus.COMPLETED:
                operation.error = team_result.error
                operation.status = AsyncOperationStatus.FAILED
                operation.end_time = time.time()
                return operation
            
            agents = team_result.result
            
            # Create default tasks if none provided
            if not task_descriptions:
                task_descriptions = [
                    f"Plan and design the {project_type} application architecture",
                    f"Implement core features for the {project_type} application",
                    f"Review code quality and ensure best practices",
                    f"Coordinate project delivery and documentation"
                ]
            
            # Create tasks
            tasks = []
            for i, description in enumerate(task_descriptions[:len(agents)]):
                task = Task(
                    description=description,
                    agent=agents[i],
                    expected_output=f"Completed task: {description}"
                )
                tasks.append(task)
            
            # Execute crew
            loop = asyncio.get_event_loop()
            # Cast agents to the expected type for Crew
            base_agents: List[BaseAgent] = list(agents)
            crew = Crew(
                agents=base_agents,
                tasks=tasks,
                verbose=True
            )
            
            result = await loop.run_in_executor(
                self.agent_factory.executor,
                crew.kickoff
            )
            
            operation.result = {
                "crew_result": result,
                "agents_count": len(agents),
                "tasks_count": len(tasks),
                "project_type": project_type
            }
            operation.status = AsyncOperationStatus.COMPLETED
            operation.end_time = time.time()

        except Exception as e:
            operation.error = e
            operation.status = AsyncOperationStatus.FAILED
            operation.end_time = time.time()

        return operation


# Utility functions for async operations
async def create_agents_concurrently(
    configs: List[Dict[str, Any]],
    llm_config: LLMConfig,
    max_workers: int = 4
) -> List[AsyncOperationResult]:
    """
    Utility function to create multiple agents concurrently
    
    Args:
        configs: List of agent configurations
        llm_config: LLM configuration
        max_workers: Maximum concurrent operations
        
    Returns:
        List of AsyncOperationResult objects
    """
    factory = AsyncAgentFactory(max_workers=max_workers)
    
    try:
        results = await factory.create_agents_batch_async(configs, llm_config)
        return results
    finally:
        await factory.shutdown()


async def run_development_workflow_async(
    project_type: str,
    llm_config: LLMConfig,
    team_size: str = "standard",
    custom_tasks: Optional[List[str]] = None
) -> AsyncOperationResult:
    """
    Utility function to run a complete development workflow asynchronously
    
    Args:
        project_type: Type of project to develop
        llm_config: LLM configuration
        team_size: Size of development team
        custom_tasks: Optional custom task descriptions
        
    Returns:
        AsyncOperationResult with workflow results
    """
    factory = AsyncAgentFactory()
    manager = AsyncCrewManager(factory)
    
    try:
        result = await manager.create_and_run_crew_async(
            config=llm_config,
            project_type=project_type,
            team_size=team_size,
            task_descriptions=custom_tasks
        )
        return result
    finally:
        await factory.shutdown()


# Export main classes and functions
__all__ = [
    'AsyncAgentFactory',
    'AsyncCrewManager',
    'AsyncOperationResult',
    'AsyncOperationStatus',
    'create_agents_concurrently',
    'run_development_workflow_async'
]
