#!/usr/bin/env python3
"""
Enhanced Async Agents Demo

This demo showcases the new asynchronous agent capabilities including:
- Concurrent agent creation
- Async team building
- Parallel task execution
- Real-time progress monitoring
"""

import asyncio
import time
from typing import List, Dict, Any

from src.config.llm_config import LLMConfig, LLMProvider
from src.agents.async_agents import (
    AsyncAgentFactory, 
    AsyncCrewManager,
    AsyncOperationStatus,
    run_development_workflow_async
)
from src.monitoring.real_time_monitor import RealTimeMonitor


async def demo_concurrent_agent_creation():
    """Demonstrate concurrent agent creation"""
    print("\n🚀 Demo: Concurrent Agent Creation")
    print("=" * 50)
    
    # Initialize LLM config
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model_name="llama2",
        temperature=0.7,
        verbose=True
    )
    
    # Create async factory
    factory = AsyncAgentFactory(max_workers=4)
    
    try:
        # Define multiple agent configurations
        agent_configs = [
            {
                "role": "frontend_developer",
                "goal": "Create responsive and user-friendly web interfaces",
                "backstory": "Frontend specialist with React and TypeScript expertise",
                "allow_code_execution": True
            },
            {
                "role": "backend_developer", 
                "goal": "Build robust and scalable server-side applications",
                "backstory": "Backend expert with Python and API development skills",
                "allow_code_execution": True
            },
            {
                "role": "devops_engineer",
                "goal": "Manage deployment and infrastructure automation",
                "backstory": "DevOps specialist with Docker and cloud platform experience",
                "allow_code_execution": True
            },
            {
                "role": "qa_tester",
                "goal": "Ensure software quality through comprehensive testing",
                "backstory": "Quality assurance expert with automated testing skills",
                "allow_code_execution": False
            }
        ]
        
        print(f"Creating {len(agent_configs)} agents concurrently...")
        start_time = time.time()
        
        # Create agents concurrently
        results = await factory.create_agents_batch_async(agent_configs, config)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analyze results
        successful_agents = [r for r in results if r.status == AsyncOperationStatus.COMPLETED]
        failed_agents = [r for r in results if r.status == AsyncOperationStatus.FAILED]
        
        print(f"\n✅ Agent Creation Results:")
        print(f"   • Successfully created: {len(successful_agents)} agents")
        print(f"   • Failed: {len(failed_agents)} agents")
        print(f"   • Total time: {duration:.2f} seconds")
        print(f"   • Average time per agent: {duration/len(agent_configs):.2f} seconds")
        
        if failed_agents:
            print(f"\n❌ Failed agents:")
            for result in failed_agents:
                role = "Unknown"
                if result.metadata:
                    role = result.metadata.get('role', 'Unknown')
                print(f"   • {role}: {result.error}")
        
        return [r.result for r in successful_agents]
        
    finally:
        await factory.shutdown()


async def demo_async_team_creation():
    """Demonstrate async development team creation"""
    print("\n🏗️  Demo: Async Development Team Creation")
    print("=" * 50)
    
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model_name="llama2",
        temperature=0.7,
        verbose=True
    )
    
    factory = AsyncAgentFactory(max_workers=3)
    
    try:
        # Test different team sizes
        team_sizes = ["minimal", "standard", "large"]
        
        for team_size in team_sizes:
            print(f"\n📋 Creating {team_size} team...")
            start_time = time.time()
            
            result = await factory.create_development_team_async(
                config=config,
                project_type="web_app",
                team_size=team_size
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.status == AsyncOperationStatus.COMPLETED:
                agents = result.result
                print(f"   ✅ Created {len(agents)} agents in {duration:.2f}s")
                print(f"   📊 Team composition:")
                for i, agent in enumerate(agents, 1):
                    print(f"      {i}. {agent.role}")
            else:
                print(f"   ❌ Failed: {result.error}")
    
    finally:
        await factory.shutdown()


async def demo_parallel_task_execution():
    """Demonstrate parallel task execution"""
    print("\n⚡ Demo: Parallel Task Execution")
    print("=" * 50)
    
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model_name="llama2",
        temperature=0.7,
        verbose=True
    )
    
    factory = AsyncAgentFactory(max_workers=4)
    
    try:
        # Create a development team
        team_result = await factory.create_development_team_async(
            config=config,
            project_type="mobile_app",
            team_size="standard"
        )
        
        if team_result.status != AsyncOperationStatus.COMPLETED:
            print(f"❌ Failed to create team: {team_result.error}")
            return
        
        agents = team_result.result
        print(f"✅ Created team with {len(agents)} agents")
        
        # Create tasks for parallel execution
        from crewai import Task
        
        tasks = [
            Task(
                description="Design the mobile app architecture and technology stack",
                agent=agents[0],
                expected_output="Architecture document with technology recommendations"
            ),
            Task(
                description="Create user interface mockups and user experience design",
                agent=agents[1] if len(agents) > 1 else agents[0],
                expected_output="UI/UX design files and user flow documentation"
            ),
            Task(
                description="Plan the development timeline and milestones",
                agent=agents[2] if len(agents) > 2 else agents[0],
                expected_output="Project timeline with development phases"
            )
        ]
        
        print(f"\n🏃‍♂️ Executing {len(tasks)} tasks in parallel...")
        start_time = time.time()
        
        # Execute tasks in parallel
        execution_result = await factory.execute_tasks_async(
            tasks=tasks,
            agents=agents,
            execution_mode="parallel"
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if execution_result.status == AsyncOperationStatus.COMPLETED:
            results = execution_result.result
            print(f"✅ All tasks completed in {duration:.2f} seconds")
            print(f"📋 Task results:")
            for i, result in enumerate(results, 1):
                print(f"   Task {i}: {'✅ Success' if result else '❌ Failed'}")
        else:
            print(f"❌ Task execution failed: {execution_result.error}")
    
    finally:
        await factory.shutdown()


async def demo_operation_monitoring():
    """Demonstrate real-time operation monitoring"""
    print("\n📊 Demo: Real-time Operation Monitoring")
    print("=" * 50)
    
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model_name="llama2",
        temperature=0.7,
        verbose=True
    )
    
    factory = AsyncAgentFactory(max_workers=2)
    
    try:
        # Start a long-running operation
        print("🚀 Starting development team creation...")
        
        operation_task = asyncio.create_task(
            factory.create_development_team_async(
                config=config,
                project_type="ai_platform",
                team_size="large"
            )
        )
        
        # Monitor the operation
        print("👀 Monitoring operation progress...")
        
        monitoring_active = True
        start_time = time.time()
        
        async def monitor_progress():
            while monitoring_active:
                active_ops = factory.get_active_operations()
                completed_ops = factory.get_completed_operations()
                
                print(f"\r📈 Active: {len(active_ops)}, Completed: {len(completed_ops)}, "
                      f"Time: {time.time() - start_time:.1f}s", end="", flush=True)
                
                await asyncio.sleep(0.5)
        
        # Start monitoring
        monitor_task = asyncio.create_task(monitor_progress())
        
        # Wait for operation to complete
        result = await operation_task
        monitoring_active = False
        
        # Stop monitoring
        monitor_task.cancel()
        
        print(f"\n\n✅ Operation completed!")
        print(f"   Status: {result.status}")
        print(f"   Duration: {result.duration:.2f}s" if result.duration else "   Duration: N/A")
        
        if result.status == AsyncOperationStatus.COMPLETED:
            agents = result.result
            print(f"   Created {len(agents)} agents successfully")
        
    finally:
        await factory.shutdown()


async def demo_full_development_workflow():
    """Demonstrate a complete async development workflow"""
    print("\n🎯 Demo: Complete Async Development Workflow")
    print("=" * 50)
    
    config = LLMConfig(
        provider=LLMProvider.OLLAMA,
        model_name="llama2",
        temperature=0.7,
        verbose=True
    )
    
    print("🚀 Starting complete development workflow...")
    start_time = time.time()
    
    # Custom tasks for the workflow
    custom_tasks = [
        "Analyze requirements and create technical specifications",
        "Design system architecture and select technology stack",
        "Implement core application features and functionality",
        "Conduct code review and ensure quality standards",
        "Create deployment strategy and documentation"
    ]
    
    try:
        result = await run_development_workflow_async(
            project_type="e_commerce_platform",
            llm_config=config,
            team_size="standard",
            custom_tasks=custom_tasks
        )
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        print(f"\n🎉 Workflow Results:")
        print(f"   Status: {result.status}")
        print(f"   Total Duration: {total_duration:.2f} seconds")
        
        if result.status == AsyncOperationStatus.COMPLETED:
            workflow_data = result.result
            print(f"   ✅ Successfully completed development workflow")
            print(f"   📊 Workflow Details:")
            print(f"      • Team Size: {workflow_data['agents_count']} agents")
            print(f"      • Tasks Executed: {workflow_data['tasks_count']}")
            print(f"      • Project Type: {workflow_data['project_type']}")
            print(f"   🎯 Final Result: {workflow_data['crew_result']}")
        else:
            print(f"   ❌ Workflow failed: {result.error}")
    
    except Exception as e:
        print(f"❌ Workflow error: {e}")


async def main():
    """Main demo function"""
    print("🤖 AICrewDev - Async Agents Demo")
    print("=" * 60)
    print("This demo showcases enhanced asynchronous capabilities:")
    print("• Concurrent agent creation for faster team building")
    print("• Parallel task execution for improved performance") 
    print("• Real-time operation monitoring and progress tracking")
    print("• Complete async development workflows")
    
    try:
        # Run all demos
        await demo_concurrent_agent_creation()
        await demo_async_team_creation()
        await demo_parallel_task_execution()
        await demo_operation_monitoring()
        await demo_full_development_workflow()
        
        print(f"\n🎉 All async demos completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async demo
    asyncio.run(main())
