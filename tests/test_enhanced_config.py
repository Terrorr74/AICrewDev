"""
Test suite for improved LLM configuration and Agent Factory.

Tests the enhanced configuration system and CrewAI integration.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.config.llm_config import LLMConfig, LLMProvider
from src.agents.agent_factory import AgentFactory

class TestLLMConfig:
    """Test the LLM configuration class"""
    
    def test_default_config_creation(self):
        """Test creating default configuration"""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "openai",
            "LLM_MODEL_NAME": "gpt-4o-mini",
            "LLM_TEMPERATURE": "0.7"
        }):
            config = LLMConfig.get_default_config()
            
            assert config.provider == LLMProvider.OPENAI
            assert config.model_name == "gpt-4o-mini"
            assert config.temperature == 0.7
            assert config.verbose is True
    
    def test_provider_validation(self):
        """Test provider validation and fallback"""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "invalid_provider"
        }):
            config = LLMConfig.get_default_config()
            assert config.provider == LLMProvider.OPENAI  # Should fallback
    
    def test_temperature_bounds(self):
        """Test temperature is properly bounded"""
        with patch.dict(os.environ, {
            "LLM_TEMPERATURE": "5.0"  # Too high
        }):
            config = LLMConfig.get_default_config()
            assert config.temperature <= 2.0
    
    def test_crewai_format_conversion(self):
        """Test conversion to CrewAI format"""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o"
        )
        assert config.to_crewai_format() == "openai/gpt-4o"
        
        config.provider = LLMProvider.ANTHROPIC
        config.model_name = "claude-3-haiku"
        assert config.to_crewai_format() == "anthropic/claude-3-haiku"
    
    def test_model_params_for_crewai(self):
        """Test getting parameters for CrewAI"""
        config = LLMConfig(
            temperature=0.5,
            max_tokens=1000,
            max_rpm=20,
            verbose=True
        )
        params = config.get_model_params_for_crewai()
        
        assert params["temperature"] == 0.5
        assert params["max_tokens"] == 1000
        assert params["max_rpm"] == 20
        assert params["verbose"] is True

class TestAgentFactory:
    """Test the Agent Factory class"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing"""
        return LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o-mini",
            temperature=0.7,
            verbose=True
        )
    
    def test_tech_lead_creation(self, mock_config):
        """Test creating a tech lead agent"""
        with patch('src.config.llm_config.ChatOpenAI') as mock_openai:
            mock_openai.return_value = MagicMock()
            
            agent = AgentFactory.create_tech_lead(mock_config)
            
            assert "Technical Lead" in agent.role
            assert agent.allow_delegation is True
            assert "strategic" in agent.goal.lower()
    
    def test_developer_creation(self, mock_config):
        """Test creating a developer agent"""
        with patch('src.config.llm_config.ChatOpenAI') as mock_openai:
            mock_openai.return_value = MagicMock()
            
            agent = AgentFactory.create_developer(mock_config, specialization="backend")
            
            assert "Backend Developer" in agent.role
            assert "backend" in agent.goal.lower()
            assert agent.allow_code_execution is True
    
    def test_code_reviewer_creation(self, mock_config):
        """Test creating a code reviewer agent"""
        with patch('src.config.llm_config.ChatOpenAI') as mock_openai:
            mock_openai.return_value = MagicMock()
            
            agent = AgentFactory.create_code_reviewer(mock_config)
            
            assert "Quality" in agent.role
            assert "review" in agent.goal.lower()
            assert agent.verbose is True
    
    def test_role_optimization(self, mock_config):
        """Test role-specific optimizations"""
        # Test manager role optimization
        optimized = AgentFactory._optimize_config_for_role(mock_config, "manager")
        assert optimized.temperature == 0.1  # Lower temperature for consistency
        
        # Test developer role optimization
        optimized = AgentFactory._optimize_config_for_role(mock_config, "developer")
        assert optimized.temperature == 0.3  # Balanced temperature
        
        # Test reviewer role optimization
        optimized = AgentFactory._optimize_config_for_role(mock_config, "reviewer")
        assert optimized.temperature == 0.2  # Lower temperature for accuracy

class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_full_workflow(self):
        """Test a complete workflow from config to agents"""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "openai",
            "LLM_MODEL_NAME": "gpt-4o-mini",
            "LLM_TEMPERATURE": "0.7",
            "LLM_VERBOSE": "true"
        }):
            with patch('src.config.llm_config.ChatOpenAI') as mock_openai:
                mock_openai.return_value = MagicMock()
                
                # Create configuration
                config = LLMConfig.get_default_config()
                
                # Create agents
                tech_lead = AgentFactory.create_tech_lead(config)
                developer = AgentFactory.create_developer(config)
                reviewer = AgentFactory.create_code_reviewer(config)
                
                # Verify all agents were created
                assert tech_lead is not None
                assert developer is not None
                assert reviewer is not None
                
                # Verify they have different roles
                roles = {tech_lead.role, developer.role, reviewer.role}
                assert len(roles) == 3  # All unique roles
    
    def test_provider_specific_models(self):
        """Test that provider-specific models are created correctly"""
        configs = [
            (LLMProvider.OPENAI, "gpt-4o"),
            (LLMProvider.ANTHROPIC, "claude-3-haiku"),
            (LLMProvider.OLLAMA, "llama3.1:8b")
        ]
        
        for provider, model in configs:
            config = LLMConfig(provider=provider, model_name=model)
            
            with patch(f'src.config.llm_config.Chat{provider.value.title()}') as mock_model:
                mock_model.return_value = MagicMock()
                
                llm = config.create_chat_model()
                assert llm is not None

if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
