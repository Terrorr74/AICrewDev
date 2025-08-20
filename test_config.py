#!/usr/bin/env python3
"""
Simple test script to validate the enhanced LLM configuration works.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("🔧 Testing LLM Configuration...")
    
    try:
        from config.llm_config import LLMConfig, LLMProvider
        print("✅ Successfully imported LLMConfig")
        
        # Test basic config creation
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-4o-mini",
            temperature=0.7
        )
        print(f"✅ Created config: {config.provider.value}/{config.model_name}")
        
        # Test CrewAI format
        crewai_format = config.to_crewai_format()
        print(f"✅ CrewAI format: {crewai_format}")
        
        # Test parameter extraction
        params = config.get_model_params_for_crewai()
        print(f"✅ Parameters: {params}")
        
    except Exception as e:
        print(f"❌ LLMConfig test failed: {e}")
        return False
    
    print("\n🤖 Testing Agent Factory...")
    
    try:
        from agents.agent_factory import AgentFactory
        print("✅ Successfully imported AgentFactory")
        
        # Test role optimization
        optimized = AgentFactory._optimize_config_for_role(config, "manager")
        print(f"✅ Manager optimization: temperature={optimized.temperature}")
        
        optimized = AgentFactory._optimize_config_for_role(config, "developer")
        print(f"✅ Developer optimization: temperature={optimized.temperature}")
        
    except Exception as e:
        print(f"❌ AgentFactory test failed: {e}")
        return False
    
    print("\n🌍 Testing Environment Configuration...")
    
    try:
        # Test with environment variables
        os.environ["LLM_PROVIDER"] = "anthropic"
        os.environ["LLM_MODEL_NAME"] = "claude-3-haiku"
        os.environ["LLM_TEMPERATURE"] = "0.5"
        
        env_config = LLMConfig.get_default_config()
        print(f"✅ Environment config: {env_config.provider.value}/{env_config.model_name}")
        print(f"✅ Temperature from env: {env_config.temperature}")
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    return True

def test_configuration_examples():
    """Test different provider configurations"""
    print("\n📋 Testing Provider Configurations...")
    
    providers_and_models = [
        (LLMProvider.OPENAI, "gpt-4o"),
        (LLMProvider.ANTHROPIC, "claude-3-sonnet"),
        (LLMProvider.OLLAMA, "llama3.1:8b")
    ]
    
    for provider, model in providers_and_models:
        try:
            config = LLMConfig(provider=provider, model_name=model)
            crewai_format = config.to_crewai_format()
            print(f"✅ {provider.value}: {crewai_format}")
        except Exception as e:
            print(f"❌ {provider.value} configuration failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Enhanced Configuration Tests\n")
    
    success = True
    success &= test_basic_functionality()
    success &= test_configuration_examples()
    
    if success:
        print("\n🎯 All tests completed successfully!")
        print("\n📝 Your enhanced LLM configuration is ready to use!")
        print("   • Use LLMConfig.get_default_config() for environment-based setup")
        print("   • Use AgentFactory methods to create optimized agents")
        print("   • Check examples/llm_config_example.py for usage patterns")
    else:
        print("\n❌ Some tests failed. Check the configuration files.")
        sys.exit(1)
