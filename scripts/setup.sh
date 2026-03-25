#!/bin/bash

# MyFiles to Markdown - Setup Script

set -e

echo "================================================"
echo "MyFiles to Markdown - Setup"
echo "================================================"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker found"

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install it first."
    echo "   Visit: https://ollama.com/download"
    exit 1
fi

echo "✓ Ollama found"

# Check Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start it with: ollama serve"
    exit 1
fi

echo "✓ Ollama is running"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p input output logs config

echo "✓ Directories created"
echo ""

# Pull default model
echo "Pulling Ollama text model (this may take a few minutes)..."
ollama pull llama3.2:latest

echo ""
echo "✓ Text model downloaded"
echo ""

# Optional: Pull vision model
read -p "Do you want to pull the vision model for image descriptions? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pulling vision model..."
    ollama pull llava:7b
    echo "✓ Vision model downloaded"
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Quick Start:"
echo "  1. Place your documents in the 'input' directory"
echo "  2. Run: docker-compose up converter"
echo "  3. Find converted files in the 'output' directory"
echo ""
echo "For more information, see README.md"
echo ""

