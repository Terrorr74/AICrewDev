"""
Data models for AICrewDev components.
"""

try:
    from .agent_models import AgentSpecification, AgentRole
    from .task_models import TaskSpecification, TaskType
    __all__ = ["AgentSpecification", "AgentRole", "TaskSpecification", "TaskType"]
except ImportError:
    # Graceful handling if modules not available
    __all__ = []
