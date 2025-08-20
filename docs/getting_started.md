# Getting Started with AICrewDev

## Introduction
AICrewDev is an AI-powered development team simulator built using the CrewAI framework. It creates a virtual team of AI agents that collaborate on software development tasks.

## Quick Start

1. **Environment Setup**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
.\.venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

2. **Configure Environment Variables**
Copy `.env.example` to `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. **Run the Application**
```bash
python src/main.py
```

## Project Structure

```
AICrewDev/
├── src/                    # Source code
│   ├── agents/            # AI agent definitions
│   │   └── agent_factory.py
│   ├── tasks/             # Task definitions
│   │   └── task_factory.py
│   ├── utils/             # Utility functions
│   │   └── environment.py
│   └── main.py           # Application entry point
├── docs/                  # Documentation
└── tests/                # Test files
```

## AI Agents

The project includes three specialized AI agents:

1. **Tech Lead**
   - Oversees technical decisions
   - Ensures architectural consistency
   - Reviews and approves major changes

2. **Developer**
   - Implements features and fixes
   - Writes clean, efficient code
   - Follows best practices

3. **Code Reviewer**
   - Reviews code changes
   - Ensures code quality
   - Provides feedback and suggestions

## Task Workflow

1. Tasks are created using the `TaskFactory`
2. Agents are assigned to tasks based on their roles
3. The crew executes tasks in sequence
4. Results are collected and reported

## Best Practices

- Always activate the virtual environment before running the project
- Keep the OpenAI API key secure
- Follow the existing code structure for new additions
- Document new features and changes
