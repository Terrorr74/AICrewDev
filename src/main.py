"""
AICrewDev Main Module

This module serves as the entry point for the AI development crew system.
It orchestrates the creation and execution of AI agents and their tasks.

Classes:
    AICrewDev: Main class that coordinates AI agents and tasks

Example:
    >>> ai_crew = AICrewDev()
    >>> result = ai_crew.run()
    >>> print(result)
"""

from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
from src.utils.environment import validate_environment
from src.agents.agent_factory import AgentFactory
from src.tasks.task_factory import TaskFactory

class AICrewDev:
    """
    Main class for managing AI development crew operations.
    
    This class handles the creation and coordination of AI agents,
    task assignment, and execution of the development workflow.
    
    Attributes:
        llm (ChatOpenAI): Language model instance for agent communication
    """

    def __init__(self):
        """
        Initialize the AICrewDev instance.
        
        Sets up the language model and validates the environment.
        Raises EnvironmentError if required variables are missing.
        """
        validate_environment()
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
        
    def create_agents(self):
        """Create specialized AI agents with specific roles"""
        tech_lead = Agent(
            role='Tech Lead',
            goal='Ensure technical excellence and project success',
            backstory='Experienced technical leader with focus on architecture and code quality',
            llm=self.llm
        )
        
        developer = Agent(
            role='Developer',
            goal='Write clean, efficient, and maintainable code',
            backstory='Skilled developer with strong problem-solving abilities',
            llm=self.llm
        )
        
        code_reviewer = Agent(
            role='Code Reviewer',
            goal='Ensure code quality and best practices',
            backstory='Detail-oriented developer with extensive experience in code review',
            llm=self.llm
        )
        
        return [tech_lead, developer, code_reviewer]
    
    def create_tasks(self):
        """
        Define development tasks and their workflows.
        
        Returns:
            list[Task]: List of tasks to be executed by the AI agents
        """
        agents = self.create_agents()
        tech_lead, developer, code_reviewer = agents
        
        design_task = TaskFactory.create_design_task(tech_lead)
        development_task = TaskFactory.create_development_task(
            developer,
            "Implement the core functionality based on the design"
        )
        review_task = TaskFactory.create_review_task(
            code_reviewer,
            "Review the implemented code for quality and best practices"
        )
        
        return [design_task, development_task, review_task]
    
    def run(self):
        """Execute the AI development workflow"""
        agents = self.create_agents()
        tasks = self.create_tasks()
        
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return result

if __name__ == "__main__":
    ai_crew = AICrewDev()
    result = ai_crew.run()
    print("Development Process Complete:", result)
