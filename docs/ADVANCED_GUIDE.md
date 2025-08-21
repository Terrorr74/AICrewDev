# Advanced AICrewDev Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Core Components](#core-components)
5. [Async Agents](#async-agents)
6. [Configuration Validation](#configuration-validation)
7. [Docker Integration](#docker-integration)
8. [Monitoring & Observability](#monitoring--observability)
9. [Examples & Tutorials](#examples--tutorials)
10. [API Reference](#api-reference)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

## Overview

AICrewDev is a sophisticated AI-powered development team simulator built on the CrewAI framework. It provides:

- **Multi-Agent Development Teams**: Create specialized AI agents for different development roles
- **Asynchronous Operations**: Concurrent agent creation and task execution for improved performance
- **Multiple LLM Providers**: Support for OpenAI, Anthropic, Ollama, and Groq
- **Docker Integration**: Safe code execution in containerized environments
- **Real-time Monitoring**: Track progress and performance metrics
- **Configuration Validation**: Comprehensive validation for production-ready deployments

### Key Features

✅ **Concurrent Agent Creation** - Create multiple agents simultaneously  
✅ **Parallel Task Execution** - Execute development tasks concurrently  
✅ **Real-time Progress Tracking** - Monitor operations as they happen  
✅ **Multi-Provider LLM Support** - Choose the best LLM for each role  
✅ **Docker Safe Execution** - Secure code execution environment  
✅ **Comprehensive Validation** - Prevent configuration errors  
✅ **Production Ready** - Built for scalable deployments  

## Installation

### Prerequisites

- Python 3.11 or higher
- Docker Desktop (for code execution)
- Git

### Basic Installation

```bash
# Clone the repository
git clone <repository-url>
cd AICrewDev

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Docker Installation

AICrewDev requires Docker for safe code execution. Install Docker Desktop:

**macOS:**
```bash
# Using Homebrew
brew install --cask docker

# Or download from: https://www.docker.com/products/docker-desktop
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose
```

**Windows:**
Download Docker Desktop from https://www.docker.com/products/docker-desktop

### Verification

```bash
# Verify Python environment
python --version  # Should be 3.11+

# Verify Docker installation
docker --version
docker run hello-world

# Test AICrewDev installation
python -m src.main --help
```

## Configuration

### LLM Configuration

AICrewDev supports multiple LLM providers. Configure them using the `LLMConfig` class:

```python
from src.config.llm_config import LLMConfig, LLMProvider

# OpenAI Configuration
openai_config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model_name="gpt-4o-mini",
    temperature=0.7,
    api_key="your-api-key"  # Or set OPENAI_API_KEY env var
)

# Ollama Configuration (Local)
ollama_config = LLMConfig(
    provider=LLMProvider.OLLAMA,
    model_name="llama2",
    base_url="http://localhost:11434",
    temperature=0.7
)

# Anthropic Configuration
anthropic_config = LLMConfig(
    provider=LLMProvider.ANTHROPIC,
    model_name="claude-3-haiku-20240307",
    api_key="your-api-key",  # Or set ANTHROPIC_API_KEY env var
    temperature=0.7
)
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key

# Groq
GROQ_API_KEY=your_groq_api_key

# Ollama (if not running locally)
OLLAMA_BASE_URL=http://your-ollama-server:11434

# Docker Settings
DOCKER_TIMEOUT=300
DOCKER_MEMORY_LIMIT=2g

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aicrewdev.log
```

### Agent Configuration

Configure agents using YAML files (recommended for production):

```yaml
# config/agents.yaml
agents:
  tech_lead:
    role: "Technical Lead"
    goal: "Provide technical leadership and architecture guidance"
    backstory: "Senior technical leader with 10+ years of experience"
    allow_delegation: true
    verbose: true
    temperature: 0.3  # Lower for more focused responses
    
  developer:
    role: "Full Stack Developer"
    goal: "Implement features and write high-quality code"
    backstory: "Experienced developer with full-stack capabilities"
    allow_code_execution: true
    verbose: true
    temperature: 0.5
    
  reviewer:
    role: "Code Reviewer"
    goal: "Review code quality and ensure best practices"
    backstory: "Quality-focused engineer with attention to detail"
    allow_code_execution: false
    verbose: true
    temperature: 0.2  # Very focused for reviews
```

## Core Components

### Agent Factory

The `AgentFactory` class creates specialized agents for different development roles:

```python
from src.agents.agent_factory import AgentFactory
from src.config.llm_config import LLMConfig, LLMProvider

# Initialize configuration
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model_name="gpt-4o-mini"
)

# Create specialized agents
tech_lead = AgentFactory.create_tech_lead(config)
developer = AgentFactory.create_developer(config)
reviewer = AgentFactory.create_code_reviewer(config)
manager = AgentFactory.create_project_manager(config)
```

### Crew Manager

The `CrewManager` orchestrates teams of agents:

```python
from src.core.crew_manager import CrewManager

# Initialize crew manager
crew_manager = CrewManager()

# Create and run a development team
result = crew_manager.create_development_crew(
    config=config,
    project_type="web_application",
    agents=[tech_lead, developer, reviewer]
)

# Execute the crew
output = crew_manager.run_crew(result)
```

### Task Factory

Create specialized development tasks:

```python
from src.tasks.task_factory import TaskFactory

# Create development tasks
tasks = TaskFactory.create_development_tasks(
    project_type="web_app",
    requirements=[
        "User authentication system",
        "RESTful API backend",
        "React frontend",
        "Database integration"
    ]
)
```

## Async Agents

AICrewDev provides powerful asynchronous capabilities for improved performance and scalability.

### Async Agent Factory

Create agents concurrently for faster team building:

```python
import asyncio
from src.agents.async_agents import AsyncAgentFactory

async def create_team():
    factory = AsyncAgentFactory(max_workers=4)
    
    try:
        # Define agent configurations
        agent_configs = [
            {
                "role": "frontend_developer",
                "goal": "Create responsive user interfaces",
                "backstory": "React/TypeScript specialist",
                "allow_code_execution": True
            },
            {
                "role": "backend_developer",
                "goal": "Build scalable APIs",
                "backstory": "Python/FastAPI expert",
                "allow_code_execution": True
            }
        ]
        
        # Create agents concurrently
        results = await factory.create_agents_batch_async(
            agent_configs, config
        )
        
        # Extract successful agents
        agents = [r.result for r in results if r.status == "completed"]
        return agents
        
    finally:
        await factory.shutdown()

# Run async function
agents = asyncio.run(create_team())
```

### Parallel Task Execution

Execute development tasks concurrently:

```python
async def execute_parallel_tasks():
    factory = AsyncAgentFactory()
    
    try:
        # Create team
        team_result = await factory.create_development_team_async(
            config=config,
            project_type="mobile_app",
            team_size="standard"
        )
        
        agents = team_result.result
        
        # Create tasks
        tasks = [
            Task(
                description="Design app architecture",
                agent=agents[0],
                expected_output="Architecture document"
            ),
            Task(
                description="Create UI mockups",
                agent=agents[1],
                expected_output="UI design files"
            )
        ]
        
        # Execute in parallel
        result = await factory.execute_tasks_async(
            tasks=tasks,
            agents=agents,
            execution_mode="parallel"
        )
        
        return result.result
        
    finally:
        await factory.shutdown()
```

### Operation Monitoring

Monitor long-running operations in real-time:

```python
async def monitor_operation():
    factory = AsyncAgentFactory()
    
    # Start operation
    operation_task = asyncio.create_task(
        factory.create_development_team_async(
            config=config,
            project_type="ai_platform",
            team_size="large"
        )
    )
    
    # Monitor progress
    while not operation_task.done():
        active_ops = factory.get_active_operations()
        print(f"Active operations: {len(active_ops)}")
        await asyncio.sleep(1)
    
    result = await operation_task
    print(f"Operation completed: {result.status}")
```

## Configuration Validation

AICrewDev includes comprehensive configuration validation to prevent errors in production.

### Validation Classes

```python
from src.config.validators import (
    AgentConfigValidator,
    LLMConfigValidator,
    TaskConfigValidator,
    SystemConfigValidator
)

# Validate agent configuration
agent_config = {
    "role": "developer",
    "goal": "Write clean code",
    "backstory": "Experienced developer",
    "allow_code_execution": True
}

try:
    validator = AgentConfigValidator(**agent_config)
    print("✅ Agent configuration is valid")
except ValidationError as e:
    print(f"❌ Validation error: {e}")

# Validate LLM configuration
llm_config = {
    "provider": "openai",
    "model_name": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 2000
}

validator = LLMConfigValidator(**llm_config)
```

### System Health Validation

Check system requirements and dependencies:

```python
from src.config.validators import SystemConfigValidator

# Validate system configuration
system_validator = SystemConfigValidator()

# Check all requirements
validation_result = system_validator.validate_system()

if validation_result.is_valid:
    print("✅ System is ready for AICrewDev")
else:
    print("❌ System validation failed:")
    for issue in validation_result.issues:
        print(f"  • {issue}")
```

### Custom Validation Rules

Add custom validation for specific use cases:

```python
from pydantic import BaseModel, Field, field_validator

class CustomProjectValidator(BaseModel):
    project_type: str
    team_size: int = Field(ge=1, le=10)
    budget: float = Field(gt=0)
    deadline_days: int = Field(ge=1, le=365)
    
    @field_validator('project_type')
    @classmethod
    def validate_project_type(cls, v):
        allowed_types = ['web', 'mobile', 'desktop', 'ai', 'data']
        if v not in allowed_types:
            raise ValueError(f"Project type must be one of {allowed_types}")
        return v
    
    @field_validator('team_size')
    @classmethod
    def validate_team_size(cls, v, info):
        project_type = info.data.get('project_type')
        if project_type == 'ai' and v < 3:
            raise ValueError("AI projects require at least 3 team members")
        return v
```

## Docker Integration

AICrewDev uses Docker for safe code execution in isolated environments.

### Docker Configuration

Configure Docker settings for optimal performance:

```python
from src.config.validators import DockerConfigValidator

# Validate Docker setup
docker_config = {
    "timeout": 300,
    "memory_limit": "2g",
    "cpu_limit": "2.0",
    "network_mode": "bridge",
    "auto_remove": True
}

validator = DockerConfigValidator(**docker_config)
```

### Safe Code Execution

Execute code safely in Docker containers:

```python
from src.utils.docker_executor import DockerExecutor

async def execute_code_safely():
    executor = DockerExecutor(
        image="python:3.11-slim",
        timeout=60,
        memory_limit="512m"
    )
    
    code = """
    print("Hello from Docker!")
    result = sum(range(10))
    print(f"Sum: {result}")
    """
    
    try:
        result = await executor.execute_python_code(code)
        print(f"Output: {result.output}")
        print(f"Exit code: {result.exit_code}")
    finally:
        await executor.cleanup()
```

### Container Management

Manage Docker containers for different development tasks:

```python
# Create specialized containers for different tasks
containers = {
    "python": DockerExecutor("python:3.11-slim"),
    "node": DockerExecutor("node:18-alpine"),
    "database": DockerExecutor("postgres:15-alpine")
}

# Execute tasks in appropriate containers
python_result = await containers["python"].execute_code(python_code)
node_result = await containers["node"].execute_code(javascript_code)
```

## Monitoring & Observability

AICrewDev includes comprehensive monitoring capabilities for production deployments.

### Real-time Monitoring

Monitor agent performance and system health:

```python
from src.monitoring.real_time_monitor import RealTimeMonitor

# Initialize monitoring
monitor = RealTimeMonitor(
    update_interval=1.0,
    metrics_retention_hours=24
)

# Start monitoring
await monitor.start()

# Monitor specific operations
operation_id = "crew_execution_123"
await monitor.track_operation(operation_id, metadata={
    "operation_type": "crew_execution",
    "team_size": 4,
    "project_type": "web_app"
})

# Get real-time metrics
metrics = monitor.get_current_metrics()
print(f"Active operations: {metrics.active_operations}")
print(f"Memory usage: {metrics.memory_usage_mb}MB")
print(f"CPU usage: {metrics.cpu_usage_percent}%")
```

### Metrics Collection

Collect and analyze performance metrics:

```python
from src.monitoring.metrics_collector import MetricsCollector

collector = MetricsCollector()

# Collect agent performance metrics
agent_metrics = collector.collect_agent_metrics(agent)
print(f"Response time: {agent_metrics.avg_response_time}s")
print(f"Success rate: {agent_metrics.success_rate}%")

# Collect system metrics
system_metrics = collector.collect_system_metrics()
print(f"Memory usage: {system_metrics.memory_usage}")
print(f"Disk usage: {system_metrics.disk_usage}")
```

### Health Checking

Monitor system health and availability:

```python
from src.monitoring.health_checker import HealthChecker

health_checker = HealthChecker()

# Check overall system health
health_status = await health_checker.check_system_health()

if health_status.is_healthy:
    print("✅ System is healthy")
else:
    print("❌ System health issues detected:")
    for issue in health_status.issues:
        print(f"  • {issue.component}: {issue.message}")

# Check specific components
docker_health = await health_checker.check_docker_health()
llm_health = await health_checker.check_llm_health(config)
```

## Examples & Tutorials

### Quick Start Example

```python
#!/usr/bin/env python3
"""Quick start example for AICrewDev"""

import asyncio
from src.config.llm_config import LLMConfig, LLMProvider
from src.agents.async_agents import run_development_workflow_async

async def main():
    # Configure LLM
    config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        temperature=0.7
    )
    
    # Run development workflow
    result = await run_development_workflow_async(
        project_type="web_application",
        llm_config=config,
        team_size="standard"
    )
    
    if result.status == "completed":
        print("🎉 Development workflow completed successfully!")
        print(f"Result: {result.result}")
    else:
        print(f"❌ Workflow failed: {result.error}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Agent Example

```python
"""Create custom specialized agents"""

from src.agents.agent_factory import AgentFactory
from crewai import Agent

def create_data_scientist_agent(config):
    """Create a specialized data science agent"""
    optimized_config = AgentFactory._optimize_config_for_role(
        config, "data_scientist"
    )
    
    llm = optimized_config.create_crewai_llm()
    
    return Agent(
        role="Data Scientist",
        goal="Analyze data and build machine learning models",
        backstory="""You are an experienced data scientist with expertise in:
        - Python data analysis (pandas, numpy, scikit-learn)
        - Machine learning model development
        - Data visualization and statistical analysis
        - Feature engineering and model evaluation""",
        llm=llm,
        allow_code_execution=True,
        verbose=True,
        tools=[
            # Add data science specific tools
        ]
    )

# Usage
config = LLMConfig(provider=LLMProvider.OPENAI)
data_scientist = create_data_scientist_agent(config)
```

### Complex Workflow Example

```python
"""Complex multi-team development workflow"""

async def complex_development_workflow():
    factory = AsyncAgentFactory(max_workers=6)
    
    try:
        # Create multiple specialized teams
        frontend_team = await factory.create_agents_batch_async([
            {
                "role": "react_developer",
                "goal": "Build responsive React applications",
                "backstory": "React specialist with TypeScript expertise"
            },
            {
                "role": "ui_designer",
                "goal": "Create beautiful user interfaces",
                "backstory": "UI/UX designer with modern design principles"
            }
        ], config)
        
        backend_team = await factory.create_agents_batch_async([
            {
                "role": "api_developer",
                "goal": "Build scalable REST APIs",
                "backstory": "Backend developer with FastAPI expertise"
            },
            {
                "role": "database_expert",
                "goal": "Design efficient database schemas",
                "backstory": "Database specialist with PostgreSQL expertise"
            }
        ], config)
        
        devops_team = await factory.create_agents_batch_async([
            {
                "role": "devops_engineer",
                "goal": "Manage deployment and infrastructure",
                "backstory": "DevOps expert with Docker and Kubernetes"
            },
            {
                "role": "security_expert",
                "goal": "Ensure application security",
                "backstory": "Security specialist with penetration testing skills"
            }
        ], config)
        
        # Coordinate teams with parallel execution
        all_teams = frontend_team + backend_team + devops_team
        successful_agents = [
            r.result for r in all_teams 
            if r.status == "completed"
        ]
        
        print(f"Created {len(successful_agents)} specialized agents")
        return successful_agents
        
    finally:
        await factory.shutdown()
```

## API Reference

### Core Classes

#### LLMConfig

Configuration class for LLM providers.

**Parameters:**
- `provider` (LLMProvider): LLM provider (openai, anthropic, ollama)
- `model_name` (str): Model name (e.g., "gpt-4o-mini")
- `temperature` (float): Temperature setting (0.0-2.0)
- `max_tokens` (int, optional): Maximum tokens
- `api_key` (str, optional): API key
- `base_url` (str, optional): Base URL for provider
- `verbose` (bool): Enable verbose logging

**Methods:**
- `create_crewai_llm()`: Create CrewAI LLM instance
- `to_crewai_format()`: Convert to CrewAI format
- `validate()`: Validate configuration

#### AsyncAgentFactory

Factory for creating agents asynchronously.

**Parameters:**
- `max_workers` (int): Maximum concurrent operations

**Methods:**
- `create_agent_async()`: Create single agent
- `create_agents_batch_async()`: Create multiple agents
- `create_development_team_async()`: Create development team
- `execute_tasks_async()`: Execute tasks in parallel
- `get_operation_status()`: Get operation status
- `wait_for_operation()`: Wait for operation completion
- `shutdown()`: Cleanup resources

#### AsyncOperationResult

Result object for async operations.

**Properties:**
- `operation_id` (str): Unique operation ID
- `status` (AsyncOperationStatus): Operation status
- `result` (Any): Operation result
- `error` (Exception, optional): Error if failed
- `duration` (float, optional): Duration in seconds
- `is_complete` (bool): Whether operation is complete

### Validation Classes

#### AgentConfigValidator

Validates agent configurations.

**Fields:**
- `role` (str): Agent role
- `goal` (str): Agent goal
- `backstory` (str): Agent backstory
- `allow_delegation` (bool): Allow delegation
- `allow_code_execution` (bool): Allow code execution
- `verbose` (bool): Verbose mode

#### SystemConfigValidator

Validates system requirements.

**Methods:**
- `validate_python_version()`: Check Python version
- `validate_docker_installation()`: Check Docker
- `validate_dependencies()`: Check dependencies
- `validate_system()`: Full system validation

## Best Practices

### Configuration Management

1. **Use Environment Variables** for sensitive data:
   ```python
   import os
   
   config = LLMConfig(
       provider=LLMProvider.OPENAI,
       api_key=os.getenv("OPENAI_API_KEY"),
       model_name=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
   )
   ```

2. **Validate Configurations** before deployment:
   ```python
   # Always validate before using
   try:
       validator = LLMConfigValidator(**config_dict)
       config = LLMConfig(**validator.model_dump())
   except ValidationError as e:
       logger.error(f"Configuration invalid: {e}")
       raise
   ```

3. **Use YAML** for complex configurations:
   ```yaml
   # config/production.yaml
   llm:
     provider: openai
     model_name: gpt-4o-mini
     temperature: 0.7
     max_tokens: 2000
   
   agents:
     tech_lead:
       temperature: 0.3
       allow_delegation: true
     developer:
       temperature: 0.5
       allow_code_execution: true
   ```

### Performance Optimization

1. **Use Async Operations** for better performance:
   ```python
   # Good: Concurrent execution
   results = await factory.create_agents_batch_async(configs, llm_config)
   
   # Avoid: Sequential execution
   agents = []
   for config in configs:
       agent = await factory.create_agent_async(config, llm_config)
       agents.append(agent)
   ```

2. **Optimize Temperature** for different roles:
   ```python
   role_temperatures = {
       "code_reviewer": 0.2,    # More focused
       "creative_writer": 0.9,   # More creative
       "tech_lead": 0.3,        # Balanced
       "developer": 0.5         # Moderate creativity
   }
   ```

3. **Use Connection Pooling** for API calls:
   ```python
   config = LLMConfig(
       provider=LLMProvider.OPENAI,
       max_retries=3,
       max_rpm=100  # Respect rate limits
   )
   ```

### Error Handling

1. **Always Handle Async Errors**:
   ```python
   try:
       result = await factory.create_development_team_async(config)
       if result.status != AsyncOperationStatus.COMPLETED:
           logger.error(f"Team creation failed: {result.error}")
           return None
   except Exception as e:
       logger.exception("Unexpected error in team creation")
       raise
   ```

2. **Implement Retry Logic**:
   ```python
   async def create_agent_with_retry(factory, config, max_retries=3):
       for attempt in range(max_retries):
           try:
               result = await factory.create_agent_async(config)
               if result.status == AsyncOperationStatus.COMPLETED:
                   return result.result
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
               await asyncio.sleep(2 ** attempt)  # Exponential backoff
   ```

3. **Graceful Degradation**:
   ```python
   async def create_team_with_fallback(config, team_size="standard"):
       try:
           # Try to create full team
           result = await factory.create_development_team_async(
               config, team_size=team_size
           )
           return result.result
       except Exception:
           # Fallback to minimal team
           logger.warning("Full team creation failed, using minimal team")
           result = await factory.create_development_team_async(
               config, team_size="minimal"
           )
           return result.result
   ```

### Security

1. **Never Log API Keys**:
   ```python
   # Good: Mask sensitive data
   logger.info(f"Using provider: {config.provider}")
   
   # Bad: Don't log API keys
   # logger.info(f"Config: {config}")  # This could expose api_key
   ```

2. **Use Docker for Code Execution**:
   ```python
   # Always use Docker for untrusted code
   agent = Agent(
       role="developer",
       allow_code_execution=True,  # This uses Docker automatically
       tools=[safe_execution_tool]
   )
   ```

3. **Validate Input Data**:
   ```python
   @field_validator('code_input')
   @classmethod
   def validate_code_input(cls, v):
       # Prevent malicious code patterns
       dangerous_patterns = ['import os', 'subprocess', '__import__']
       for pattern in dangerous_patterns:
           if pattern in v:
               raise ValueError(f"Dangerous pattern detected: {pattern}")
       return v
   ```

### Monitoring

1. **Monitor Resource Usage**:
   ```python
   from src.monitoring.real_time_monitor import RealTimeMonitor
   
   monitor = RealTimeMonitor()
   await monitor.start()
   
   # Check metrics regularly
   if monitor.get_memory_usage() > 80:
       logger.warning("High memory usage detected")
   ```

2. **Track Operation Metrics**:
   ```python
   # Track important metrics
   start_time = time.time()
   result = await operation()
   duration = time.time() - start_time
   
   metrics_collector.record_metric(
       "operation_duration",
       duration,
       tags={"operation_type": "agent_creation"}
   )
   ```

3. **Set Up Alerts**:
   ```python
   # Set up alerts for critical metrics
   if operation_duration > 300:  # 5 minutes
       alert_manager.send_alert(
           "Long running operation detected",
           severity="warning"
       )
   ```

## Troubleshooting

### Common Issues

#### Docker Not Available

**Problem**: `Docker not available` error
**Solution**:
```bash
# Check Docker status
docker --version
docker ps

# Start Docker Desktop (macOS/Windows)
# Or start Docker daemon (Linux)
sudo systemctl start docker
```

#### API Key Errors

**Problem**: `Invalid API key` or `Authentication failed`
**Solution**:
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Set environment variables
export OPENAI_API_KEY="your-key-here"

# Or use .env file
echo "OPENAI_API_KEY=your-key-here" >> .env
```

#### Memory Issues

**Problem**: `Out of memory` during large operations
**Solution**:
```python
# Reduce concurrent operations
factory = AsyncAgentFactory(max_workers=2)  # Reduce from 4

# Use smaller teams
result = await factory.create_development_team_async(
    config, team_size="minimal"
)

# Clean up regularly
factory.cleanup_operations(max_age_hours=1)
```

#### Model Not Found

**Problem**: `Model not found` for Ollama
**Solution**:
```bash
# Pull the model first
ollama pull llama2

# Check available models
ollama list

# Use correct model name
config = LLMConfig(
    provider=LLMProvider.OLLAMA,
    model_name="llama2"  # Must match ollama list output
)
```

### Performance Issues

#### Slow Agent Creation

**Problem**: Agent creation takes too long
**Solution**:
```python
# Use async batch creation
results = await factory.create_agents_batch_async(configs, llm_config)

# Optimize LLM settings
config = LLMConfig(
    max_tokens=1000,  # Reduce token limit
    temperature=0.5,   # Reduce for faster responses
    max_retries=1     # Reduce retries
)
```

#### Rate Limit Errors

**Problem**: `Rate limit exceeded` errors
**Solution**:
```python
# Implement rate limiting
config = LLMConfig(
    max_rpm=60,  # Respect API limits
    max_retries=3
)

# Add delays between requests
await asyncio.sleep(1)  # Add delay between operations
```

### Debugging

#### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable verbose mode
config = LLMConfig(verbose=True)
```

#### Monitor Operations

```python
# Monitor active operations
active_ops = factory.get_active_operations()
for op_id, operation in active_ops.items():
    print(f"Operation {op_id}: {operation.status}")
    if operation.metadata:
        print(f"  Metadata: {operation.metadata}")
```

#### Check System Health

```python
from src.monitoring.health_checker import HealthChecker

health_checker = HealthChecker()
health_status = await health_checker.check_system_health()

print(f"System healthy: {health_status.is_healthy}")
for issue in health_status.issues:
    print(f"Issue: {issue}")
```

---

For more information and updates, visit the [AICrewDev repository](https://github.com/your-repo/aicrewdev).
