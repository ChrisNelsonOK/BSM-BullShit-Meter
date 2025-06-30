#!/usr/bin/env python3
"""
BSM Launch Script
Simple script to run BSM from the project directory
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    from bsm.main import main
    main()