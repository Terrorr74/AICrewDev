# AICrewDev Natural Language CLI

Create applications using only natural language commands in the terminal! This CLI integrates Context7 for up-to-date documentation and provides an intelligent manager-like experience to guide you through application development.

## 🚀 Quick Start

### Method 1: Interactive Mode (Recommended)
```bash
python natural_language_cli.py
```

### Method 2: Quick Start Script
```bash
python quick_start.py
```

### Method 3: One-liner Command
```bash
python natural_language_cli.py --non-interactive --prompt "Create a web app for managing tasks with user authentication"
```

## 🎯 What You Can Say

The AI manager understands natural language requests like:

### Web Applications
- "Create a web application for managing tasks with user authentication"
- "Build a blog platform with comments and user profiles"
- "Make a dashboard for analytics with charts and real-time data"

### Mobile Apps  
- "Build a mobile app that tracks expenses and generates reports"
- "Create an iOS/Android app for food delivery with GPS tracking"
- "Make a fitness tracking app with workout logging"

### API Services
- "I need an API service for processing images with machine learning"
- "Create a REST API for managing customer data with authentication"
- "Build a GraphQL service for a social media platform"

### Other Applications
- "Create a data analytics dashboard for sales metrics"
- "Build a CLI tool for file management and automation"
- "Make a desktop application for photo editing"

## 🛠️ How It Works

1. **🧠 Natural Language Parsing**: The AI manager analyzes your request and extracts:
   - Application type (web, mobile, API, etc.)
   - Required technologies
   - Features and functionality
   - Database requirements
   - Authentication needs
   - API integrations

2. **❓ Intelligent Questions**: The manager asks follow-up questions to clarify requirements:
   - "What programming language would you prefer?"
   - "Do you need user authentication?"
   - "Where would you like to deploy this?"

3. **📋 Requirement Summary**: Shows you exactly what will be built before proceeding

4. **🤖 AI Development Team**: Creates specialized AI agents (developers, architects, testers) who work together

5. **📚 Context7 Integration**: Fetches the latest documentation and best practices for all technologies

6. **🎉 Complete Application**: Generates:
   - Full source code
   - Project structure
   - Dependencies and requirements
   - README with setup instructions
   - Environment configuration
   - Testing setup

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project directory:

```bash
# Required: Choose your LLM provider
OPENAI_API_KEY=your_openai_api_key
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key
# OR for local models
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Context7 Integration
CONTEXT7_ENABLED=true
```

### LLM Providers

You can use different LLM providers:

```bash
# OpenAI (default)
python natural_language_cli.py --provider openai --model gpt-4o-mini

# Anthropic Claude
python natural_language_cli.py --provider anthropic --model claude-3-haiku-20240307

# Local Ollama
python natural_language_cli.py --provider ollama --model llama2

# Groq (fast inference)
python natural_language_cli.py --provider groq --model mixtral-8x7b-32768
```

## 🎭 Example Session

```
🎯 Welcome to AICrewDev Natural Language Interface!

I'm your AI Development Manager. I'll help you create applications using only natural language.

💬 What would you like to build? 
> Create a web app for task management with user authentication and PostgreSQL

🔍 Analyzing your request...

📋 Project Requirements Summary:
   🎯 Name: task_management_web_app
   📱 Type: Web App
   🛠️  Technologies: python, javascript
   ⭐ Features: authentication, database, task management
   🗄️  Database: postgresql
   🔐 Authentication: ✅ Required

❓ I have a few questions to better understand your needs:
   1. What programming language or framework would you prefer?
   2. Where would you like to deploy this application?
   3. Do you need any third-party API integrations?

💭 Please provide additional details: 
> I prefer Python with FastAPI, deploy on AWS, and integrate with Stripe for payments

✅ Should I proceed with creating this application? (y/n): y

🚀 Creating your web app application...
⏳ This may take a few minutes. Please wait...
📁 Creating project in: ./task_management_web_app
🤖 AI development team is working...

🎉 Application 'task_management_web_app' created successfully!
📂 Project location: ./task_management_web_app
📝 Generated additional project files (README, dependencies, etc.)

📋 Next Steps:
   1. 📁 Navigate to your project: cd task_management_web_app
   2. 📖 Read the README.md for detailed setup instructions
   3. ⚙️  Configure your environment variables in .env
   4. 🐍 Install Python dependencies: pip install -r requirements.txt
   5. ▶️  Run the application: python main.py
   6. 🗄️  Set up your postgresql database
   7. 🔐 Configure authentication settings
   8. 🔗 Set up API keys for: stripe
```

## 🌟 Features

### Smart Technology Detection
- Automatically detects mentioned technologies and frameworks
- Suggests appropriate technology stacks based on requirements
- Handles multiple programming languages and platforms

### Context7 Integration
- Fetches latest documentation and examples
- Ensures current API usage and best practices
- Provides up-to-date dependency versions

### Intelligent Project Generation
- Creates complete project structure
- Generates configuration files (requirements.txt, package.json, .env, etc.)
- Includes setup and deployment instructions
- Adds testing frameworks and examples

### Multiple Application Types
- ✅ Web Applications (React, Vue, Angular, Django, FastAPI)
- ✅ Mobile Apps (Flutter, React Native, iOS, Android)
- ✅ API Services (REST, GraphQL, microservices)
- ✅ Desktop Applications (Electron, Qt, Tkinter)
- ✅ AI/ML Projects (TensorFlow, PyTorch, scikit-learn)
- ✅ Data Analytics (Pandas, Plotly, Streamlit)
- ✅ CLI Tools and Scripts
- ✅ Microservices and containerized apps

## 🔍 Advanced Usage

### Custom Project Types
```bash
python natural_language_cli.py --non-interactive --prompt "Create a microservice for real-time chat with WebSocket support, Redis for caching, and Docker deployment"
```

### Specific Technology Requests
```bash
python natural_language_cli.py --non-interactive --prompt "Build a React Native app with Firebase authentication, Stripe payments, and push notifications"
```

### Complex Business Logic
```bash
python natural_language_cli.py --non-interactive --prompt "Create an e-commerce platform with inventory management, order processing, payment integration, and admin dashboard"
```

## 🤖 AI Development Team

The system creates specialized AI agents that work together:

- **🏗️ Tech Lead**: Designs architecture and makes technology decisions
- **💻 Senior Developer**: Implements core functionality and business logic  
- **🔧 Frontend Developer**: Creates user interfaces and user experience
- **⚙️ Backend Developer**: Builds APIs, database, and server-side logic
- **🧪 Quality Assurance**: Creates tests and ensures code quality
- **📊 DevOps Engineer**: Sets up deployment and infrastructure
- **👥 Project Manager**: Coordinates the team and ensures requirements are met

## 📚 Documentation Integration

With Context7 integration, the AI team has access to:
- Latest API documentation for all technologies
- Current best practices and patterns
- Up-to-date code examples
- Security recommendations
- Performance optimization techniques

## 🛡️ Error Handling

The system handles common issues gracefully:
- Missing environment variables
- Invalid LLM configurations  
- Network connectivity issues
- Dependency conflicts
- Project directory conflicts

## 🎨 Customization

You can customize the behavior by:
- Setting specific LLM models and parameters
- Providing detailed technology preferences
- Specifying deployment targets
- Adding custom requirements in follow-up questions

## 📦 Dependencies

The CLI automatically manages dependencies for generated projects:
- Python: `requirements.txt`
- Node.js: `package.json`
- Environment: `.env.example`
- Git: `.gitignore`
- Documentation: `README.md`

## 🔧 Troubleshooting

### Common Issues

**"Environment setup failed"**
- Check that you have the required API keys set
- Verify your Python version (3.8+ required)
- Ensure internet connectivity for LLM API calls

**"Manager not initialized"**
- Verify your LLM provider configuration
- Check API key validity
- Try a different LLM provider

**"Context7 MCP server not available"**
- This is optional - the system works without it
- To enable: `npm install -g @upstash/context7-mcp`

### Getting Help

1. Check the generated README.md in your project
2. Review the example prompts above
3. Try different LLM providers if one isn't working
4. Use simpler language in your requests

## 🚀 Pro Tips

1. **Be Specific**: Include details about your preferred technologies, deployment targets, and features
2. **Iterate**: Start with a basic request, then add details in follow-up questions
3. **Use Examples**: Reference existing applications or patterns you want to follow
4. **Consider Scale**: Mention expected user load and performance requirements
5. **Think Integration**: Include third-party services and APIs you'll need

## 📄 License

This project is part of AICrewDev and follows the same MIT license.

---

**Create anything with just natural language!** 🎉
