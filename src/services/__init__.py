"""
Service layer for AICrewDev business logic.
"""

try:
    from .agent_service import AgentService
    from .task_service import TaskService
    __all__ = ["AgentService", "TaskService"]
except ImportError:
    # Graceful handling if modules not available
    __all__ = []
