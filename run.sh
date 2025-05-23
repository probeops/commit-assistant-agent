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

./commit_assistant/direct_commit.py "$@"
