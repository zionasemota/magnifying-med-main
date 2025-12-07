#!/bin/bash
# Wrapper script to generate poster graph with proper Python path

cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the script with all arguments
python3 -c "
import sys
sys.path.insert(0, '.')
from generate_poster_graph import generate_poster_graph

if len(sys.argv) > 1:
    generate_poster_graph(sys.argv[1])
else:
    generate_poster_graph()
" "$@"

