#!/usr/bin/env python3
"""
Test script to verify the fixed CrewAI delegation issues

This script tests both delegation-enabled and delegation-disabled modes
to ensure the fixes work properly.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import AICrewDev
from src.config.llm_config import LLMConfig, LLMProvider

def test_without_delegation():
    """Test crew execution without delegation (should work)"""
    print("🧪 Testing crew execution WITHOUT delegation...")
    
    try:
        # Create AICrewDev instance
        ai_crew = AICrewDev()
        
        # Run without delegation
        result = ai_crew.run(
            project_type="web",
            use_crew_manager=True,
            enable_delegation=False
        )
        
        print("✅ SUCCESS: Crew executed without delegation!")
        print(f"📄 Result length: {len(str(result))} characters")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_with_delegation():
    """Test crew execution with delegation (may have issues)"""
    print("\n🧪 Testing crew execution WITH delegation...")
    
    try:
        # Create AICrewDev instance
        ai_crew = AICrewDev()
        
        # Run with delegation
        result = ai_crew.run(
            project_type="web",
            use_crew_manager=True,
            enable_delegation=True
        )
        
        print("✅ SUCCESS: Crew executed with delegation!")
        print(f"📄 Result length: {len(str(result))} characters")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        if "unhashable type" in str(e):
            print("💡 This is the delegation tool error we're trying to fix")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Fixed CrewAI Delegation Issues")
    print("=" * 50)
    
    # Test without delegation first
    success_no_delegation = test_without_delegation()
    
    # Test with delegation
    success_with_delegation = test_with_delegation()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print(f"   Without delegation: {'✅ PASS' if success_no_delegation else '❌ FAIL'}")
    print(f"   With delegation: {'✅ PASS' if success_with_delegation else '❌ FAIL'}")
    
    if success_no_delegation:
        print("\n🎉 Great! Basic crew functionality is working.")
        if not success_with_delegation:
            print("🔧 Delegation still needs work, but basic functionality is available.")
    else:
        print("\n⚠️  Basic crew functionality is not working. Check your configuration.")

if __name__ == "__main__":
    main()
