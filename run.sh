#!/bin/bash

echo "===================================="
echo "Agent-Driven TODO Executor"
echo "===================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate venv
source venv/bin/activate

# Check if requirements installed
if ! pip show openai > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Run the agent
echo "Starting agent..."
echo ""
python main.py

