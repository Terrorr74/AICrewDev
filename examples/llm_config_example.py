#!/usr/bin/env python3
"""
Enhanced LLM Configuration Example - Fixed Version

This example demonstrates the improved LLM configuration system using
CrewAI best practices based on the latest Context7 documentation.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.llm_config import LLMConfig, LLMProvider
from src.agents.agent_factory import AgentFactory

def main():
    """Demonstrate the enhanced LLM configuration system."""
    
    print("🚀 Enhanced LLM Configuration with CrewAI Integration\n")
    
    # === 1. Environment-based Configuration ===
    print("📋 1. Environment-based Configuration")
    
    # Set up environment variables for testing
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LLM_MODEL_NAME"] = "gpt-4o-mini"
    os.environ["LLM_TEMPERATURE"] = "0.7"
    os.environ["LLM_VERBOSE"] = "true"
    
    # Create configuration from environment
    config = LLMConfig.get_default_config()
    print(f"✅ Provider: {config.provider}")
    print(f"✅ Model: {config.model_name}")
    print(f"✅ Temperature: {config.temperature}")
    print(f"✅ CrewAI Format: {config.to_crewai_format()}")
    
    # === 2. CrewAI LLM Instance Creation ===
    print(f"\n🤖 2. CrewAI LLM Instance Creation")
    
    crewai_llm = config.create_crewai_llm()
    if crewai_llm:
        print("✅ CrewAI LLM instance created successfully")
        print(f"   Type: {type(crewai_llm).__name__}")
    else:
        print("⚠️  CrewAI LLM not available, using string format fallback")
        print(f"   Format: {config.to_crewai_format()}")
    
    # === 3. Role-Specific Agent Creation ===
    print(f"\n👥 3. Role-Specific Agent Creation")
    
    try:
        # Create different types of agents
        tech_lead = AgentFactory.create_tech_lead(config)
        print(f"✅ Tech Lead: {tech_lead.role}")
        
        developer = AgentFactory.create_developer(config, specialization="backend")
        print(f"✅ Developer: {developer.role}")
        
        reviewer = AgentFactory.create_code_reviewer(config)
        print(f"✅ Reviewer: {reviewer.role}")
        
        manager = AgentFactory.create_project_manager(config)
        print(f"✅ Manager: {manager.role}")
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
    
    # === 4. Multi-Provider Configuration ===
    print(f"\n🔄 4. Multi-Provider Configuration")
    
    providers_to_test = [
        (LLMProvider.OPENAI, "gpt-4o-mini"),
        (LLMProvider.ANTHROPIC, "claude-3-haiku-20240307"),
        (LLMProvider.OLLAMA, "llama3.1:8b")
    ]
    
    for provider, model in providers_to_test:
        try:
            test_config = LLMConfig(
                provider=provider,
                model_name=model,
                temperature=0.5
            )
            
            crewai_format = test_config.to_crewai_format()
            params = test_config.get_model_params_for_crewai()
            
            print(f"✅ {provider.value}: {crewai_format}")
            print(f"   Params: {params}")
            
        except Exception as e:
            print(f"❌ {provider.value}: Configuration failed - {e}")
    
    # === 5. Recommended Models by Role ===
    print(f"\n💡 5. Recommended Models by Role")
    
    recommendations = AgentFactory.get_recommended_models_by_role()
    for role, models in recommendations.items():
        print(f"\n{role.replace('_', ' ').title()}:")
        for provider, model in models.items():
            print(f"  • {provider}: {model}")
    
    # === 6. Configuration Export ===
    print(f"\n📤 6. Configuration Export")
    
    provider_config = config.get_provider_specific_config()
    print("Provider-specific configuration:")
    for key, value in provider_config.items():
        if key != "api_key":  # Don't print sensitive information
            print(f"  {key}: {value}")
    
    print(f"\n🎉 Configuration demonstration completed successfully!")
    print("\n📝 Next Steps:")
    print("1. Set your API keys in environment variables")
    print("2. Use AgentFactory to create optimized agents")
    print("3. Configure CrewAI crews with these agents")
    print("4. Test with your specific use cases")

if __name__ == "__main__":
    main()
