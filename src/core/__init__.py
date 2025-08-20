"""
Core module for AICrewDev business logic and settings.
"""

try:
    from .settings import Settings
    from .crew_manager import CrewManager
    __all__ = ["Settings", "CrewManager"]
except ImportError:
    # Graceful handling if modules not available
    __all__ = []
