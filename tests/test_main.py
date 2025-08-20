"""Test the main AICrewDev functionality"""

import unittest
from src.main import AICrewDev
from src.agents.agent_factory import AgentFactory
from src.tasks.task_factory import TaskFactory

class TestAICrewDev(unittest.TestCase):
    """Test cases for AICrewDev class"""
    
    def setUp(self):
        """Set up test cases"""
        self.ai_crew = AICrewDev()
    
    def test_create_agents(self):
        """Test agent creation"""
        agents = self.ai_crew.create_agents()
        self.assertEqual(len(agents), 3)
        
    def test_create_tasks(self):
        """Test task creation"""
        tasks = self.ai_crew.create_tasks()
        self.assertEqual(len(tasks), 3)

if __name__ == '__main__':
    unittest.main()
