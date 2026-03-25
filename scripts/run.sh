#!/bin/bash

# MyFiles to Markdown - Run Script

set -e

echo "================================================"
echo "MyFiles to Markdown - Document Converter"
echo "================================================"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start it with: ollama serve"
    exit 1
fi

echo "✓ Ollama is running"
echo ""

# Check for input files
if [ -z "$(ls -A input 2>/dev/null)" ]; then
    echo "⚠️  No files found in 'input' directory"
    echo ""
    echo "Please add documents to the 'input' directory:"
    echo "  Supported formats: PDF, DOCX, PPTX, XLSX"
    echo ""
    echo "Then run this script again."
    exit 0
fi

echo "Found files to process:"
ls -1 input/
echo ""

# Run converter
echo "Starting conversion..."
echo ""
docker compose up converter

echo ""
echo "================================================"
echo "Conversion Complete!"
echo "================================================"
echo ""
echo "Check the 'output' directory for converted files"
echo ""

