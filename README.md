# AICrewDev - Advanced AI Development Team Simulator

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-green.svg)](https://github.com/joaomdmoura/crewAI)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)
[![Async](https://img.shields.io/badge/Async-Enabled-purple.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AICrewDev is a sophisticated AI-powered development team simulator built on the CrewAI framework. It creates specialized AI agents that work together as a cohesive development team to tackle complex software development projects.

## 🌟 Key Features

### ⚡ **Asynchronous Operations** (NEW!)
- **Concurrent Agent Creation**: Create multiple agents simultaneously for faster team building
- **Parallel Task Execution**: Execute development tasks concurrently for improved performance
- **Real-time Progress Monitoring**: Track operations as they happen with live updates
- **Background Processing**: Long-running operations with non-blocking execution

### 🛡️ **Production-Ready Validation** (NEW!)
- **Comprehensive Configuration Validation**: Prevent errors before deployment
- **System Health Checks**: Validate dependencies and requirements
- **Docker Integration Validation**: Ensure safe code execution environment
- **LLM Provider Validation**: Verify API connectivity and model availability

### 🐳 **Docker Integration** (NEW!)
- **Safe Code Execution**: All code runs in isolated Docker containers
- **Automatic Container Management**: Containers are created, managed, and cleaned up automatically
- **Multi-Environment Support**: Support for different development environments
- **Security-First Approach**: Isolated execution prevents system compromise

### 🤖 **Multi-Agent Architecture**
- **Specialized Agent Roles**: Tech Lead, Developer, Code Reviewer, Project Manager
- **Role-Optimized LLM Settings**: Each agent type uses optimized temperature and parameters
- **Collaborative Workflows**: Agents work together on complex development tasks
- **Scalable Team Sizes**: Support for minimal, standard, and large team configurations

### 🔗 **Multi-Provider LLM Support**
- **OpenAI**: GPT-4, GPT-3.5-turbo with native CrewAI integration
- **Anthropic**: Claude-3 models with enhanced reasoning capabilities
- **Ollama**: Local LLM deployment for privacy and cost control
- **Groq**: High-speed inference for rapid development cycles

### 📊 **Advanced Monitoring & Observability**
- **Real-time Metrics**: CPU, memory, and operation tracking
- **Performance Analytics**: Response times, success rates, and throughput
- **Health Monitoring**: System health checks and dependency validation
- **Structured Logging**: Comprehensive logging for debugging and analysis

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - Required for modern async features
- **Docker Desktop** - Essential for safe code execution
- **Git** - For version control and repository management

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd AICrewDev

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify Docker installation
docker --version
docker run hello-world
```

### Basic Usage

```python
import asyncio
from src.config.llm_config import LLMConfig, LLMProvider
from src.agents.async_agents import run_development_workflow_async

async def main():
    # Configure your LLM provider
    config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        temperature=0.7
    )
    
    # Run an async development workflow
    result = await run_development_workflow_async(
        project_type="web_application",
        llm_config=config,
        team_size="standard"
    )
    
    if result.status == "completed":
        print("🎉 Development workflow completed!")
        print(f"Result: {result.result}")
    else:
        print(f"❌ Workflow failed: {result.error}")

# Run the async workflow
asyncio.run(main())
```

## 🏗️ Architecture Overview

AICrewDev uses a layered architecture designed for scalability and maintainability:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Async Agents    │  Validation    │  Monitoring    │ Docker │
├─────────────────────────────────────────────────────────────┤
│              Core Services Layer                            │
├─────────────────────────────────────────────────────────────┤
│  Agent Factory   │  Crew Manager  │  Task Factory          │
├─────────────────────────────────────────────────────────────┤
│                  Configuration Layer                        │
├─────────────────────────────────────────────────────────────┤
│  LLM Config      │  Agent Config  │  System Config         │
├─────────────────────────────────────────────────────────────┤
│                   Foundation Layer                          │
└─────────────────────────────────────────────────────────────┘
│              CrewAI Framework & LLM Providers               │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

- **Async Agent Factory**: Creates and manages agents concurrently
- **Crew Manager**: Orchestrates team workflows and task execution
- **Configuration Validation**: Ensures all settings are correct before deployment
- **Docker Integration**: Provides safe, isolated code execution environment
- **Real-time Monitoring**: Tracks performance and system health
- **Multi-Provider LLM Support**: Integrates with various AI model providers

## 📚 Documentation

### Quick Links
- 📖 **[Advanced Guide](docs/ADVANCED_GUIDE.md)** - Comprehensive documentation with examples
- 🏁 **[Getting Started](docs/getting_started.md)** - Step-by-step setup guide
- 🏛️ **[Architecture](docs/architecture.md)** - Detailed system architecture
- ⚙️ **[LLM Configuration](docs/llm_configuration.md)** - Provider-specific setup

### Example Scripts
- 🚀 **[Async Agents Demo](examples/async_agents_demo.py)** - Showcase async capabilities
- 🔧 **[Enhanced Architecture](examples/enhanced_architecture_demo.py)** - Full system demo
- 📊 **[Real-time Monitoring](examples/enhanced_real_time_demo.py)** - Monitoring features
- 🦙 **[Ollama Integration](examples/ollama_llama2_demo.py)** - Local LLM usage

## ⚡ Async Capabilities (NEW!)

### Concurrent Agent Creation

Create multiple agents simultaneously for faster team building:

```python
from src.agents.async_agents import AsyncAgentFactory

async def create_team():
    factory = AsyncAgentFactory(max_workers=4)
    
    agent_configs = [
        {"role": "frontend_developer", "goal": "Build React UIs", ...},
        {"role": "backend_developer", "goal": "Create APIs", ...},
        {"role": "devops_engineer", "goal": "Manage deployments", ...}
    ]
    
    # Create all agents concurrently
    results = await factory.create_agents_batch_async(agent_configs, config)
    agents = [r.result for r in results if r.status == "completed"]
    
    return agents
```

### Parallel Task Execution

Execute development tasks concurrently:

```python
# Execute tasks in parallel for better performance
result = await factory.execute_tasks_async(
    tasks=development_tasks,
    agents=team_agents,
    execution_mode="parallel"  # or "sequential"
)
```

### Real-time Operation Monitoring

Monitor long-running operations:

```python
# Start operation and monitor progress
operation = await factory.create_development_team_async(config)

# Track progress in real-time
while not operation.is_complete:
    print(f"Status: {operation.status}, Duration: {operation.duration}s")
    await asyncio.sleep(1)
```

## 🛡️ Configuration Validation (NEW!)

Comprehensive validation prevents configuration errors:

```python
from src.config.validators import (
    AgentConfigValidator,
    LLMConfigValidator,
    SystemConfigValidator
)

# Validate agent configuration
agent_config = {
    "role": "developer",
    "goal": "Write clean code",
    "backstory": "Experienced developer",
    "allow_code_execution": True
}

validator = AgentConfigValidator(**agent_config)
print("✅ Agent configuration is valid")

# Validate system requirements
system_validator = SystemConfigValidator()
validation_result = system_validator.validate_system()

if validation_result.is_valid:
    print("✅ System ready for AICrewDev")
else:
    for issue in validation_result.issues:
        print(f"❌ {issue}")
```

## 🐳 Docker Integration (NEW!)

Safe code execution in isolated containers:

```python
# Agents automatically use Docker for code execution
agent = Agent(
    role="developer",
    allow_code_execution=True,  # Uses Docker automatically
    goal="Write and test code safely"
)

# Docker containers are managed automatically:
# - Created when needed
# - Isolated from host system
# - Cleaned up after use
# - Security-first approach
```

## 📊 Monitoring & Observability

Real-time monitoring and metrics collection:

```python
from src.monitoring.real_time_monitor import RealTimeMonitor

# Start monitoring
monitor = RealTimeMonitor()
await monitor.start()

# Get real-time metrics
metrics = monitor.get_current_metrics()
print(f"Active operations: {metrics.active_operations}")
print(f"Memory usage: {metrics.memory_usage_mb}MB")
print(f"CPU usage: {metrics.cpu_usage_percent}%")
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GROQ_API_KEY=your_groq_api_key

# Ollama Configuration (if not running locally)
OLLAMA_BASE_URL=http://localhost:11434

# Docker Settings
DOCKER_TIMEOUT=300
DOCKER_MEMORY_LIMIT=2g

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aicrewdev.log
```

### LLM Provider Setup

#### OpenAI
```python
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    model_name="gpt-4o-mini",
    temperature=0.7,
    api_key="your-api-key"  # Or use OPENAI_API_KEY env var
)
```

#### Ollama (Local)
```bash
# Install and start Ollama
ollama pull llama2
ollama serve

# Configure AICrewDev
config = LLMConfig(
    provider=LLMProvider.OLLAMA,
    model_name="llama2",
    base_url="http://localhost:11434"
)
```

#### Anthropic
```python
config = LLMConfig(
    provider=LLMProvider.ANTHROPIC,
    model_name="claude-3-haiku-20240307",
    api_key="your-api-key"  # Or use ANTHROPIC_API_KEY env var
)
```

## 🎯 Use Cases

### Web Development Team
```python
# Create a specialized web development team
result = await factory.create_development_team_async(
    config=config,
    project_type="web_application",
    team_size="standard"
)
```

### Mobile App Development
```python
# Mobile-focused development workflow
result = await run_development_workflow_async(
    project_type="mobile_app",
    llm_config=config,
    custom_tasks=[
        "Design mobile app architecture",
        "Implement native iOS/Android features",
        "Create responsive UI components",
        "Set up app store deployment"
    ]
)
```

### AI/ML Project Team
```python
# AI project with specialized agents
agent_configs = [
    {
        "role": "data_scientist",
        "goal": "Build machine learning models",
        "backstory": "ML expert with Python and TensorFlow"
    },
    {
        "role": "ml_engineer",
        "goal": "Deploy models to production",
        "backstory": "MLOps specialist with cloud platforms"
    }
]
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_enhanced_config.py
python -m pytest tests/test_llm.py
python -m pytest tests/test_main.py

# Run with verbose output
python -m pytest -v tests/
```

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/aicrewdev.git
cd aicrewdev

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run tests before committing
python -m pytest tests/
```

## 📋 Roadmap

### Phase 2 (Current)
- ✅ Asynchronous agent operations
- ✅ Configuration validation system
- ✅ Docker integration for safe execution
- ✅ Enhanced documentation

### Phase 3 (Next)
- 🔄 Web-based management interface
- 🔄 Integration with popular IDEs
- 🔄 Advanced workflow templates
- 🔄 Plugin system for extensibility

### Phase 4 (Future)
- 🔄 Distributed agent execution
- 🔄 Advanced AI model fine-tuning
- 🔄 Enterprise security features
- 🔄 Cloud deployment options

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: [Advanced Guide](docs/ADVANCED_GUIDE.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/your-repo/aicrewdev/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/aicrewdev/discussions)
- 📧 **Email**: support@aicrewdev.com

## 🙏 Acknowledgments

- **CrewAI Team** - For the excellent multi-agent framework
- **OpenAI, Anthropic, Ollama** - For providing powerful LLM capabilities
- **Docker** - For containerization and safe execution
- **Python Community** - For the amazing ecosystem and tools

---

**Made with ❤️ by the AICrewDev Team**

*Empowering developers with AI-powered development teams*
