"""
Task Factory Module

This module provides a factory for creating development tasks that can be
assigned to AI agents. Each task is configured with specific requirements,
descriptions, and success criteria.

Classes:
    TaskFactory: Creates and configures development tasks

Example:
    >>> tech_lead = AgentFactory.create_tech_lead(llm)
    >>> design_task = TaskFactory.create_design_task(tech_lead)
"""

from crewai import Task

class TaskFactory:
    """
    Factory class for creating development tasks.
    
    This class provides static methods to create different types of tasks
    that can be assigned to AI agents. Each task is configured with
    appropriate parameters and success criteria.
    
    The factory ensures consistent task creation and proper assignment
    to qualified agents.
    """
    
    @staticmethod
    def create_design_task(tech_lead):
        """Create a system design task"""
        return Task(
            description="Design the system architecture and component interactions",
            agent=tech_lead,
            expected_output="A detailed system architecture design document"
        )
    
    @staticmethod
    def create_development_task(developer, spec):
        """Create a development task"""
        return Task(
            description=f"Implement the following specification: {spec}",
            agent=developer,
            expected_output="Implementation code meeting the specification"
        )
    
    @staticmethod
    def create_review_task(reviewer, code):
        """Create a code review task"""
        return Task(
            description=f"Review the following code implementation: {code}",
            agent=reviewer,
            expected_output="Code review feedback and suggestions"
        )
