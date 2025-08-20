#!/usr/bin/env python3
"""
Enhanced Real-time Monitoring Demo

This demo showcases the new real-time progress tracking capabilities,
providing live updates during LLM operations and showing progress bars.
"""

import os
import sys
import time
import threading
import asyncio
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import AICrewDev
from src.core.settings import Settings
from src.monitoring.real_time_monitor import (
    get_global_monitor, get_global_display_manager, 
    OperationStatus, track_operation
)

def setup_ollama_environment():
    """Configure environment for Ollama"""
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL_NAME"] = "llama2"
    os.environ["LLM_TEMPERATURE"] = "0.7"
    os.environ["LLM_API_BASE"] = "http://localhost:11434"
    os.environ["AICREWDEV_DEBUG"] = "true"

def simulate_llm_operation_with_progress():
    """Simulate an LLM operation with real-time progress updates"""
    print("\n🤖 Simulating LLM Operation with Real-time Progress")
    print("-" * 50)
    
    monitor = get_global_monitor()
    operation_id = f"llm_demo_{uuid.uuid4().hex[:8]}"
    
    # Start operation
    operation = monitor.start_operation(
        operation_id=operation_id,
        operation_type="llm_generation",
        estimated_duration=10.0,
        metadata={"model": "llama2", "prompt_length": 50}
    )
    
    try:
        # Phase 1: Initializing
        monitor.update_operation(
            operation_id,
            status=OperationStatus.INITIALIZING,
            progress_percent=5.0,
            current_step="Connecting to Ollama..."
        )
        time.sleep(1.0)
        
        # Phase 2: Processing prompt
        monitor.update_operation(
            operation_id,
            status=OperationStatus.PROCESSING,
            progress_percent=20.0,
            current_step="Processing prompt..."
        )
        time.sleep(1.5)
        
        # Phase 3: Generating tokens (simulate streaming)
        for i in range(8):
            progress = 20 + (i * 8)  # 20% to 84%
            tokens_so_far = i * 10
            
            monitor.update_operation(
                operation_id,
                status=OperationStatus.STREAMING,
                progress_percent=progress,
                current_step=f"Generating response... ({tokens_so_far} tokens)",
                tokens_processed=tokens_so_far
            )
            time.sleep(0.8)  # Simulate token generation time
        
        # Phase 4: Finalizing
        monitor.update_operation(
            operation_id,
            status=OperationStatus.FINALIZING,
            progress_percent=95.0,
            current_step="Finalizing response..."
        )
        time.sleep(0.5)
        
        # Complete
        monitor.complete_operation(
            operation_id,
            success=True,
            final_metadata={
                "total_tokens": 80,
                "completion_reason": "finished",
                "model_performance": "excellent"
            }
        )
        
        print(f"\n✅ Operation {operation_id} completed successfully!")
        
    except Exception as e:
        monitor.complete_operation(operation_id, success=False,
                                 final_metadata={"error": str(e)})
        print(f"\n❌ Operation {operation_id} failed: {e}")

def simulate_real_ollama_with_progress():
    """Simulate a real Ollama request with progress tracking"""
    print("\n🦙 Real Ollama Request with Progress Tracking")
    print("-" * 50)
    
    monitor = get_global_monitor()
    operation_id = f"real_ollama_{uuid.uuid4().hex[:8]}"
    
    try:
        # Start operation
        operation = monitor.start_operation(
            operation_id=operation_id,
            operation_type="llm_chat",
            estimated_duration=12.0,
            metadata={"provider": "ollama", "model": "llama2"}
        )
        
        # Phase 1: Initialize
        monitor.update_operation(
            operation_id,
            status=OperationStatus.INITIALIZING,
            progress_percent=10.0,
            current_step="Preparing request to Ollama..."
        )
        time.sleep(0.5)
        
        # Phase 2: Make real request
        monitor.update_operation(
            operation_id,
            status=OperationStatus.PROCESSING,
            progress_percent=25.0,
            current_step="Sending request to Ollama..."
        )
        
        import requests
        start_time = time.time()
        
        # Simulate progress during request
        def update_progress_during_request():
            """Update progress while waiting for response"""
            elapsed = 0
            while elapsed < 15:  # Max 15 seconds
                elapsed = time.time() - start_time
                progress = min(90.0, 25 + (elapsed * 5))  # Gradual progress
                
                monitor.update_operation(
                    operation_id,
                    status=OperationStatus.STREAMING,
                    progress_percent=progress,
                    current_step=f"Waiting for Ollama response... ({elapsed:.1f}s)"
                )
                time.sleep(0.3)
        
        # Start progress updater in background
        progress_thread = threading.Thread(target=update_progress_during_request, daemon=True)
        progress_thread.start()
        
        # Make actual request
        response = requests.post("http://localhost:11434/api/generate", 
                               json={
                                   "model": "llama2",
                                   "prompt": "Explain quantum computing in simple terms.",
                                   "stream": False
                               },
                               timeout=20)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            tokens_used = len(response_text.split())
            
            monitor.update_operation(
                operation_id,
                status=OperationStatus.FINALIZING,
                progress_percent=95.0,
                current_step="Processing response...",
                tokens_processed=tokens_used
            )
            time.sleep(0.5)
            
            monitor.complete_operation(
                operation_id,
                success=True,
                final_metadata={
                    "response_length": len(response_text),
                    "tokens_generated": tokens_used,
                    "duration_seconds": duration,
                    "status_code": response.status_code
                }
            )
            
            print(f"\n✅ Real Ollama request completed!")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Tokens: {tokens_used}")
            print(f"   Response preview: {response_text[:100]}...")
            
        else:
            raise Exception(f"Ollama request failed: {response.status_code}")
            
    except Exception as e:
        monitor.complete_operation(operation_id, success=False,
                                 final_metadata={"error": str(e)})
        print(f"\n❌ Real Ollama request failed: {e}")

def simulate_multiple_concurrent_operations():
    """Simulate multiple operations running concurrently"""
    print("\n⚡ Multiple Concurrent Operations")
    print("-" * 50)
    
    def worker_operation(worker_id: int, duration: float):
        """Worker operation that runs in parallel"""
        monitor = get_global_monitor()
        operation_id = f"worker_{worker_id}_{uuid.uuid4().hex[:6]}"
        
        operation = monitor.start_operation(
            operation_id=operation_id,
            operation_type="agent_task",
            estimated_duration=duration,
            metadata={"worker_id": worker_id}
        )
        
        try:
            steps = ["Analyzing", "Processing", "Generating", "Reviewing", "Finalizing"]
            for i, step in enumerate(steps):
                progress = (i + 1) * 20
                monitor.update_operation(
                    operation_id,
                    status=OperationStatus.PROCESSING,
                    progress_percent=progress,
                    current_step=f"Worker {worker_id}: {step}..."
                )
                time.sleep(duration / len(steps))
            
            monitor.complete_operation(operation_id, success=True)
            
        except Exception as e:
            monitor.complete_operation(operation_id, success=False,
                                     final_metadata={"error": str(e)})
    
    # Start multiple workers
    threads = []
    for i in range(3):
        duration = 3.0 + i  # Different durations
        thread = threading.Thread(target=worker_operation, args=(i+1, duration))
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Stagger starts
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    print(f"\n✅ All concurrent operations completed!")

def show_monitoring_dashboard():
    """Show the current monitoring dashboard"""
    print("\n📊 Live Monitoring Dashboard")
    print("-" * 50)
    
    monitor = get_global_monitor()
    display_manager = get_global_display_manager()
    
    # Show active operations
    active_ops = monitor.get_active_operations()
    
    if active_ops:
        print(f"📈 Active Operations ({len(active_ops)}):")
        for op_id, operation in active_ops.items():
            print(f"   🔹 {op_id}")
            print(f"      Status: {operation.status.value}")
            print(f"      Progress: {operation.progress_percent:.1f}%")
            print(f"      Step: {operation.current_step}")
            print(f"      Elapsed: {operation.elapsed_seconds():.1f}s")
            
            remaining = operation.estimated_remaining_seconds()
            if remaining is not None:
                print(f"      ETA: {remaining:.1f}s")
            print()
    else:
        print("   No active operations")
    
    # Show JSON status
    print("\n📋 JSON Status:")
    json_status = display_manager.get_progress_json()
    print(json_status)

def main():
    """Run the enhanced real-time monitoring demo"""
    print("🚀 Enhanced Real-time Monitoring Demo")
    print("=" * 60)
    
    print("\nThis demo showcases:")
    print("• Real-time progress tracking for LLM operations")
    print("• Live progress bars with ETA estimates")
    print("• Token/second rate monitoring")
    print("• Concurrent operation tracking")
    print("• Historical performance learning")
    
    # Setup environment
    setup_ollama_environment()
    
    # Initialize monitoring
    monitor = get_global_monitor()
    display_manager = get_global_display_manager()
    
    print(f"\n✅ Real-time monitoring initialized")
    print(f"   Update interval: {monitor.update_interval}s")
    print(f"   Console display: enabled")
    
    try:
        # Demo 1: Simulated operation with progress
        simulate_llm_operation_with_progress()
        time.sleep(1)
        
        # Demo 2: Real Ollama request with progress
        simulate_real_ollama_with_progress()
        time.sleep(1)
        
        # Demo 3: Multiple concurrent operations
        simulate_multiple_concurrent_operations()
        time.sleep(1)
        
        # Demo 4: Show dashboard
        show_monitoring_dashboard()
        
        print("\n🎉 Enhanced Real-time Monitoring Demo Complete!")
        print("=" * 60)
        
        print("\n✅ Key Features Demonstrated:")
        print("• ⏱️  Real-time progress bars with completion estimates")
        print("• 📊 Live token/second rate monitoring")
        print("• 🔄 Multi-phase operation tracking")
        print("• ⚡ Concurrent operation management")
        print("• 📈 Historical performance learning")
        print("• 🎯 Accurate ETA predictions")
        
        print("\n💡 Benefits:")
        print("• Users can see exactly what's happening")
        print("• Progress visibility reduces perceived wait time")
        print("• Performance metrics help optimize operations")
        print("• Concurrent tracking enables workflow monitoring")
        print("• Historical data improves future estimates")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        monitor.stop_monitoring()
        print("\n🔧 Monitoring stopped")

if __name__ == "__main__":
    main()
