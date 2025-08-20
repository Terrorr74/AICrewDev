#!/usr/bin/env python3
"""
Simple validation of our enhanced configuration files.
This script tests the syntax and basic structure without external dependencies.
"""

import sys
import os
import ast

def validate_python_syntax(file_path):
    """Validate that a Python file has correct syntax"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        print(f"✅ {os.path.basename(file_path)}: Syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ {os.path.basename(file_path)}: Syntax error - {e}")
        return False
    except Exception as e:
        print(f"❌ {os.path.basename(file_path)}: Error - {e}")
        return False

def check_file_structure():
    """Check that all expected files exist"""
    expected_files = [
        "src/config/llm_config.py",
        "src/agents/agent_factory.py",
        "examples/llm_config_example.py",
        "config/agents.yaml.example",
        ".env.example"
    ]
    
    print("📁 Checking file structure...")
    all_exist = True
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: Found")
        else:
            print(f"❌ {file_path}: Missing")
            all_exist = False
    
    return all_exist

def check_configuration_completeness():
    """Check that configuration files have expected content"""
    print("\n🔍 Checking configuration completeness...")
    
    # Check .env.example
    try:
        with open(".env.example", "r") as f:
            env_content = f.read()
        
        required_vars = ["LLM_PROVIDER", "LLM_MODEL_NAME", "LLM_TEMPERATURE", "OPENAI_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ .env.example missing variables: {missing_vars}")
            return False
        else:
            print("✅ .env.example: All required variables present")
    except Exception as e:
        print(f"❌ .env.example: Error reading file - {e}")
        return False
    
    # Check agents.yaml.example
    try:
        with open("config/agents.yaml.example", "r") as f:
            yaml_content = f.read()
        
        required_sections = ["agents:", "tasks:"]
        missing_sections = []
        
        for section in required_sections:
            if section not in yaml_content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ agents.yaml.example missing sections: {missing_sections}")
            return False
        else:
            print("✅ agents.yaml.example: All required sections present")
    except Exception as e:
        print(f"❌ agents.yaml.example: Error reading file - {e}")
        return False
    
    return True

def main():
    """Main validation function"""
    print("🚀 Enhanced Configuration Validation\n")
    
    success = True
    
    # Check file structure
    success &= check_file_structure()
    
    print("\n🐍 Validating Python syntax...")
    
    # Validate Python files
    python_files = [
        "src/config/llm_config.py",
        "src/agents/agent_factory.py", 
        "examples/llm_config_example.py",
        "test_config.py"
    ]
    
    for file_path in python_files:
        if os.path.exists(file_path):
            success &= validate_python_syntax(file_path)
    
    # Check configuration completeness
    success &= check_configuration_completeness()
    
    print(f"\n{'='*50}")
    if success:
        print("🎉 All validations passed!")
        print("\n📋 Your enhanced LLM configuration is ready!")
        print("✨ Key improvements made:")
        print("   • LLMConfig with proper CrewAI integration")
        print("   • Role-specific agent optimization")
        print("   • Comprehensive provider support")
        print("   • Environment-based configuration")
        print("   • Example usage patterns")
        print("\n🚀 Next steps:")
        print("   1. Copy .env.example to .env and configure your API keys")
        print("   2. Run examples/llm_config_example.py to test")
        print("   3. Use AgentFactory to create optimized agents")
    else:
        print("❌ Some validations failed!")
        print("   Please check the errors above and fix them.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
