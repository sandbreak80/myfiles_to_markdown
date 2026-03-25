#!/bin/bash
#
# Batch convert all documents in a directory
# Usage: ./convert-batch.sh <directory>
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: No directory specified${NC}"
    echo ""
    echo "Usage: $0 <directory>"
    echo ""
    echo "Examples:"
    echo "  $0 ~/Downloads"
    echo "  $0 ~/Documents/Reports"
    echo ""
    echo "Supported formats: PDF, DOCX, PPTX, HTML"
    exit 1
fi

SOURCE_DIR="$1"

# Check if directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Error: Directory not found: $SOURCE_DIR${NC}"
    exit 1
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}Error: Ollama is not running!${NC}"
    echo "Please start Ollama first"
    exit 1
fi

echo -e "${GREEN}✓${NC} Ollama is running"
echo ""

# Find all supported files
FILES=$(find "$SOURCE_DIR" -type f \( -iname "*.pdf" -o -iname "*.docx" -o -iname "*.pptx" -o -iname "*.html" \))
FILE_COUNT=$(echo "$FILES" | grep -v '^$' | wc -l | tr -d ' ')

if [ "$FILE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}No supported files found in $SOURCE_DIR${NC}"
    echo "Looking for: PDF, DOCX, PPTX, HTML"
    exit 0
fi

echo "Found ${GREEN}$FILE_COUNT${NC} files to convert:"
echo "$FILES" | sed 's/^/  - /'
echo ""

read -p "Continue with batch conversion? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Starting batch conversion..."
echo ""

# Clear input directory
rm -f "$SCRIPT_DIR/input"/*

# Copy files to input
echo "$FILES" | while read file; do
    if [ -n "$file" ]; then
        cp "$file" "$SCRIPT_DIR/input/"
    fi
done

# Run batch conversion
docker compose -f "$SCRIPT_DIR/docker compose.yml" run --rm converter python src/main.py

echo ""
echo -e "${GREEN}✓ Batch conversion complete!${NC}"
echo ""
echo "Converted files: $SCRIPT_DIR/output/"
echo "Attachments: $SCRIPT_DIR/output/attachments/"
echo ""

# Summary
SUCCESS_COUNT=$(ls -1 "$SCRIPT_DIR/output"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "Successfully converted: ${GREEN}$SUCCESS_COUNT${NC} files"

