#!/usr/bin/env python3
"""
Enhanced AICrewDev Architecture Demo

This example demonstrates the complete enhanced architecture including:
- Centralized settings management
- Service layer abstraction
- Enhanced crew management
- Data models and specifications
- Multiple workflow types
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import AICrewDev
from src.core.settings import Settings
from src.models.agent_models import AgentSpecification, AgentRole, DeveloperSpecialization
from src.models.task_models import TaskSpecification, TaskType, TaskPriority
from src.services.agent_service import AgentService
from src.services.task_service import TaskService

def demonstrate_enhanced_architecture():
    """Demonstrate the complete enhanced architecture."""
    
    print("🚀 AICrewDev Enhanced Architecture Demonstration")
    print("=" * 60)
    
    # === 1. Settings and Configuration ===
    print("\n📋 1. Enhanced Settings and Configuration")
    
    # Create development-optimized settings
    dev_settings = Settings.for_development()
    print(f"✅ Development Settings:")
    print(f"   Environment: {dev_settings.environment}")
    print(f"   Debug Mode: {dev_settings.debug}")
    print(f"   LLM Provider: {dev_settings.llm_config.provider}")
    print(f"   LLM Model: {dev_settings.llm_config.model_name}")
    print(f"   Crew Verbose: {dev_settings.crew_verbose}")
    print(f"   Max Agents: {dev_settings.max_agents}")
    
    # === 2. Service Layer Demonstration ===
    print("\n🔧 2. Service Layer Operations")
    
    # Agent Service
    agent_service = AgentService(dev_settings.llm_config)
    
    # Create custom agent specifications
    custom_specs = [
        AgentSpecification.for_tech_lead(temperature=0.1),
        AgentSpecification.for_developer(
            DeveloperSpecialization.FRONTEND, 
            temperature=0.3,
            tools=["react", "typescript", "css"]
        ),
        AgentSpecification.for_developer(
            DeveloperSpecialization.BACKEND,
            temperature=0.3,
            tools=["python", "fastapi", "postgresql"]
        ),
        AgentSpecification.for_code_reviewer(temperature=0.2)
    ]
    
    # Create agents from specifications
    created_agents = []
    for spec in custom_specs:
        agent = agent_service.create_agent_from_spec(spec)
        created_agents.append(agent)
        print(f"✅ Created Agent: {spec.get_display_name()}")
    
    # Show team summary
    team_summary = agent_service.get_team_summary()
    print(f"\n📊 Team Summary:")
    print(f"   Total Agents: {team_summary['total_agents']}")
    print(f"   Role Distribution: {team_summary['role_distribution']}")
    print(f"   Specializations: {team_summary['developer_specializations']}")
    
    # Task Service
    task_service = TaskService()
    
    # Create custom task specifications
    custom_task_specs = [
        TaskSpecification.for_design_task(
            title="E-commerce Platform Architecture",
            priority=TaskPriority.CRITICAL
        ),
        TaskSpecification.for_development_task(
            "user authentication system",
            priority=TaskPriority.HIGH,
            estimated_duration=300
        ),
        TaskSpecification.for_testing_task(
            "authentication flows",
            priority=TaskPriority.HIGH
        ),
        TaskSpecification.for_review_task(
            "authentication implementation",
            priority=TaskPriority.MEDIUM
        )
    ]
    
    # Create tasks from specifications
    created_tasks = []
    for i, spec in enumerate(custom_task_specs):
        agent = created_agents[i % len(created_agents)]
        task = task_service.create_task_from_spec(spec, agent)
        created_tasks.append(task)
        print(f"✅ Created Task: {spec.title}")
    
    # Show workflow summary
    workflow_summary = task_service.get_workflow_summary()
    print(f"\n📊 Workflow Summary:")
    print(f"   Total Tasks: {workflow_summary['total_tasks']}")
    print(f"   Task Types: {workflow_summary['task_type_distribution']}")
    print(f"   Priorities: {workflow_summary['priority_distribution']}")
    
    # === 3. Enhanced Main Application ===
    print("\n🤖 3. Enhanced Main Application")
    
    # Create AICrewDev with custom settings
    ai_crew = AICrewDev(dev_settings)
    
    # Show comprehensive status
    status = ai_crew.get_status()
    print(f"✅ AICrewDev Status:")
    print(f"   Application: {status['application']['app_name']} v{status['application']['version']}")
    print(f"   Environment: {status['application']['environment']}")
    print(f"   Debug Mode: {status['application']['debug']}")
    
    # === 4. Multiple Workflow Types ===
    print("\n⚙️ 4. Multiple Workflow Demonstrations")
    
    # Web Development Workflow
    print(f"\n🌐 Web Development Workflow:")
    try:
        web_result = ai_crew.run(project_type="web", use_crew_manager=True)
        print(f"✅ Web development workflow completed")
        print(f"📄 Result Summary: {str(web_result)[:150]}...")
    except Exception as e:
        print(f"❌ Web workflow failed: {e}")
    
    # Analysis Workflow
    print(f"\n🔍 Code Analysis Workflow:")
    try:
        analysis_result = ai_crew.run_analysis("e-commerce codebase")
        print(f"✅ Analysis workflow completed")
        print(f"📄 Analysis Summary: {str(analysis_result)[:150]}...")
    except Exception as e:
        print(f"❌ Analysis workflow failed: {e}")
    
    # === 5. Workflow Templates ===
    print("\n📋 5. Available Workflow Templates")
    
    available_workflows = task_service.get_available_workflows()
    print(f"✅ Available Templates:")
    for workflow in available_workflows:
        template = task_service.get_workflow_template(workflow)
        if template:
            print(f"   • {workflow}: {len(template)} tasks")
        else:
            print(f"   • {workflow}: template not found")
    
    # === 6. Final Status and Metrics ===
    print("\n📈 6. Final Status and Metrics")
    
    final_status = ai_crew.get_status()
    execution_history = ai_crew.crew_manager.get_execution_history()
    
    print(f"✅ Final System Status:")
    print(f"   Total Executions: {len(execution_history)}")
    print(f"   Agents Created: {final_status['agent_service']['total_agents']}")
    print(f"   Tasks Created: {final_status['task_service']['total_tasks']}")
    
    if execution_history:
        successful_executions = sum(1 for ex in execution_history if ex.get('success', False))
        print(f"   Success Rate: {successful_executions}/{len(execution_history)} ({successful_executions/len(execution_history)*100:.1f}%)")
    
    # === 7. Performance Features ===
    print("\n⚡ 7. Performance and Configuration Features")
    
    print(f"✅ Configuration Features:")
    print(f"   Environment Variables: Automatic loading with AICREWDEV_ prefix")
    print(f"   Role Optimization: Temperature tuning per agent role")
    print(f"   Provider Fallbacks: Graceful degradation when providers unavailable")
    print(f"   Memory Management: Configurable agent memory and delegation")
    print(f"   Execution Tracking: Comprehensive execution history and metrics")
    
    print(f"\n✅ Architecture Benefits:")
    print(f"   Service Layer: Separated business logic from CrewAI framework")
    print(f"   Data Models: Type-safe specifications with validation")
    print(f"   Workflow Templates: Reusable task configurations")
    print(f"   Settings Management: Centralized configuration with environment support")
    print(f"   Enhanced Error Handling: Graceful failure management")
    
    print("\n🎉 Enhanced Architecture Demonstration Complete!")
    print("=" * 60)

def demonstrate_production_settings():
    """Demonstrate production-optimized settings."""
    
    print("\n🏭 Production Settings Demo")
    print("-" * 40)
    
    # Create production settings
    prod_settings = Settings.for_production()
    
    print(f"✅ Production Configuration:")
    print(f"   Environment: {prod_settings.environment}")
    print(f"   Debug Mode: {prod_settings.debug}")
    print(f"   Verbose Crew: {prod_settings.crew_verbose}")
    print(f"   Max Iterations: {prod_settings.max_iterations}")
    print(f"   Timeout: {prod_settings.timeout_seconds}s")
    print(f"   Code Execution: {prod_settings.enable_code_execution}")
    
    # Create AICrewDev with production settings
    prod_ai_crew = AICrewDev(prod_settings)
    prod_status = prod_ai_crew.get_status()
    
    print(f"\n📊 Production AICrewDev Status:")
    print(f"   App Version: {prod_status['application']['version']}")
    print(f"   Environment: {prod_status['application']['environment']}")
    print(f"   Max Agents: {prod_status['application']['max_agents']}")

if __name__ == "__main__":
    # Set up environment for demo
    os.environ.setdefault("LLM_PROVIDER", "openai")
    os.environ.setdefault("LLM_MODEL_NAME", "gpt-4o-mini")
    os.environ.setdefault("LLM_TEMPERATURE", "0.7")
    os.environ.setdefault("AICREWDEV_CREW_VERBOSE", "true")
    
    try:
        # Run main demonstration
        demonstrate_enhanced_architecture()
        
        # Run production demo
        demonstrate_production_settings()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Set your API keys: export OPENAI_API_KEY=your_key")
    print(f"   2. Customize settings: AICREWDEV_* environment variables")
    print(f"   3. Create custom workflows: Use TaskService.get_workflow_template()")
    print(f"   4. Scale your team: Use AgentService.create_development_team()")
    print(f"   5. Monitor performance: Check execution history and metrics")
