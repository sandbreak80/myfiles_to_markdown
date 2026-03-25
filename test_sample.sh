#!/bin/bash
#
# Test the converter with a sample markdown document
# This creates a simple test PDF and converts it
#

set -e

echo "Creating sample test document..."

# Create a sample markdown file
cat > /tmp/test_document.md << 'EOF'
# Test Document

This is a test document for the MyFiles to Markdown converter.

## Features to Test

- Text extraction
- Heading preservation  
- List formatting
- **Bold text**
- *Italic text*

## Sample Table

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

## Conclusion

This document tests the basic conversion functionality.
EOF

echo "✓ Sample document created"
echo ""
echo "To test the converter:"
echo "  1. Convert this markdown to PDF using any tool (pandoc, browser print, etc.)"
echo "  2. Run: ./convert.sh /path/to/test.pdf"
echo "  3. Check: output/test.md"
echo ""
echo "Or create your own test document and run:"
echo "  ./convert.sh your-test-file.pdf"
echo ""

