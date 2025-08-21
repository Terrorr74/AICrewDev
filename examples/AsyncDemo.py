#!/usr/bin/env python3
"""
Simple Async Demo - Test that async imports and basic functionality work
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main():
    """Run async operations demo"""
    
    print("🚀 AICrewDev Async Operations Demo")
    print("=" * 50)
    
    try:
        # Test async imports
        print("🔧 Testing Async Imports...")
        
        from src.agents.async_agents import AsyncAgentFactory, AsyncCrewManager
        
        print("✅ Async modules imported successfully")
        
        # Test async factory instantiation
        print("\n🎯 Testing Async Factory Instantiation...")
        
        async_factory = AsyncAgentFactory()
        print("✅ AsyncAgentFactory created successfully")
        
        # Test basic async operation
        print("\n⚡ Testing Basic Async Operation...")
        
        async def sample_async_task():
            await asyncio.sleep(0.1)  # Simulate async work
            return "Async task completed"
        
        start_time = asyncio.get_event_loop().time()
        result = await sample_async_task()
        end_time = asyncio.get_event_loop().time()
        
        print(f"✅ {result} in {(end_time - start_time):.3f} seconds")
        
        # Test concurrent operations
        print("\n🔀 Testing Concurrent Operations...")
        
        async def concurrent_task(task_id: int, delay: float):
            await asyncio.sleep(delay)
            return f"Task {task_id} completed"
        
        tasks = [
            concurrent_task(1, 0.1),
            concurrent_task(2, 0.05),
            concurrent_task(3, 0.08)
        ]
        
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        print(f"✅ Completed {len(results)} concurrent tasks in {(end_time - start_time):.3f} seconds")
        for result in results:
            print(f"   - {result}")
        
        print("\n✨ Async demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
