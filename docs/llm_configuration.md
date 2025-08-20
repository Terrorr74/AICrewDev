# LLM Configuration Guide

This guide explains how to configure different Language Learning Models (LLMs) in the AICrewDev framework.

## Overview

AICrewDev supports multiple LLM providers:
- Ollama (default, local)
- OpenAI
- Other hosted models

## Configuration Options

The LLM configuration can be set through environment variables:

```env
# Provider Selection
LLM_PROVIDER=ollama  # Options: ollama, openai, other

# Model Configuration
LLM_MODEL_NAME=llama2  # Model name (e.g., llama2, gpt-4, etc.)
LLM_TEMPERATURE=0.5    # Temperature for response generation (default: 0.5)
LLM_MAX_TOKENS=2000    # Maximum tokens per response

# API Configuration
LLM_API_KEY=your_key   # Required for OpenAI and other providers
LLM_API_BASE=your_url  # Required for other providers
```

## Provider-Specific Setup

### Ollama (Default)

```env
LLM_PROVIDER=ollama
LLM_MODEL_NAME=llama2
```

Ollama runs locally and doesn't require an API key. Make sure you have Ollama installed and the model pulled.

### OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-4
LLM_API_KEY=your_openai_key
```

Requires an OpenAI API key. Available models include:
- gpt-4
- gpt-3.5-turbo
- Others as provided by OpenAI

### Other Hosted Models

```env
LLM_PROVIDER=other
LLM_MODEL_NAME=your_model
LLM_API_BASE=https://your.api.endpoint
LLM_API_KEY=your_api_key
```

Use this for other hosted LLM providers. You'll need to provide both the API base URL and key.

## Usage in Code

### Basic Usage

```python
from src.config import LLMConfig
from src.agents.agent_factory import AgentFactory

# Uses configuration from environment variables
tech_lead = AgentFactory.create_tech_lead()
```

### Custom Configuration

```python
from src.config import LLMConfig, LLMProvider

# Create custom configuration
config = LLMConfig(
    provider=LLMProvider.OLLAMA,
    model_name="codellama",
    temperature=0.5
)

# Create agent with custom config
tech_lead = AgentFactory.create_tech_lead(config)
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| LLM_PROVIDER | No | "ollama" | The LLM provider to use |
| LLM_MODEL_NAME | No | "llama2" | Name of the model to use |
| LLM_TEMPERATURE | No | 0.5 | Temperature for response generation |
| LLM_MAX_TOKENS | No | None | Maximum tokens per response |
| LLM_API_KEY | For OpenAI/Other | None | API key for the provider |
| LLM_API_BASE | For Other | None | Base URL for API endpoint |

## Testing

You can run the LLM configuration tests with:

```bash
python -m unittest tests/test_llm.py
```
