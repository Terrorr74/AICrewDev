"""Test the LLM configuration and agent factory"""

import os
import unittest
from src.config import LLMConfig, LLMProvider
from src.agents.agent_factory import AgentFactory

class TestLLMConfiguration(unittest.TestCase):
    """Test cases for LLM configuration"""
    
    def setUp(self):
        """Set up test cases"""
        # Save original environment variables
        self.original_env = {
            key: os.environ.get(key)
            for key in ["LLM_PROVIDER", "LLM_MODEL_NAME", "LLM_API_KEY", "LLM_API_BASE"]
        }
        
    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    
    def test_default_config(self):
        """Test default LLM configuration"""
        # Clear any existing LLM environment variables
        for key in ["LLM_PROVIDER", "LLM_MODEL_NAME", "LLM_API_KEY", "LLM_API_BASE", "LLM_TEMPERATURE"]:
            os.environ.pop(key, None)
            
        config = LLMConfig.get_default_config()
        self.assertEqual(config.provider, LLMProvider.OLLAMA)
        self.assertEqual(config.model_name, "llama2")
        self.assertEqual(config.temperature, 0.5)
        
    def test_custom_config(self):
        """Test custom LLM configuration"""
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["LLM_MODEL_NAME"] = "gpt-4"
        os.environ["LLM_API_KEY"] = "test-key"
        os.environ["LLM_TEMPERATURE"] = "0.5"
        
        config = LLMConfig.get_default_config()
        self.assertEqual(config.provider, LLMProvider.OPENAI)
        self.assertEqual(config.model_name, "gpt-4")
        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.temperature, 0.5)

class TestAgentFactory(unittest.TestCase):
    """Test cases for Agent Factory"""
    
    def setUp(self):
        """Set up test cases"""
        # Configure for Ollama to avoid API key requirements
        os.environ["LLM_PROVIDER"] = "ollama"
        os.environ["LLM_MODEL_NAME"] = "llama2"
    
    def test_create_tech_lead(self):
        """Test creating a tech lead agent"""
        agent = AgentFactory.create_tech_lead()
        self.assertEqual(agent.role, "Tech Lead")
        self.assertIn("architecture", agent.backstory.lower())
    
    def test_create_developer(self):
        """Test creating a developer agent"""
        agent = AgentFactory.create_developer()
        self.assertEqual(agent.role, "Developer")
        self.assertIn("problem-solving", agent.backstory.lower())
    
    def test_create_code_reviewer(self):
        """Test creating a code reviewer agent"""
        agent = AgentFactory.create_code_reviewer()
        self.assertEqual(agent.role, "Code Reviewer")
        self.assertIn("review", agent.backstory.lower())
    
    def test_custom_llm_config(self):
        """Test creating an agent with custom LLM config"""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="codellama",
            temperature=0.5
        )
        agent = AgentFactory.create_tech_lead(config)
        self.assertEqual(agent.role, "Tech Lead")
        # Verify the LLM model configuration through the agent's llm property
        self.assertEqual(agent.llm.model, "codellama")

if __name__ == '__main__':
    unittest.main()
