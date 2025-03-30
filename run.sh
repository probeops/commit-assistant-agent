#!/bin/bash

# Check if venv exists
if [ ! -d "./venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
else
    source ./venv/bin/activate
fi

# Check for direct API usage
if [ "$1" == "direct" ]; then
    # Run direct API implementation
    shift  # Remove the "direct" argument
    ./direct_commit.py "$@"
else
    # Run the script with smolagents
    python caa.py "$@"
fi
