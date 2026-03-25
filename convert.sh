#!/bin/bash
#
# Convert a single document file to markdown
# Usage: ./convert.sh <input-file> [output-file]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: No input file specified${NC}"
    echo ""
    echo "Usage: $0 <input-file> [output-file]"
    echo ""
    echo "Examples:"
    echo "  $0 document.pdf"
    echo "  $0 document.pdf output/document.md"
    echo "  $0 ~/Documents/report.docx"
    echo ""
    echo "Supported formats: PDF, DOCX, PPTX, HTML"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-}"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}Error: File not found: $INPUT_FILE${NC}"
    exit 1
fi

# Get absolute path
INPUT_FILE="$(cd "$(dirname "$INPUT_FILE")" && pwd)/$(basename "$INPUT_FILE")"
INPUT_DIR="$(dirname "$INPUT_FILE")"
INPUT_BASENAME="$(basename "$INPUT_FILE")"

# Check if Ollama is accessible (either on host or in Docker)
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}Error: Ollama is not running!${NC}"
    echo "Please start Ollama first:"
    echo "  - macOS: Run Ollama app or 'ollama serve'"
    echo "  - Or: docker compose up -d ollama"
    exit 1
fi

echo -e "${GREEN}✓${NC} Ollama is running"

# Build container if needed
if ! docker images | grep -q myfiles_to_markdown-converter; then
    echo -e "${YELLOW}Building converter container (first time only)...${NC}"
    docker compose -f "$SCRIPT_DIR/docker compose.yml" build converter
fi

echo ""
echo -e "${GREEN}Converting:${NC} $INPUT_FILE"
echo ""

# Run conversion
if [ -n "$OUTPUT_FILE" ]; then
    # With custom output path
    OUTPUT_FILE="$(cd "$(dirname "$OUTPUT_FILE")" && pwd)/$(basename "$OUTPUT_FILE")"
    OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
    
    docker run --rm \
        --add-host=host.docker.internal:host-gateway \
        -v "$INPUT_DIR:/app/input:ro" \
        -v "$OUTPUT_DIR:/app/output" \
        -v "$SCRIPT_DIR/config:/app/config:ro" \
        -v "$SCRIPT_DIR/logs:/app/logs" \
        -e OLLAMA_HOST=http://host.docker.internal:11434 \
        myfiles_to_markdown-converter \
        python src/main.py "/app/input/$INPUT_BASENAME" -o "/app/output/$(basename "$OUTPUT_FILE")"
    
    echo ""
    echo -e "${GREEN}✓ Success!${NC}"
    echo -e "Output: ${GREEN}$OUTPUT_FILE${NC}"
else
    # Default output location
    docker run --rm \
        --add-host=host.docker.internal:host-gateway \
        -v "$INPUT_DIR:/app/input:ro" \
        -v "$SCRIPT_DIR/output:/app/output" \
        -v "$SCRIPT_DIR/config:/app/config:ro" \
        -v "$SCRIPT_DIR/logs:/app/logs" \
        -e OLLAMA_HOST=http://host.docker.internal:11434 \
        myfiles_to_markdown-converter \
        python src/main.py "/app/input/$INPUT_BASENAME"
    
    OUTPUT_NAME="${INPUT_BASENAME%.*}.md"
    OUTPUT_FILE="$SCRIPT_DIR/output/$OUTPUT_NAME"
    
    echo ""
    echo -e "${GREEN}✓ Success!${NC}"
    echo -e "Output: ${GREEN}$OUTPUT_FILE${NC}"
fi

# Check for attachments
ATTACHMENTS_DIR="$SCRIPT_DIR/output/attachments"
if [ -d "$ATTACHMENTS_DIR" ] && [ "$(ls -A "$ATTACHMENTS_DIR" 2>/dev/null)" ]; then
    IMAGE_COUNT=$(find "$ATTACHMENTS_DIR" -type f -name "${INPUT_BASENAME%.*}_img_*" 2>/dev/null | wc -l)
    if [ $IMAGE_COUNT -gt 0 ]; then
        echo -e "Images: ${GREEN}$IMAGE_COUNT extracted${NC} → $ATTACHMENTS_DIR"
    fi
fi

echo ""

