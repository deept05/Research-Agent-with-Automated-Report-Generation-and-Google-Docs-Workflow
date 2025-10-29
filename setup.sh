#!/bin/bash

# Setup script for LangChain Research Agent
# This script automates the initial setup process

echo "========================================="
echo "LangChain Research Agent Setup"
echo "========================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directory structure..."
mkdir -p logs
mkdir -p docs
mkdir -p research_outputs
mkdir -p tests

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created. Please edit it with your credentials."
else
    echo ".env file already exists"
fi

# Check for Google credentials
if [ ! -f "service-account.json" ]; then
    echo "⚠️  Warning: Google service account credentials not found"
    echo "Please download your service account JSON and place it in the project root"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and credentials"
echo "2. Place your Google service account JSON in the project root"
echo "3. Run the application: python app/main.py"
echo ""
echo "For more information, see README.md"
echo ""