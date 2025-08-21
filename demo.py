#!/usr/bin/env python3
"""
AICrewDev Natural Language CLI Demo

A demonstration of the natural language interface for creating applications.
This shows how to use the system with various example prompts.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_demo():
    """Run a demonstration of the natural language CLI"""
    
    print("🎯 AICrewDev Natural Language CLI Demo")
    print("=" * 50)
    
    # Check if the CLI script exists
    cli_script = Path("natural_language_cli.py")
    if not cli_script.exists():
        print("❌ natural_language_cli.py not found!")
        print("Make sure you're running this from the AICrewDev directory.")
        return
    
    # Example prompts to demonstrate
    example_prompts = [
        "Create a simple web app for task management with user authentication",
        "Build a REST API for a blog platform with PostgreSQL database",
        "Make a mobile app for expense tracking with charts and reports",
        "Create a data analytics dashboard with real-time metrics",
        "Build a CLI tool for file organization and automation"
    ]
    
    print("\n🚀 Available Demo Prompts:")
    for i, prompt in enumerate(example_prompts, 1):
        print(f"   {i}. {prompt}")
    
    print("\n💡 You can also:")
    print("   6. Enter your own custom prompt")
    print("   7. Run interactive mode")
    print("   8. Exit")
    
    while True:
        try:
            choice = input("\n🔢 Choose an option (1-8): ").strip()
            
            if choice == "8":
                print("👋 Thanks for trying the demo!")
                break
            elif choice == "7":
                print("\n🎯 Starting interactive mode...")
                run_interactive_mode()
                break
            elif choice == "6":
                custom_prompt = input("\n💭 Enter your custom prompt: ").strip()
                if custom_prompt:
                    run_with_prompt(custom_prompt)
                else:
                    print("❌ No prompt provided.")
            elif choice in ["1", "2", "3", "4", "5"]:
                index = int(choice) - 1
                prompt = example_prompts[index]
                print(f"\n🎯 Using prompt: {prompt}")
                
                # Ask for confirmation
                confirm = input("📋 Run this demo? (y/n): ").lower()
                if confirm in ['y', 'yes']:
                    run_with_prompt(prompt)
                else:
                    print("⏸️  Demo cancelled.")
            else:
                print("❌ Invalid choice. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def run_with_prompt(prompt: str):
    """Run the CLI with a specific prompt"""
    print(f"\n🚀 Running AICrewDev with prompt:")
    print(f"💬 '{prompt}'")
    print("\n⏳ This will show you how the system parses and handles your request...")
    print("📝 Note: This is a demo - it may not create actual files without proper API keys.")
    
    # For demo purposes, we'll run in non-interactive mode
    cmd = [
        sys.executable, 
        "natural_language_cli.py", 
        "--non-interactive", 
        "--prompt", 
        prompt
    ]
    
    try:
        print("\n" + "="*60)
        subprocess.run(cmd)
        print("="*60)
        print("✅ Demo completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
    except KeyboardInterrupt:
        print("\n⏸️  Demo interrupted by user.")

def run_interactive_mode():
    """Run the CLI in interactive mode"""
    print("\n🎯 Starting AICrewDev Interactive Mode...")
    print("💡 You can type natural language requests and the AI manager will help you!")
    print("📝 Note: Make sure you have API keys configured for full functionality.")
    
    cmd = [sys.executable, "natural_language_cli.py"]
    
    try:
        subprocess.run(cmd)
    except subprocess.CalledProcessError as e:
        print(f"❌ Interactive mode failed: {e}")
    except KeyboardInterrupt:
        print("\n⏸️  Interactive mode interrupted.")

def main():
    """Main entry point"""
    print("🎨 Welcome to the AICrewDev Natural Language CLI Demo!")
    print("\nThis demo shows how you can create applications using only natural language.")
    print("The AI development manager will parse your requests and guide you through the process.")
    
    # Check requirements
    print("\n🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return
    print("✅ Python version OK")
    
    # Check if the main CLI exists
    if not Path("natural_language_cli.py").exists():
        print("❌ natural_language_cli.py not found!")
        print("Make sure you're in the AICrewDev directory.")
        return
    print("✅ CLI script found")
    
    print("\n🎯 Everything looks good! Let's start the demo.")
    
    # Run the demo
    run_demo()

if __name__ == "__main__":
    main()
