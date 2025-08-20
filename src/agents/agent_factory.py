"""
Agent Factory Module

This module provides a factory for creating specialized AI agents with
specific roles and capabilities. Each agent is configured with specific
goals and backstories relevant to their role in the development process.

Classes:
    AgentFactory: Creates and configures AI agents for different roles

Example:
    >>> from langchain_openai import ChatOpenAI
    >>> llm = ChatOpenAI(temperature=0.7)
    >>> tech_lead = AgentFactory.create_tech_lead(llm)
"""

from crewai import Agent
from langchain_openai import ChatOpenAI

class AgentFactory:
    """
    Factory class for creating specialized AI agents.
    
    This class provides static methods to create different types of AI agents,
    each with specific roles, goals, and capabilities. The factory ensures
    consistent agent creation with appropriate configurations.
    """
    
    @staticmethod
    def create_tech_lead(llm):
        """Create a Tech Lead agent"""
        return Agent(
            role='Tech Lead',
            goal='Ensure technical excellence and project success',
            backstory='Experienced technical leader with focus on architecture and code quality',
            llm=llm
        )
    
    @staticmethod
    def create_developer(llm):
        """Create a Developer agent"""
        return Agent(
            role='Developer',
            goal='Write clean, efficient, and maintainable code',
            backstory='Skilled developer with strong problem-solving abilities',
            llm=llm
        )
    
    @staticmethod
    def create_code_reviewer(llm):
        """Create a Code Reviewer agent"""
        return Agent(
            role='Code Reviewer',
            goal='Ensure code quality and best practices',
            backstory='Detail-oriented developer with extensive experience in code review',
            llm=llm
        )
