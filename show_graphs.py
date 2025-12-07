#!/usr/bin/env python3
"""
Generate poster graph - wrapper that fixes imports
"""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Now import and run
from generate_poster_graph import generate_poster_graph

if __name__ == "__main__":
    scope = sys.argv[1] if len(sys.argv) > 1 else None
    generate_poster_graph(scope)
