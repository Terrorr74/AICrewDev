#!/usr/bin/env python3
"""
Simple Ollama Demo - A basic working example without complex agent interactions
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import AICrewDev

def main():
    """Run a simple Ollama demo with basic configuration"""
    
    print("🚀 AICrewDev Simple Ollama Demo")
    print("=" * 50)
    
    # Set minimal environment variables
    os.environ.setdefault("CHROMA_OPENAI_API_KEY", "dummy-key-for-local-testing")
    
    try:
        # Initialize with simple configuration
        ai_crew = AICrewDev()
        
        print("✅ AICrewDev initialized successfully")
        
        # Get basic status without running complex crews
        status = ai_crew.get_status()
        print(f"📊 System Status: {status}")
        
        # Test configuration validation
        print("\n🔧 Testing Configuration Validation...")
        
        # Import our validation system
        from src.config.validators import AgentConfigValidator, LLMConfigValidator
        
        # Test agent config validation
        agent_config = {
            "role": "developer",
            "goal": "Test the system functionality",
            "backstory": "A senior software developer with 5+ years of experience in testing systems",
            "verbose": True,
            "allow_delegation": False
        }
        
        agent_validator = AgentConfigValidator(**agent_config)
        print(f"✅ Agent Config Valid: {agent_validator.role}")
        
        # Test LLM config validation
        llm_config = {
            "provider": "ollama",
            "model_name": "llama2",
            "temperature": 0.7,
            "max_tokens": 1000,
            "timeout": 60
        }
        
        llm_validator = LLMConfigValidator(**llm_config)
        print(f"✅ LLM Config Valid: {llm_validator.provider}/{llm_validator.model_name}")
        
        print("\n🎯 All validations passed!")
        print("✨ Simple demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
