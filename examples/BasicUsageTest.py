import sys
import os
from src.main import AICrewDev
from examples.docker_free_ollama_main import DockerFreeOllamaAICrewDev

# Set environment variables to fix memory requirements
os.environ.setdefault("CHROMA_OPENAI_API_KEY", "dummy-key-for-local-testing")
os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-local-testing")

# Initialize AICrewDev
ai_crew = AICrewDev()

# Run development workflow
result = ai_crew.run(project_type="web", use_crew_manager=True)

# Run analysis workflow
analysis_result = ai_crew.run_analysis("project codebase")

# Get system status
status = ai_crew.get_status()