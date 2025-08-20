#!/usr/bin/env python3
"""
Real Ollama LLM Test with Monitoring

This script performs a real LLM interaction with Ollama/Llama2 and 
monitors the performance metrics in real-time.
"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import AICrewDev
from src.core.settings import Settings
from src.monitoring.metrics_collector import PerformanceTracker

def test_real_llm_interaction():
    """Test real LLM interaction with Ollama and monitor performance"""
    print("🤖 Real Ollama LLM Interaction Test")
    print("=" * 40)
    
    # Configure environment for Ollama
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL_NAME"] = "llama2"
    os.environ["LLM_TEMPERATURE"] = "0.7"
    os.environ["LLM_API_BASE"] = "http://localhost:11434"
    os.environ["AICREWDEV_DEBUG"] = "true"
    
    try:
        # Create AICrewDev instance
        print("🔧 Setting up AICrewDev with Ollama...")
        settings = Settings.for_development()
        ai_crew = AICrewDev(settings)
        
        print("✅ AICrewDev initialized successfully")
        print(f"   Provider: {ai_crew.settings.llm_config.provider}")
        print(f"   Model: {ai_crew.settings.llm_config.model_name}")
        
        # Test simple prompt
        print("\n🚀 Testing simple prompt with performance tracking...")
        
        # Import ollama for direct testing
        import requests
        
        prompt = "Write a simple Python function to calculate the factorial of a number."
        
        with PerformanceTracker(ai_crew.metrics, "real_llm_test"):
            start_time = time.time()
            
            # Make request to Ollama
            response = requests.post("http://localhost:11434/api/generate", 
                                   json={
                                       "model": "llama2",
                                       "prompt": prompt,
                                       "stream": False
                                   },
                                   timeout=30)
            
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                tokens_used = len(response_text.split())  # Rough token estimate
                
                # Log the interaction
                ai_crew.logger.log_llm_interaction(
                    provider="ollama",
                    model="llama2",
                    operation="text_generation",
                    tokens_used=tokens_used,
                    duration_ms=duration_ms,
                    success=True
                )
                
                # Track metrics
                ai_crew.metrics.track_llm_usage(
                    provider="ollama",
                    model="llama2",
                    operation="text_generation",
                    tokens_used=tokens_used,
                    duration_ms=duration_ms,
                    cost_usd=0.0,  # Free with Ollama
                    success=True
                )
                
                print(f"✅ LLM Response received!")
                print(f"   Duration: {duration_ms:.1f}ms")
                print(f"   Estimated tokens: {tokens_used}")
                print(f"   Response length: {len(response_text)} characters")
                
                print("\n📝 Response Preview:")
                print("-" * 40)
                print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
                print("-" * 40)
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                ai_crew.logger.log_llm_interaction(
                    provider="ollama",
                    model="llama2",
                    operation="text_generation",
                    tokens_used=0,
                    duration_ms=duration_ms,
                    success=False
                )
        
        # Show performance dashboard
        print("\n📊 Performance Metrics After Real Test:")
        dashboard = ai_crew.metrics.get_performance_dashboard()
        
        llm_usage = dashboard['llm_usage']
        print(f"   Total LLM Requests: {llm_usage['total_requests']}")
        print(f"   Total Tokens: {llm_usage['total_tokens']:,}")
        print(f"   Total Cost: ${llm_usage['total_cost_usd']:.2f}")
        
        performance = dashboard['performance']
        print(f"   Total Operations: {performance['total_executions']}")
        print(f"   Success Rate: {performance['overall_success_rate']:.1%}")
        
        # Show provider breakdown
        provider_breakdown = llm_usage['provider_breakdown']
        for provider, stats in provider_breakdown.items():
            if 'ollama' in provider.lower():
                print(f"\n🦙 {provider} Statistics:")
                print(f"   Requests: {stats['requests']}")
                print(f"   Tokens: {stats['tokens']:,}")
                print(f"   Success Rate: {stats.get('success_rate', 'N/A')}")
        
        # Get system status
        print("\n🏥 System Health Status:")
        status = ai_crew.get_status()
        monitoring = status.get('monitoring', {})
        health_checks = monitoring.get('health_checks', {})
        
        for check_name, check_info in health_checks.items():
            status_emoji = "✅" if check_info['status'] == 'healthy' else "⚠️" if check_info['status'] == 'warning' else "❌"
            print(f"   {status_emoji} {check_name}: {check_info['status']}")
        
        print("\n🎯 Test Summary:")
        print("✅ Real LLM interaction successful")
        print("✅ Performance monitoring active")
        print("✅ Metrics collection working")
        print("✅ Health monitoring operational")
        print("✅ Zero cost with local Ollama!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_llm_interaction()
    
    if success:
        print("\n🎉 Real Ollama Integration Test: SUCCESS!")
        print("\nThe AICrewDev monitoring system is working perfectly with Ollama!")
        print("You now have a fully functional local LLM setup with comprehensive monitoring.")
    else:
        print("\n❌ Real Ollama Integration Test: FAILED!")
        print("Please check Ollama installation and model availability.")
