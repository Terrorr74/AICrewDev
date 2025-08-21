#!/usr/bin/env python3
"""
AICrewDev Natural Language CLI

A natural language interface for creating applications quickly using only terminal commands.
This CLI integrates Context7 for up-to-date documentation and provides an intelligent
manager-like experience to guide users through application development.

Usage:
    python natural_language_cli.py
    
Features:
    - Natural language application creation
    - Context7 integration for current documentation
    - Interactive manager guidance
    - Automatic project setup and configuration
    - Smart technology recommendations
"""

import os
import sys
import asyncio
import json
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import argparse
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import AICrewDev
from src.config.llm_config import LLMConfig, LLMProvider
from src.agents.async_agents import AsyncAgentFactory, run_development_workflow_async
from src.monitoring.logger import AICrewLogger
from src.utils.environment import validate_environment
from src.utils.context7_integration import context7

class ApplicationType(Enum):
    """Supported application types"""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DESKTOP_APP = "desktop_app"
    AI_ML_PROJECT = "ai_ml_project"
    DATA_ANALYTICS = "data_analytics"
    AUTOMATION_SCRIPT = "automation_script"
    MICROSERVICE = "microservice"
    CLI_TOOL = "cli_tool"
    CUSTOM = "custom"

@dataclass
class ProjectRequirements:
    """Project requirements extracted from natural language"""
    name: str
    description: str
    app_type: ApplicationType
    technologies: List[str]
    features: List[str]
    deployment_target: Optional[str] = None
    database_type: Optional[str] = None
    auth_required: bool = False
    api_integrations: Optional[List[str]] = None
    performance_requirements: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.api_integrations is None:
            self.api_integrations = []
        if self.performance_requirements is None:
            self.performance_requirements = []

class NaturalLanguageManager:
    """
    AI Manager that guides users through application development using natural language.
    Acts as an intelligent project manager that asks the right questions and provides guidance.
    """
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.logger = AICrewLogger("natural_language_manager")
        self.conversation_history: List[Dict[str, str]] = []
        
    def welcome_message(self) -> str:
        """Generate a welcoming manager-like message"""
        return """
🎯 Welcome to AICrewDev Natural Language Interface!

I'm your AI Development Manager. I'll help you create applications using only natural language.
Just tell me what you want to build, and I'll guide you through the entire process.

Examples of what you can say:
• "Create a web application for managing tasks with user authentication"
• "Build a mobile app that tracks expenses and generates reports"  
• "I need an API service for processing images with machine learning"
• "Create a data analytics dashboard for sales metrics"

What would you like to build today?
"""

    def parse_natural_language_request(self, user_input: str) -> ProjectRequirements:
        """
        Parse natural language input to extract project requirements.
        This is a simplified implementation - in production, you'd use more sophisticated NLP.
        """
        user_input_lower = user_input.lower()
        
        # Detect application type
        app_type = self._detect_app_type(user_input_lower)
        
        # Extract project name (simplified)
        name = self._extract_project_name(user_input)
        
        # Detect technologies
        technologies = self._detect_technologies(user_input_lower)
        
        # Detect features
        features = self._extract_features(user_input_lower)
        
        # Detect database requirements
        database_type = self._detect_database(user_input_lower)
        
        # Check for authentication requirements
        auth_required = any(auth_keyword in user_input_lower for auth_keyword in 
                          ['auth', 'login', 'user', 'sign in', 'register', 'authentication'])
        
        # Extract API integrations
        api_integrations = self._extract_api_integrations(user_input_lower)
        
        return ProjectRequirements(
            name=name,
            description=user_input,
            app_type=app_type,
            technologies=technologies,
            features=features,
            database_type=database_type,
            auth_required=auth_required,
            api_integrations=api_integrations
        )
    
    def _detect_app_type(self, text: str) -> ApplicationType:
        """Detect application type from natural language"""
        app_type_keywords = {
            ApplicationType.WEB_APP: ['web', 'website', 'webapp', 'browser', 'html', 'react', 'vue', 'angular'],
            ApplicationType.MOBILE_APP: ['mobile', 'app', 'ios', 'android', 'flutter', 'react native'],
            ApplicationType.API_SERVICE: ['api', 'service', 'endpoint', 'rest', 'graphql', 'microservice'],
            ApplicationType.DESKTOP_APP: ['desktop', 'gui', 'tkinter', 'electron', 'qt', 'javafx'],
            ApplicationType.AI_ML_PROJECT: ['ai', 'ml', 'machine learning', 'neural network', 'tensorflow', 'pytorch'],
            ApplicationType.DATA_ANALYTICS: ['analytics', 'dashboard', 'visualization', 'charts', 'metrics', 'reports'],
            ApplicationType.AUTOMATION_SCRIPT: ['automation', 'script', 'bot', 'scraping', 'batch', 'task'],
            ApplicationType.CLI_TOOL: ['cli', 'command line', 'terminal', 'console', 'command'],
        }
        
        for app_type, keywords in app_type_keywords.items():
            if any(keyword in text for keyword in keywords):
                return app_type
        
        return ApplicationType.WEB_APP  # Default to web app
    
    def _extract_project_name(self, text: str) -> str:
        """Extract or generate project name"""
        # Simple implementation - in production, use more sophisticated extraction
        words = text.split()
        if len(words) >= 3:
            # Try to find action + object pattern
            for i, word in enumerate(words):
                if word.lower() in ['create', 'build', 'make', 'develop'] and i + 1 < len(words):
                    return '_'.join(words[i+1:i+3]).replace(' ', '_')
        
        # Fallback to generic name with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return f"aicrewdev_project_{timestamp}"
    
    def _detect_technologies(self, text: str) -> List[str]:
        """Detect technologies mentioned in the request"""
        tech_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node', 'nodejs', 'react', 'vue', 'angular'],
            'typescript': ['typescript', 'ts'],
            'java': ['java', 'spring', 'springboot'],
            'csharp': ['c#', 'csharp', '.net', 'dotnet'],
            'go': ['go', 'golang'],
            'rust': ['rust'],
            'php': ['php', 'laravel', 'symfony'],
            'ruby': ['ruby', 'rails'],
            'swift': ['swift', 'ios'],
            'kotlin': ['kotlin', 'android'],
            'dart': ['dart', 'flutter'],
        }
        
        detected_techs = []
        for tech, keywords in tech_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_techs.append(tech)
        
        # If no specific technology detected, default based on app type
        if not detected_techs:
            if 'web' in text or 'api' in text:
                detected_techs.append('python')  # Default to Python for web/API
            elif 'mobile' in text:
                detected_techs.append('dart')  # Default to Flutter for mobile
        
        return detected_techs or ['python']  # Always return at least Python
    
    def _extract_features(self, text: str) -> List[str]:
        """Extract features from the request"""
        feature_keywords = {
            'authentication': ['auth', 'login', 'register', 'user management'],
            'database': ['database', 'storage', 'data', 'crud'],
            'api': ['api', 'rest', 'graphql', 'endpoint'],
            'real_time': ['real-time', 'realtime', 'live', 'websocket'],
            'file_upload': ['upload', 'file', 'image', 'document'],
            'payments': ['payment', 'stripe', 'paypal', 'billing'],
            'notifications': ['notification', 'email', 'sms', 'push'],
            'search': ['search', 'filter', 'query'],
            'analytics': ['analytics', 'tracking', 'metrics', 'dashboard'],
            'mobile_responsive': ['mobile', 'responsive', 'adaptive'],
        }
        
        detected_features = []
        for feature, keywords in feature_keywords.items():
            if any(keyword in text for keyword in keywords):
                detected_features.append(feature)
        
        return detected_features
    
    def _detect_database(self, text: str) -> Optional[str]:
        """Detect database type from request"""
        db_keywords = {
            'postgresql': ['postgresql', 'postgres', 'psql'],
            'mysql': ['mysql'],
            'mongodb': ['mongodb', 'mongo', 'nosql'],
            'sqlite': ['sqlite'],
            'redis': ['redis', 'cache'],
            'elasticsearch': ['elasticsearch', 'elastic', 'search engine'],
        }
        
        for db_type, keywords in db_keywords.items():
            if any(keyword in text for keyword in keywords):
                return db_type
        
        return 'postgresql'  # Default to PostgreSQL
    
    def _extract_api_integrations(self, text: str) -> List[str]:
        """Extract API integrations from request"""
        api_keywords = {
            'stripe': ['stripe', 'payment'],
            'sendgrid': ['sendgrid', 'email'],
            'twilio': ['twilio', 'sms'],
            'aws': ['aws', 'amazon', 's3'],
            'google': ['google', 'gmail', 'maps'],
            'github': ['github', 'git'],
            'slack': ['slack'],
            'discord': ['discord'],
        }
        
        integrations = []
        for service, keywords in api_keywords.items():
            if any(keyword in text for keyword in keywords):
                integrations.append(service)
        
        return integrations

    def generate_follow_up_questions(self, requirements: ProjectRequirements) -> List[str]:
        """Generate intelligent follow-up questions based on the requirements"""
        questions = []
        
        # Ask about missing critical information
        if not requirements.technologies:
            questions.append("What programming language or framework would you prefer?")
        
        if not requirements.deployment_target:
            questions.append("Where would you like to deploy this application? (AWS, Google Cloud, local, etc.)")
        
        if requirements.app_type == ApplicationType.WEB_APP and not requirements.auth_required:
            questions.append("Do you need user authentication and user management?")
        
        if not requirements.database_type and 'database' in requirements.features:
            questions.append("What type of database would you prefer? (PostgreSQL, MongoDB, MySQL, etc.)")
        
        if requirements.app_type in [ApplicationType.WEB_APP, ApplicationType.API_SERVICE]:
            questions.append("Do you need any third-party API integrations? (Stripe, SendGrid, etc.)")
        
        # Add performance questions for larger applications
        if len(requirements.features) > 3:
            questions.append("What are your expected user load and performance requirements?")
        
        return questions[:3]  # Limit to 3 questions to avoid overwhelming

    def create_context7_prompt(self, requirements: ProjectRequirements) -> str:
        """Create a Context7-enhanced prompt for the development crew"""
        base_prompt = f"""
Create a {requirements.app_type.value} called "{requirements.name}" with the following requirements:

Description: {requirements.description}

Technical Requirements:
- Technologies: {', '.join(requirements.technologies)}
- Features: {', '.join(requirements.features)}
- Database: {requirements.database_type or 'Not specified'}
- Authentication: {'Required' if requirements.auth_required else 'Not required'}
- API Integrations: {', '.join(requirements.api_integrations) if requirements.api_integrations else 'None specified'}

Please provide:
1. Complete project structure and file organization
2. Full implementation with best practices
3. Setup instructions and dependencies
4. Testing strategies
5. Deployment guidelines
"""
        
        # Use Context7 integration to enhance the prompt
        enhanced_prompt = context7.enhance_prompt_with_context7(base_prompt, requirements.technologies)
        return enhanced_prompt

class AICrewDevCLI:
    """
    Main CLI class for natural language application development.
    Orchestrates the entire process from user input to application creation.
    """
    
    def __init__(self):
        self.logger = AICrewLogger("aicrewdev_cli")
        self.manager = None
        self.ai_crew = None
        self.current_requirements: Optional[ProjectRequirements] = None
        
    def setup_environment(self, llm_provider: str = "openai", model_name: str = "gpt-4o-mini") -> bool:
        """Setup the LLM environment and validate dependencies"""
        try:
            # Validate environment
            validate_environment()
            
            # Configure LLM
            provider_enum = LLMProvider(llm_provider.lower())
            llm_config = LLMConfig(
                provider=provider_enum,
                model_name=model_name,
                temperature=0.7
            )
            
            # Initialize components
            self.manager = NaturalLanguageManager(llm_config)
            self.ai_crew = AICrewDev()
            
            self.logger.info("Environment setup completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Environment setup failed: {e}")
            self.logger.error(f"Environment setup failed: {e}")
            return False
    
    async def interactive_session(self):
        """Run an interactive session for application development"""
        if not self.manager:
            print("❌ Manager not initialized")
            return
            
        print(self.manager.welcome_message())
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 What would you like to build? (or 'quit' to exit): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using AICrewDev! Happy coding!")
                    break
                
                if not user_input:
                    continue
                
                # Parse requirements
                print("\n🔍 Analyzing your request...")
                requirements = self.manager.parse_natural_language_request(user_input)
                self.current_requirements = requirements
                
                # Display parsed requirements
                self.display_requirements(requirements)
                
                # Ask follow-up questions if needed
                follow_up_questions = self.manager.generate_follow_up_questions(requirements)
                if follow_up_questions:
                    print("\n❓ I have a few questions to better understand your needs:")
                    for i, question in enumerate(follow_up_questions, 1):
                        print(f"   {i}. {question}")
                    
                    response = input("\n💭 Please provide additional details (or press Enter to continue): ").strip()
                    if response:
                        # Update requirements based on response
                        requirements = self.update_requirements_from_response(requirements, response)
                
                # Confirm before proceeding
                proceed = input("\n✅ Should I proceed with creating this application? (y/n): ").lower()
                if proceed not in ['y', 'yes']:
                    print("⏸️  Okay, let's try something else.")
                    continue
                
                # Create the application
                await self.create_application(requirements)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                self.logger.error(f"Interactive session error: {e}")
                print("🔄 Let's try again...")
    
    def display_requirements(self, requirements: ProjectRequirements):
        """Display parsed requirements in a nice format"""
        print(f"\n📋 Project Requirements Summary:")
        print(f"   🎯 Name: {requirements.name}")
        print(f"   📱 Type: {requirements.app_type.value.replace('_', ' ').title()}")
        print(f"   🛠️  Technologies: {', '.join(requirements.technologies)}")
        print(f"   ⭐ Features: {', '.join(requirements.features) if requirements.features else 'Basic functionality'}")
        print(f"   🗄️  Database: {requirements.database_type or 'Not specified'}")
        print(f"   🔐 Authentication: {'✅ Required' if requirements.auth_required else '❌ Not required'}")
        if requirements.api_integrations:
            print(f"   🔗 API Integrations: {', '.join(requirements.api_integrations)}")
    
    def update_requirements_from_response(self, requirements: ProjectRequirements, response: str) -> ProjectRequirements:
        """Update requirements based on user's follow-up response"""
        if not self.manager:
            return requirements
            
        response_lower = response.lower()
        
        # Update technologies
        new_techs = self.manager._detect_technologies(response_lower)
        if new_techs:
            requirements.technologies.extend([tech for tech in new_techs if tech not in requirements.technologies])
        
        # Update database
        new_db = self.manager._detect_database(response_lower)
        if new_db and not requirements.database_type:
            requirements.database_type = new_db
        
        # Update features
        new_features = self.manager._extract_features(response_lower)
        requirements.features.extend([feature for feature in new_features if feature not in requirements.features])
        
        # Update API integrations
        new_apis = self.manager._extract_api_integrations(response_lower)
        if requirements.api_integrations is None:
            requirements.api_integrations = []
        requirements.api_integrations.extend([api for api in new_apis if api not in requirements.api_integrations])
        
        # Check for deployment target
        if 'aws' in response_lower:
            requirements.deployment_target = 'aws'
        elif 'google' in response_lower or 'gcp' in response_lower:
            requirements.deployment_target = 'gcp'
        elif 'azure' in response_lower:
            requirements.deployment_target = 'azure'
        elif 'heroku' in response_lower:
            requirements.deployment_target = 'heroku'
        elif 'local' in response_lower:
            requirements.deployment_target = 'local'
        
        return requirements
    
    async def create_application(self, requirements: ProjectRequirements):
        """Create the application using AICrewDev with Context7 integration"""
        if not self.manager or not self.ai_crew:
            print("❌ Manager or AI crew not initialized")
            return
            
        print(f"\n🚀 Creating your {requirements.app_type.value.replace('_', ' ')} application...")
        print("⏳ This may take a few minutes. Please wait...")
        
        try:
            # Create Context7-enhanced prompt
            context7_prompt = self.manager.create_context7_prompt(requirements)
            
            # Set up project directory
            project_dir = Path.cwd() / requirements.name
            project_dir.mkdir(exist_ok=True)
            
            print(f"📁 Creating project in: {project_dir}")
            
            # Run the AI development workflow
            print("🤖 AI development team is working...")
            
            # Use the regular AI crew workflow with custom prompt
            # For now, we'll use a simplified approach since the async workflow parameters need adjustment
            
            result = self.ai_crew.run(
                project_type=requirements.app_type.value,
                use_crew_manager=True
            )
            
            if result:
                print(f"\n🎉 Application '{requirements.name}' created successfully!")
                print(f"📂 Project location: {project_dir}")
                
                # Generate additional files
                await self.generate_project_files(requirements, project_dir)
                
                # Provide next steps
                self.provide_next_steps(requirements, project_dir)
                
            else:
                print("❌ Application creation failed")
                
        except Exception as e:
            print(f"❌ Error creating application: {e}")
            self.logger.error(f"Application creation error: {e}")
    
    async def generate_project_files(self, requirements: ProjectRequirements, project_dir: Path):
        """Generate additional project files like README, requirements, etc."""
        try:
            # Generate README.md
            readme_content = self.generate_readme(requirements)
            (project_dir / "README.md").write_text(readme_content)
            
            # Generate requirements.txt or package.json based on technology
            if 'python' in requirements.technologies:
                deps = self.generate_python_dependencies(requirements)
                (project_dir / "requirements.txt").write_text(deps)
            
            if 'javascript' in requirements.technologies or 'typescript' in requirements.technologies:
                package_json = self.generate_package_json(requirements)
                (project_dir / "package.json").write_text(package_json)
            
            # Generate .env.example
            env_example = self.generate_env_example(requirements)
            (project_dir / ".env.example").write_text(env_example)
            
            # Generate .gitignore
            gitignore = self.generate_gitignore(requirements)
            (project_dir / ".gitignore").write_text(gitignore)
            
            print("📝 Generated additional project files (README, dependencies, etc.)")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not generate some project files: {e}")
    
    def generate_readme(self, requirements: ProjectRequirements) -> str:
        """Generate a comprehensive README.md"""
        return f"""# {requirements.name}

{requirements.description}

## 🎯 Project Overview

This is a {requirements.app_type.value.replace('_', ' ')} application created with AICrewDev.

### 🛠️ Technologies Used
{chr(10).join(f'- {tech.title()}' for tech in requirements.technologies)}

### ⭐ Features
{chr(10).join(f'- {feature.replace("_", " ").title()}' for feature in requirements.features)}

### 🗄️ Database
- **Type**: {requirements.database_type or 'Not specified'}

### 🔐 Authentication
- **Required**: {'Yes' if requirements.auth_required else 'No'}

{f'''### 🔗 API Integrations
{chr(10).join(f'- {api.title()}' for api in requirements.api_integrations)}''' if requirements.api_integrations else ''}

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (if using Python)
- Node.js 16+ (if using JavaScript/TypeScript)
- {requirements.database_type.title() if requirements.database_type else 'Database'} server

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd {requirements.name}
```

2. Install dependencies:
```bash
# For Python projects
pip install -r requirements.txt

# For Node.js projects
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
# For Python projects
python main.py

# For Node.js projects
npm start
```

## 📚 Documentation

For more detailed documentation, please refer to the `docs/` directory.

## 🤝 Contributing

This project was created with AICrewDev. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

*Created with ❤️ using AICrewDev Natural Language CLI*
"""

    def generate_python_dependencies(self, requirements: ProjectRequirements) -> str:
        """Generate Python requirements.txt"""
        deps = ["fastapi>=0.104.0", "uvicorn>=0.24.0", "pydantic>=2.5.0"]
        
        if requirements.database_type == 'postgresql':
            deps.extend(["sqlalchemy>=2.0.0", "psycopg2-binary>=2.9.0"])
        elif requirements.database_type == 'mongodb':
            deps.append("motor>=3.3.0")
        elif requirements.database_type == 'mysql':
            deps.extend(["sqlalchemy>=2.0.0", "pymysql>=1.1.0"])
        
        if requirements.auth_required:
            deps.extend(["python-jose>=3.3.0", "passlib>=1.7.0", "bcrypt>=4.1.0"])
        
        if 'stripe' in (requirements.api_integrations or []):
            deps.append("stripe>=7.0.0")
        
        if 'sendgrid' in (requirements.api_integrations or []):
            deps.append("sendgrid>=6.10.0")
        
        deps.extend([
            "python-multipart>=0.0.6",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0"
        ])
        
        return '\n'.join(sorted(deps))
    
    def generate_package_json(self, requirements: ProjectRequirements) -> str:
        """Generate package.json for Node.js projects"""
        package_data = {
            "name": requirements.name.replace('_', '-'),
            "version": "1.0.0",
            "description": requirements.description,
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "test": "jest"
            },
            "dependencies": {
                "express": "^4.18.0",
                "cors": "^2.8.5",
                "helmet": "^7.1.0",
                "dotenv": "^16.3.0"
            },
            "devDependencies": {
                "nodemon": "^3.0.0",
                "jest": "^29.7.0"
            }
        }
        
        # Add database dependencies
        if requirements.database_type == 'postgresql':
            package_data["dependencies"]["pg"] = "^8.11.0"
        elif requirements.database_type == 'mongodb':
            package_data["dependencies"]["mongodb"] = "^6.2.0"
        
        # Add authentication dependencies
        if requirements.auth_required:
            package_data["dependencies"].update({
                "jsonwebtoken": "^9.0.0",
                "bcryptjs": "^2.4.3"
            })
        
        return json.dumps(package_data, indent=2)
    
    def generate_env_example(self, requirements: ProjectRequirements) -> str:
        """Generate .env.example file"""
        env_vars = [
            "# Environment Configuration",
            "NODE_ENV=development",
            "PORT=3000",
            "",
            "# Database Configuration"
        ]
        
        if requirements.database_type == 'postgresql':
            env_vars.extend([
                "DATABASE_URL=postgresql://username:password@localhost:5432/database_name",
                "DB_HOST=localhost",
                "DB_PORT=5432",
                "DB_NAME=database_name",
                "DB_USER=username",
                "DB_PASSWORD=password"
            ])
        elif requirements.database_type == 'mongodb':
            env_vars.append("MONGODB_URI=mongodb://localhost:27017/database_name")
        
        if requirements.auth_required:
            env_vars.extend([
                "",
                "# Authentication",
                "JWT_SECRET=your_jwt_secret_key_here",
                "JWT_EXPIRES_IN=7d"
            ])
        
        for api in (requirements.api_integrations or []):
            env_vars.extend([
                f"",
                f"# {api.title()} Configuration",
                f"{api.upper()}_API_KEY=your_{api}_api_key_here"
            ])
        
        return '\n'.join(env_vars)
    
    def generate_gitignore(self, requirements: ProjectRequirements) -> str:
        """Generate .gitignore file"""
        gitignore_content = [
            "# Environment variables",
            ".env",
            ".env.local",
            ".env.production",
            "",
            "# Dependencies",
            "node_modules/",
            "__pycache__/",
            "*.pyc",
            ".venv/",
            "venv/",
            "",
            "# Build outputs",
            "dist/",
            "build/",
            "*.egg-info/",
            "",
            "# IDE files",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "",
            "# Logs",
            "*.log",
            "logs/",
            "",
            "# Database",
            "*.sqlite",
            "*.db",
            "",
            "# OS generated files",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        return '\n'.join(gitignore_content)
    
    def provide_next_steps(self, requirements: ProjectRequirements, project_dir: Path):
        """Provide helpful next steps to the user"""
        print(f"\n📋 Next Steps:")
        print(f"   1. 📁 Navigate to your project: cd {project_dir}")
        print(f"   2. 📖 Read the README.md for detailed setup instructions")
        print(f"   3. ⚙️  Configure your environment variables in .env")
        
        if 'python' in requirements.technologies:
            print(f"   4. 🐍 Install Python dependencies: pip install -r requirements.txt")
            print(f"   5. ▶️  Run the application: python main.py")
        
        if 'javascript' in requirements.technologies or 'typescript' in requirements.technologies:
            print(f"   4. 📦 Install Node.js dependencies: npm install")
            print(f"   5. ▶️  Run the application: npm start")
        
        if requirements.database_type:
            print(f"   6. 🗄️  Set up your {requirements.database_type} database")
        
        if requirements.auth_required:
            print(f"   7. 🔐 Configure authentication settings")
        
        if requirements.api_integrations:
            print(f"   8. 🔗 Set up API keys for: {', '.join(requirements.api_integrations)}")
        
        print(f"\n💡 Tips:")
        print(f"   • Check the generated code for any TODOs or customization points")
        print(f"   • Run tests to ensure everything is working correctly")
        print(f"   • Consider setting up version control: git init && git add . && git commit -m 'Initial commit'")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="AICrewDev Natural Language CLI - Create applications with natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python natural_language_cli.py
  python natural_language_cli.py --provider ollama --model llama2
  python natural_language_cli.py --provider anthropic --model claude-3-haiku-20240307
        """
    )
    
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "ollama", "groq"],
        default="openai",
        help="LLM provider to use (default: openai)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model name to use (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode with provided prompt"
    )
    
    parser.add_argument(
        "--prompt",
        help="Prompt for non-interactive mode"
    )
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = AICrewDevCLI()
    
    # Setup environment
    if not cli.setup_environment(args.provider, args.model):
        sys.exit(1)
    
    try:
        if args.non_interactive:
            if not args.prompt:
                print("❌ --prompt is required for non-interactive mode")
                sys.exit(1)
            
            if not cli.manager:
                print("❌ Manager not initialized")
                sys.exit(1)
            
            # Non-interactive mode
            requirements = cli.manager.parse_natural_language_request(args.prompt)
            cli.display_requirements(requirements)
            asyncio.run(cli.create_application(requirements))
        else:
            # Interactive mode
            asyncio.run(cli.interactive_session())
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
