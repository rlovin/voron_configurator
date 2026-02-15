#!/bin/bash

# Voron Configurator Startup Script
# Uses uv for dependency management

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Run the Flask application
echo "Starting Voron Configurator on port 3000..."
uv run python app.py