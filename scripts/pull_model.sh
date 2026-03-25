#!/bin/bash

# MyFiles to Markdown - Pull Model Script

set -e

MODEL="${1:-llama3.2:latest}"

echo "================================================"
echo "Pulling Ollama Model: $MODEL"
echo "================================================"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start it with: ollama serve"
    exit 1
fi

echo "Pulling model (this may take several minutes)..."
ollama pull "$MODEL"

echo ""
echo "✓ Model $MODEL pulled successfully"
echo ""
echo "To use this model, update config/config.yaml:"
echo "  ollama:"
echo "    model: \"$MODEL\""
echo ""

