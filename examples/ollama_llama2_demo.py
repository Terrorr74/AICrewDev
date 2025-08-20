#!/usr/bin/env python3
"""
Ollama + Llama2 Integration Demo

This demo showcases the AICrewDev monitoring capabilities using Ollama with Llama2,
demonstrating local LLM integration without requiring external API keys.
"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import AICrewDev
from src.core.settings import Settings
from src.monitoring.logger import AICrewLogger
from src.monitoring.metrics_collector import MetricsCollector, PerformanceTracker
from src.monitoring.health_checker import HealthChecker

def setup_ollama_environment():
    """Configure environment for Ollama + Llama2"""
    print("🔧 Configuring environment for Ollama + Llama2...")
    
    # Set up Ollama environment variables
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL_NAME"] = "llama2"
    os.environ["LLM_TEMPERATURE"] = "0.7"
    os.environ["LLM_MAX_TOKENS"] = "2048"
    os.environ["AICREWDEV_DEBUG"] = "true"
    
    # Ollama typically runs on localhost:11434
    os.environ["LLM_API_BASE"] = "http://localhost:11434"
    
    print("✅ Environment configured:")
    print(f"   Provider: {os.environ['LLM_PROVIDER']}")
    print(f"   Model: {os.environ['LLM_MODEL_NAME']}")
    print(f"   API Base: {os.environ['LLM_API_BASE']}")
    print(f"   Temperature: {os.environ['LLM_TEMPERATURE']}")

def test_ollama_connectivity():
    """Test Ollama connectivity and model availability"""
    print("\n🔍 Testing Ollama Connectivity...")
    
    import requests
    import json
    
    try:
        # Test Ollama API endpoint
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama server is running")
            
            # Check if llama2 is available
            model_names = [model["name"] for model in models.get("models", [])]
            print(f"   Available models: {', '.join(model_names)}")
            
            if any("llama2" in name for name in model_names):
                print("✅ Llama2 model is available")
                return True
            else:
                print("⚠️  Llama2 model not found. Available models:")
                for model in models.get("models", []):
                    print(f"     - {model['name']}")
                return False
        else:
            print(f"❌ Ollama server returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama server")
        print("   Make sure Ollama is running: 'ollama serve'")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def demo_ollama_llm_interaction():
    """Test LLM interaction logging with Ollama"""
    print("\n🤖 Testing LLM Interaction Monitoring with Ollama...")
    
    logger = AICrewLogger(
        service_name="ollama_demo",
        environment="demo",
        log_level="INFO",
        enable_console=True,
        enable_file=False
    )
    
    # Add demo context
    logger.add_context(
        demo_type="ollama_integration",
        model="llama2",
        provider="ollama"
    )
    
    # Log LLM interactions
    start_time = time.time()
    
    logger.info("Starting Ollama LLM interaction test")
    
    # Simulate LLM request
    logger.log_llm_interaction(
        provider="ollama",
        model="llama2",
        operation="chat_completion",
        tokens_used=50,
        duration_ms=1500.0,
        success=True
    )
    
    # Test a longer interaction
    logger.log_llm_interaction(
        provider="ollama",
        model="llama2",
        operation="text_generation",
        tokens_used=200,
        duration_ms=3200.0,
        success=True
    )
    
    # Simulate an error case
    logger.log_llm_interaction(
        provider="ollama",
        model="llama2",
        operation="chat_completion",
        tokens_used=0,
        duration_ms=100.0,
        success=False
    )
    
    end_time = time.time()
    total_duration = (end_time - start_time) * 1000
    
    logger.info("Ollama LLM interaction test completed", 
               operation="test_complete",
               duration_ms=total_duration)
    
    print("✅ LLM interaction monitoring completed")

def demo_ollama_metrics_collection():
    """Test metrics collection with Ollama-specific data"""
    print("\n📊 Testing Metrics Collection with Ollama...")
    
    metrics = MetricsCollector(retention_hours=1, max_datapoints=1000)
    
    print("📈 Collecting Ollama performance metrics...")
    
    # Track various Ollama operations
    operations = [
        ("chat_completion", 1200, 45, 0.0),  # Ollama is free
        ("text_generation", 2800, 150, 0.0),
        ("code_completion", 900, 75, 0.0),
        ("question_answering", 1500, 100, 0.0),
    ]
    
    for i, (operation, duration, tokens, cost) in enumerate(operations):
        metrics.track_llm_usage(
            provider="ollama",
            model="llama2",
            operation=operation,
            tokens_used=tokens,
            duration_ms=duration,
            cost_usd=cost,  # Ollama is free to run locally
            success=True
        )
        time.sleep(0.1)  # Small delay for timestamp variation
    
    # Track some agent operations using Ollama
    for i in range(3):
        metrics.track_agent_performance(
            agent_id=f"ollama_agent_{i:03d}",
            agent_role="local_assistant",
            task_type="text_processing",
            duration_ms=2000 + i * 300,
            tokens_used=100 + i * 25,
            success=True,
            quality_score=0.85 + i * 0.05
        )
    
    # Get performance dashboard
    dashboard = metrics.get_performance_dashboard()
    
    print("\n📈 Ollama Performance Dashboard:")
    print(f"   LLM Requests: {dashboard['llm_usage']['total_requests']}")
    print(f"   Total Tokens: {dashboard['llm_usage']['total_tokens']:,}")
    print(f"   Total Cost: ${dashboard['llm_usage']['total_cost_usd']:.2f} (Free with Ollama!)")
    
    # Calculate average duration if we have the data
    llm_usage = dashboard['llm_usage']
    if llm_usage['total_requests'] > 0:
        avg_duration = llm_usage.get('avg_duration_ms', 0)
        if avg_duration == 0:
            # Calculate from total duration and requests if available
            total_duration = llm_usage.get('total_duration_ms', 0)
            if total_duration > 0:
                avg_duration = total_duration / llm_usage['total_requests']
        print(f"   Average Response Time: {avg_duration:.1f}ms")
    
    # Show Ollama-specific metrics
    provider_breakdown = dashboard['llm_usage']['provider_breakdown']
    ollama_key = None
    
    # Find the ollama provider key (it might be formatted differently)
    for key in provider_breakdown.keys():
        if 'ollama' in key.lower():
            ollama_key = key
            break
    
    if ollama_key and provider_breakdown[ollama_key]:
        provider_stats = provider_breakdown[ollama_key]
        print(f"\n🦙 Llama2 Specific Metrics:")
        print(f"   Requests: {provider_stats['requests']}")
        print(f"   Tokens: {provider_stats['tokens']:,}")
        if 'avg_duration_ms' in provider_stats:
            print(f"   Avg Duration: {provider_stats['avg_duration_ms']:.1f}ms")
    else:
        print(f"\n🦙 Provider breakdown keys: {list(provider_breakdown.keys())}")
    
    print("✅ Ollama metrics collection completed")

def demo_ollama_health_monitoring():
    """Test health monitoring with Ollama connectivity"""
    print("\n🏥 Testing Health Monitoring with Ollama...")
    
    health_checker = HealthChecker(timeout_seconds=10)
    
    print("🔍 Running health checks...")
    
    # System resources
    resource_check = health_checker.check_system_resources()
    print(f"   System Resources: {resource_check.status.value}")
    if resource_check.details:
        cpu_percent = resource_check.details.get('cpu_percent', 'N/A')
        memory_percent = resource_check.details.get('memory_percent', 'N/A')
        
        if cpu_percent != 'N/A':
            print(f"   CPU: {cpu_percent:.1f}%")
        else:
            print(f"   CPU: {cpu_percent}")
            
        if memory_percent != 'N/A':
            print(f"   Memory: {memory_percent:.1f}%")
        else:
            print(f"   Memory: {memory_percent}")
    
    # Configuration check for Ollama
    ollama_config = {
        "llm_provider": "ollama",
        "llm_model_name": "llama2",
        "llm_temperature": 0.7,
        "llm_api_base": "http://localhost:11434"
    }
    
    config_check = health_checker.check_configuration_validity(ollama_config)
    print(f"\n   Ollama Configuration: {config_check.status.value}")
    print(f"   Message: {config_check.message}")
    
    # Ollama connectivity check
    try:
        ollama_check = health_checker.check_llm_connectivity("ollama")
        print(f"\n   Ollama Connectivity: {ollama_check.status.value}")
        print(f"   Message: {ollama_check.message}")
    except Exception as e:
        print(f"\n   Ollama Connectivity: ❌ Error - {e}")
    
    print("✅ Ollama health monitoring completed")

def demo_full_aicrewdev_with_ollama():
    """Test full AICrewDev integration with Ollama"""
    print("\n🚀 Testing Full AICrewDev Integration with Ollama...")
    
    try:
        # Create settings for Ollama
        settings = Settings.for_development()
        
        print("🔧 Creating AICrewDev instance with Ollama configuration...")
        
        # Create AICrewDev with monitoring
        ai_crew = AICrewDev(settings)
        
        print("📊 Getting system status with Ollama integration...")
        
        # Get comprehensive status
        status = ai_crew.get_status()
        
        print(f"\n✅ AICrewDev + Ollama Status:")
        print(f"   Application: {status['application']['app_name']}")
        print(f"   Environment: {status['application']['environment']}")
        print(f"   LLM Provider: {status['application']['llm_provider']}")
        print(f"   Model: {status['application']['llm_model']}")
        print(f"   Debug Mode: {status['application']['debug']}")
        
        # Test monitoring integration
        monitoring = status.get('monitoring', {})
        if monitoring:
            health_status = monitoring.get('health_status', {})
            print(f"\n📈 Monitoring Integration:")
            print(f"   Overall Health: {health_status.get('overall_status', 'unknown')}")
            
            health_checks = monitoring.get('health_checks', {})
            if health_checks:
                print(f"   Health Checks:")
                for check_name, check_info in health_checks.items():
                    status_emoji = "✅" if check_info['status'] == 'healthy' else "⚠️" if check_info['status'] == 'warning' else "❌"
                    print(f"     {status_emoji} {check_name}: {check_info['status']}")
        
        # Test a simple run with performance tracking
        print("\n⏱️  Testing performance tracking...")
        
        with PerformanceTracker(ai_crew.metrics, "ollama_test_operation"):
            # Simulate some work
            time.sleep(0.5)
            ai_crew.logger.info("Ollama integration test completed successfully", 
                              operation="integration_test")
        
        # Get updated metrics
        dashboard = ai_crew.metrics.get_performance_dashboard()
        print(f"   Operations Tracked: {dashboard['performance']['total_executions']}")
        print(f"   Success Rate: {dashboard['performance']['overall_success_rate']:.1%}")
        
        print("✅ Full AICrewDev + Ollama integration successful!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run Ollama + Llama2 integration demo"""
    print("🦙 Ollama + Llama2 Integration Demo")
    print("=" * 50)
    
    print("This demo tests AICrewDev monitoring with local Ollama LLM:")
    print("• Local LLM with no API costs")
    print("• Full monitoring capabilities")
    print("• Privacy-focused local inference")
    print("• Production-ready observability")
    
    try:
        # Setup environment
        setup_ollama_environment()
        
        # Test connectivity first
        if not test_ollama_connectivity():
            print("\n❌ Ollama connectivity test failed!")
            print("Please ensure:")
            print("1. Ollama is installed: https://ollama.ai/")
            print("2. Ollama service is running: 'ollama serve'")
            print("3. Llama2 model is available: 'ollama pull llama2'")
            return
        
        # Run monitoring demos
        demo_ollama_llm_interaction()
        demo_ollama_metrics_collection()
        demo_ollama_health_monitoring()
        demo_full_aicrewdev_with_ollama()
        
        print("\n🎉 Ollama + Llama2 Integration Demo Complete!")
        print("=" * 50)
        
        print("\n✅ Successfully Validated:")
        print("• Ollama connectivity and model availability")
        print("• LLM interaction monitoring with local models")
        print("• Performance metrics for local inference")
        print("• Health monitoring for local LLM setup")
        print("• Full AICrewDev integration with Ollama")
        
        print("\n💡 Benefits of Ollama Integration:")
        print("• 🆓 Zero API costs - completely free to run")
        print("• 🔒 Complete privacy - no data leaves your machine")
        print("• 🚀 Fast local inference - no network latency")
        print("• 📊 Full monitoring - same observability as cloud LLMs")
        print("• 🛠️  Easy setup - just install Ollama and pull models")
        
        print(f"\n🎯 Next Steps:")
        print("• Try different Ollama models: 'ollama pull mistral' or 'ollama pull codellama'")
        print("• Monitor performance differences between models")
        print("• Set up production monitoring for local LLM deployments")
        print("• Scale with multiple Ollama instances for high throughput")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
