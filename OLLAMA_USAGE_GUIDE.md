# 🦙 Using AICrewDev Main with Ollama - Complete Guide

This guide shows you exactly how to use the main AICrewDev system with Ollama for local AI development without API costs.

## 📋 **Prerequisites**

### 1. Install Ollama
```bash
# Visit https://ollama.ai/ and install for your system
# Or use Homebrew on macOS:
brew install ollama
```

### 2. Start Ollama Service
```bash
ollama serve
```

### 3. Pull AI Models
```bash
# Pull Llama2 (recommended for development)
ollama pull llama2

# Optional: Pull other models
ollama pull mistral
ollama pull codellama
```

## ⚙️ **Configuration Methods**

### **Method 1: Environment Variables (.env file)**

Create a `.env` file in your AICrewDev root directory:

```bash
# Ollama Configuration for AICrewDev
LLM_PROVIDER=ollama
LLM_MODEL_NAME=llama2
LLM_TEMPERATURE=0.7
LLM_API_BASE=http://localhost:11434
LLM_MAX_TOKENS=2048
LLM_TIMEOUT=60
LLM_VERBOSE=true

# AICrewDev Settings
AICREWDEV_DEBUG=true
AICREWDEV_ENVIRONMENT=development
AICREWDEV_LOG_LEVEL=INFO
```

### **Method 2: Shell Environment Variables**

```bash
export LLM_PROVIDER=ollama
export LLM_MODEL_NAME=llama2
export LLM_TEMPERATURE=0.7
export LLM_API_BASE=http://localhost:11434
export AICREWDEV_DEBUG=true
```

## 🚀 **Usage Options**

### **Option 1: Direct Main Usage (Docker-Free)**

Use our Docker-free version that works without containers:

```bash
python3 examples/docker_free_ollama_main.py
```

**What this does:**
- ✅ Creates AI agents without Docker requirements
- ✅ Demonstrates real-time monitoring
- ✅ Shows complete workflow execution
- ✅ Uses local Ollama + Llama2

### **Option 2: Custom Python Script**

Create your own script using AICrewDev with Ollama:

```python
#!/usr/bin/env python3
"""
Custom AICrewDev with Ollama Example
"""

import os
import sys
sys.path.append('src')

# Configure Ollama
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["LLM_MODEL_NAME"] = "llama2"
os.environ["LLM_TEMPERATURE"] = "0.7"
os.environ["LLM_API_BASE"] = "http://localhost:11434"

from main import AICrewDev
from core.settings import Settings

# Create custom settings for Ollama
settings = Settings.for_development()

# Initialize AICrewDev
ai_crew = AICrewDev(settings)

# Get system status
status = ai_crew.get_status()
print(f"Provider: {status['application']['llm_provider']}")
print(f"Model: {status['application']['llm_model']}")

# Run development workflow
try:
    result = ai_crew.run(project_type="web", use_crew_manager=False)
    print(f"Success: {result}")
except Exception as e:
    print(f"Note: {e}")
    # This might fail due to Docker requirements in some agents
```

### **Option 3: Configuration-Based Approach**

Use the LLM configuration system directly:

```python
#!/usr/bin/env python3
"""
Direct Configuration Approach
"""

import sys
sys.path.append('src')

from config.llm_config import LLMConfig, LLMProvider
from agents.agent_factory import AgentFactory
from monitoring import get_global_monitor

# Create Ollama configuration
config = LLMConfig(
    provider=LLMProvider.OLLAMA,
    model_name="llama2",
    temperature=0.7,
    base_url="http://localhost:11434",
    verbose=True
)

# Create monitoring
monitor = get_global_monitor()

# Create agents (avoid Docker requirements)
print("Creating Tech Lead...")
tech_lead = AgentFactory.create_tech_lead(config)

print("Creating Project Manager...")
manager = AgentFactory.create_project_manager(config)

print(f"✅ Created agents with Ollama!")
print(f"Tech Lead: {tech_lead.role}")
print(f"Manager: {manager.role}")
```

## 🔧 **Troubleshooting**

### **Issue 1: Docker Requirements**

**Problem:** "Docker is not installed" error

**Solution:** Use Docker-free agents or disable code execution:

```python
# Instead of create_developer (which requires Docker):
developer = AgentFactory.create_developer(config, specialization="frontend")

# Use these Docker-free alternatives:
tech_lead = AgentFactory.create_tech_lead(config)
manager = AgentFactory.create_project_manager(config) 
reviewer = AgentFactory.create_code_reviewer(config)
```

### **Issue 2: Ollama Connection Errors**

**Problem:** Cannot connect to Ollama

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Check available models
ollama list
```

### **Issue 3: Model Not Found**

**Problem:** "llama2 model not found"

**Solution:**
```bash
# Pull the model
ollama pull llama2

# Verify it's available
ollama list

# Try alternative models
ollama pull mistral
```

## 📊 **Real-Time Monitoring with Ollama**

The Docker-free version includes full monitoring:

```
🦙 Docker-Free AICrewDev + Ollama Integration
=======================================================

🤖 Creating AI agents (Docker-free)...
✅ [██████████████████████████████] 100.0% | Completed
✅ Created 3 Docker-free agents:
   • Tech Lead: Technical Lead
   • Business Analyst: Business Analyst  
   • Quality Reviewer: Quality Reviewer

💬 Testing LLM interaction...
✅ [██████████████████████████████] 100.0% | Completed (37.1 tok/s)

📈 Monitoring Summary:
   agent_creation: 1 ops, avg 3.0s
   llm_chat: 1 ops, avg 4.0s
   crew_execution: 1 ops, avg 10.1s
```

## 🎯 **Recommended Models for Different Tasks**

### **Development Tasks:**
- **llama2**: General purpose, good balance
- **codellama**: Specialized for code generation
- **mistral**: Fast and efficient

### **Analysis Tasks:**
- **llama2**: Comprehensive analysis
- **mistral**: Quick insights

### **Review Tasks:**
- **llama2**: Detailed reviews
- **codellama**: Code-specific reviews

## 💡 **Best Practices**

### **1. Model Selection**
```bash
# For code-heavy workflows
export LLM_MODEL_NAME=codellama

# For general workflows  
export LLM_MODEL_NAME=llama2

# For fast processing
export LLM_MODEL_NAME=mistral
```

### **2. Temperature Tuning**
```bash
# For consistent results (reviews, analysis)
export LLM_TEMPERATURE=0.1

# For creative tasks
export LLM_TEMPERATURE=0.9

# For balanced performance
export LLM_TEMPERATURE=0.7
```

### **3. Performance Optimization**
```bash
# Increase timeout for complex tasks
export LLM_TIMEOUT=120

# Increase max tokens for longer responses
export LLM_MAX_TOKENS=4096
```

## 🚀 **Production Usage**

### **1. Multiple Models**
Run different models for different agent types:

```python
# Tech Lead with reasoning model
tech_config = LLMConfig(provider=LLMProvider.OLLAMA, model_name="llama2")
tech_lead = AgentFactory.create_tech_lead(tech_config)

# Code tasks with specialized model  
code_config = LLMConfig(provider=LLMProvider.OLLAMA, model_name="codellama")
# Note: Use non-Docker requiring agents for production
```

### **2. Monitoring & Analytics**
The real-time monitoring system tracks:
- ✅ Token usage and rates
- ✅ Response times 
- ✅ Success rates
- ✅ Operation performance
- ✅ System health

### **3. Scaling**
- **Single Instance**: Perfect for development
- **Multiple Instances**: Run multiple Ollama servers
- **Load Balancing**: Distribute across different models

## 🎉 **Summary**

### **Quick Start:**
1. Install Ollama: `brew install ollama`
2. Start service: `ollama serve`
3. Pull model: `ollama pull llama2`
4. Run Docker-free version: `python3 examples/docker_free_ollama_main.py`

### **Benefits:**
- 🆓 **Zero API costs** - completely free
- 🔒 **Complete privacy** - no data leaves your machine  
- 📊 **Full monitoring** - real-time progress tracking
- 🚫 **No Docker required** - simple setup
- 🚀 **Fast local inference** - no network latency

### **Perfect For:**
- Development and testing
- Privacy-sensitive projects
- Cost-conscious deployments
- Learning and experimentation
- Offline environments

You now have a complete, production-ready AI development system running locally with full monitoring capabilities! 🎊
