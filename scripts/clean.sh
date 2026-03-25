#!/bin/bash

# MyFiles to Markdown - Clean Script

set -e

echo "================================================"
echo "MyFiles to Markdown - Cleanup"
echo "================================================"
echo ""

echo "This will:"
echo "  - Stop all containers"
echo "  - Remove processed files from output"
echo "  - Clear logs"
echo ""

read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Stop containers
echo "Stopping containers..."
docker compose down

# Clean output (keep .gitkeep)
echo "Cleaning output directory..."
find output -type f ! -name '.gitkeep' -delete
find output -type d ! -name 'output' -exec rm -rf {} + 2>/dev/null || true

# Clean logs
echo "Cleaning logs..."
find logs -type f ! -name '.gitkeep' -delete

echo ""
echo "✓ Cleanup complete"
echo ""

