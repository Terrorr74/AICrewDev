#!/usr/bin/env python3
"""
AICrewDev Quick Start Script

A simple script to quickly start creating applications with natural language.
This script makes it easy to run AICrewDev from anywhere.

Usage:
    ./quick_start.py
    python quick_start.py "Create a web app for task management"
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point for quick start"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Path to the main CLI script
    cli_script = script_dir / "natural_language_cli.py"
    
    if not cli_script.exists():
        print("❌ natural_language_cli.py not found!")
        print("Make sure you're running this from the AICrewDev directory.")
        sys.exit(1)
    
    # Check if user provided a prompt as argument
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        cmd = [sys.executable, str(cli_script), "--non-interactive", "--prompt", prompt]
    else:
        cmd = [sys.executable, str(cli_script)]
    
    try:
        # Run the CLI script
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running AICrewDev CLI: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
