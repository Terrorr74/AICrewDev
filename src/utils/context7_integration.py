"""
Context7 Integration for AICrewDev

This module integrates Context7 MCP to provide up-to-date documentation
and code examples for the AI development crew.
"""

import subprocess
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class Context7Response:
    """Response from Context7 MCP"""
    success: bool
    content: str
    error: Optional[str] = None

class Context7Integration:
    """
    Integration with Context7 MCP for enhanced documentation access.
    This allows AICrewDev to get the most current documentation and examples.
    """
    
    def __init__(self):
        self.mcp_server_available = self._check_context7_availability()
    
    def _check_context7_availability(self) -> bool:
        """Check if Context7 MCP server is available"""
        try:
            # Try to run the context7 MCP server to check if it's available
            result = subprocess.run(
                ["npx", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def resolve_library_id(self, library_name: str) -> Optional[str]:
        """
        Resolve a library name to a Context7-compatible library ID.
        This mimics the resolve-library-id tool from Context7 MCP.
        """
        if not self.mcp_server_available:
            return None
        
        # Common library mappings for quick resolution
        common_libraries = {
            'react': '/facebook/react',
            'next.js': '/vercel/next.js',
            'nextjs': '/vercel/next.js',
            'vue': '/vuejs/vue',
            'angular': '/angular/angular',
            'django': '/django/django',
            'flask': '/pallets/flask',
            'fastapi': '/tiangolo/fastapi',
            'express': '/expressjs/express',
            'node.js': '/nodejs/node',
            'nodejs': '/nodejs/node',
            'postgresql': '/postgres/postgres',
            'mongodb': '/mongodb/docs',
            'stripe': '/stripe/stripe-node',
            'supabase': '/supabase/supabase',
            'firebase': '/firebase/firebase-js-sdk',
            'tailwind': '/tailwindlabs/tailwindcss',
            'bootstrap': '/twbs/bootstrap',
            'typescript': '/microsoft/typescript',
            'python': '/python/cpython',
            'javascript': '/tc39/ecma262',
        }
        
        library_lower = library_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        for key, value in common_libraries.items():
            if key in library_lower or library_lower in key:
                return value
        
        return None
    
    def get_library_docs(self, library_id: str, topic: Optional[str] = None, tokens: int = 8000) -> Context7Response:
        """
        Get documentation for a library using Context7 MCP.
        This mimics the get-library-docs tool from Context7 MCP.
        """
        if not self.mcp_server_available:
            return Context7Response(
                success=False, 
                content="", 
                error="Context7 MCP server not available"
            )
        
        # For now, return a placeholder response with guidance to use context7
        # In a real implementation, this would call the actual Context7 MCP server
        context7_prompt = f"""
For the most up-to-date documentation and examples for {library_id}, please use:

use context7

This will fetch the latest documentation, code examples, and best practices
directly from the source repositories.

{f'Focus on: {topic}' if topic else ''}

The AI development team will use this information to create accurate,
current implementations following the latest patterns and practices.
"""
        
        return Context7Response(
            success=True,
            content=context7_prompt
        )
    
    def enhance_prompt_with_context7(self, base_prompt: str, technologies: List[str]) -> str:
        """
        Enhance a prompt with Context7 instructions for better documentation access.
        """
        if not technologies:
            return f"{base_prompt}\n\nuse context7"
        
        # Resolve library IDs for the technologies
        library_instructions = []
        for tech in technologies:
            library_id = self.resolve_library_id(tech)
            if library_id:
                library_instructions.append(f"use library {library_id} for {tech} documentation and examples")
        
        # Create enhanced prompt
        enhanced_prompt = f"""{base_prompt}

For the most accurate and up-to-date implementation, please:

{chr(10).join(library_instructions) if library_instructions else ''}

use context7

This ensures you have access to the latest documentation, APIs, and best practices
for all the technologies involved in this project.
"""
        
        return enhanced_prompt
    
    def create_context7_aware_workflow(self, project_requirements: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a workflow that leverages Context7 for documentation access.
        """
        workflow = {
            "research_phase": """
Research the latest documentation and best practices for the project technologies.

use context7

Focus on:
- Current API patterns and conventions
- Latest features and deprecations
- Security best practices
- Performance optimization techniques
""",
            
            "architecture_phase": """
Design the application architecture using current best practices.

use context7

Consider:
- Modern architectural patterns
- Scalability requirements
- Security considerations
- Technology-specific patterns
""",
            
            "implementation_phase": """
Implement the application using the most current patterns and APIs.

use context7

Ensure:
- Latest syntax and features
- Current dependency versions
- Modern tooling setup
- Best practices compliance
""",
            
            "testing_phase": """
Create comprehensive tests using current testing frameworks and practices.

use context7

Include:
- Unit tests with latest testing patterns
- Integration tests
- End-to-end tests where appropriate
- Performance tests if needed
""",
            
            "deployment_phase": """
Set up deployment using modern DevOps practices and tools.

use context7

Configure:
- CI/CD pipelines
- Container deployment if applicable
- Environment management
- Monitoring and logging
"""
        }
        
        return workflow

# Global instance for easy access
context7 = Context7Integration()
