#!/usr/bin/env python3
"""
Build script for BSM application.
Handles dependency installation and application building.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running: {cmd}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running {cmd}: {e}")
        return False

def main():
    """Main build process."""
    project_root = Path(__file__).parent
    print(f"Building BSM application in: {project_root}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher required")
        return False
    
    print(f"Using Python {sys.version}")
    
    # Install/upgrade pip
    print("Upgrading pip...")
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", project_root):
        print("Warning: Failed to upgrade pip")
    
    # Install basic dependencies first
    print("Installing basic dependencies...")
    basic_deps = [
        "PyQt6>=6.6.0",
        "pynput>=1.7.6", 
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "cryptography>=41.0.0"
    ]
    
    for dep in basic_deps:
        print(f"Installing {dep}...")
        if not run_command(f"{sys.executable} -m pip install '{dep}'", project_root):
            print(f"Warning: Failed to install {dep}")
    
    # Try to install optional dependencies
    optional_deps = [
        "opencv-python>=4.8.0",
        "numpy>=1.24.0", 
        "aiosqlite>=0.19.0",
        "aiofiles>=23.0.0",
        "pytesseract>=0.3.10"
    ]
    
    for dep in optional_deps:
        print(f"Installing optional {dep}...")
        if not run_command(f"{sys.executable} -m pip install '{dep}'", project_root):
            print(f"Warning: Failed to install optional {dep}")
    
    print("Build complete! You can now run the application.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
