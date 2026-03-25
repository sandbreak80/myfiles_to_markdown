# CLI Usage Guide

The converter works as a **command-line tool** - you pass it a file, and it returns a markdown file.

## Quick Start

### Convert a Single File

**Linux/Mac:**
```bash
./convert.sh document.pdf
```

**Windows:**
```cmd
convert.bat document.pdf
```

The markdown file will be created in `output/document.md`

### Custom Output Location

**Linux/Mac:**
```bash
./convert.sh document.pdf ~/Documents/converted.md
```

**Windows:**
```cmd
convert.bat document.pdf C:\Documents\converted.md
```

## Usage Patterns

### 1. Convert from Anywhere

```bash
# Convert a file from any location
./convert.sh ~/Documents/report.pdf

# Convert with custom output
./convert.sh ~/Documents/report.pdf ~/Obsidian/MyVault/report.md
```

### 2. Direct Docker Usage

If you prefer using Docker directly:

```bash
# Single file conversion
docker run --rm \
  --network myfiles_to_markdown_myfiles_network \
  -v "/path/to/file:/app/input:ro" \
  -v "./output:/app/output" \
  -v "./config:/app/config:ro" \
  -v "./logs:/app/logs" \
  -e OLLAMA_HOST=http://ollama:11434 \
  myfiles_to_markdown-converter \
  python src/main.py /app/input/document.pdf
```

### 3. Batch Processing Directory

Process all files in a directory:

```bash
# Copy files to input/
cp ~/Documents/*.pdf input/

# Run batch conversion
docker-compose up converter
```

## Command-Line Arguments

The Python application supports these arguments:

```bash
python src/main.py [input_file] [-o OUTPUT] [-c CONFIG]
```

### Arguments

- `input_file` - Path to input file (optional, if not provided processes input/ directory)
- `-o, --output` - Custom output file path
- `-c, --config` - Path to config file (default: `/app/config/config.yaml`)

### Examples Inside Container

```bash
# Convert specific file
python src/main.py /app/input/document.pdf

# Convert with custom output
python src/main.py /app/input/document.pdf -o /app/output/converted.md

# Batch mode (no file specified)
python src/main.py
```

## Wrapper Scripts

### convert.sh (Linux/Mac)

The `convert.sh` script handles:
- Starting Ollama if not running
- Building container if needed
- Volume mounting
- Path resolution
- Error handling

**Features:**
- ✅ Accepts files from anywhere on your system
- ✅ Automatically resolves paths
- ✅ Shows progress and results
- ✅ Handles both relative and absolute paths

### convert.bat (Windows)

Windows equivalent with same features.

## Output

### Generated Files

When you convert `document.pdf`, you get:

```
output/
├── document.md                    # Converted markdown
└── attachments/
    ├── document_img_001.png      # Extracted images
    ├── document_img_002.png
    └── ...
```

### Markdown Format

```markdown
---
title: "Document Title"
source_file: "document.pdf"
processed: "2025-11-10 14:30:00"
ai_summary: "AI-generated summary..."
tags:
  - keyword1
  - keyword2
---

> [!summary] AI Summary
> Concise summary of the document...

## Content

Your document content here...

## Images

![[attachments/document_img_001.png]]
**Description:** AI-generated image description
```

## Integration Examples

### Shell Script Automation

```bash
#!/bin/bash
# Convert all PDFs in a directory

for file in ~/Documents/*.pdf; do
    echo "Converting: $file"
    ./convert.sh "$file"
done
```

### Direct to Obsidian

```bash
# Convert and save directly to Obsidian vault
./convert.sh report.pdf ~/Obsidian/MyVault/Converted/report.md
```

### Python Integration

```python
import subprocess

def convert_document(input_file, output_file=None):
    cmd = ['./convert.sh', input_file]
    if output_file:
        cmd.append(output_file)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# Usage
convert_document('document.pdf')
convert_document('report.docx', 'output/report.md')
```

### Node.js Integration

```javascript
const { execSync } = require('child_process');

function convertDocument(inputFile, outputFile = null) {
    const cmd = outputFile 
        ? `./convert.sh "${inputFile}" "${outputFile}"`
        : `./convert.sh "${inputFile}"`;
    
    try {
        execSync(cmd, { stdio: 'inherit' });
        return true;
    } catch (error) {
        return false;
    }
}

// Usage
convertDocument('document.pdf');
```

## Troubleshooting

### "Ollama not running"

The script automatically starts Ollama, but if you see errors:

```bash
# Manually start Ollama
docker-compose up -d ollama

# Wait for it to be ready
docker-compose logs -f ollama
```

### "Container not found"

Build the container:

```bash
docker-compose build converter
```

### "File not found"

Ensure you're using the full path or correct relative path:

```bash
# Absolute path
./convert.sh /home/user/Documents/file.pdf

# Relative path from project root
./convert.sh ../Documents/file.pdf

# Check file exists
ls -la /path/to/file.pdf
```

### Permission Errors

On Linux/Mac, ensure scripts are executable:

```bash
chmod +x convert.sh
chmod +x scripts/*.sh
```

## Performance Tips

### First Run
- Downloads AI model (~2-3 GB)
- Takes 5-15 minutes
- Subsequent runs are much faster

### Conversion Speed
- Small PDF (10 pages): ~30-60 seconds
- Large PDF (100 pages): ~3-5 minutes
- DOCX/PPTX: ~20-40 seconds

### Optimization
- Disable AI: Edit `config/config.yaml`
  ```yaml
  processing:
    ai:
      generate_summary: false
      generate_tags: false
  ```
- Use faster model: `llama3.2:3b` instead of `llama3.2:latest`

## Advanced Usage

### Custom Configuration

Create a custom config file:

```bash
cp config/config.yaml my-config.yaml
# Edit my-config.yaml

# Use custom config
docker run ... myfiles_to_markdown-converter \
  python src/main.py input.pdf -c /app/config/my-config.yaml
```

### Multiple Files with Custom Names

```bash
#!/bin/bash
# Convert and rename

./convert.sh report.pdf output/2025-11-10-quarterly-report.md
./convert.sh presentation.pptx output/2025-11-10-sales-deck.md
```

### API-Style Usage

Create a simple web wrapper:

```python
# app.py
from flask import Flask, request, send_file
import subprocess
import tempfile

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
    
    file.save(temp_input.name)
    
    subprocess.run(['./convert.sh', temp_input.name, temp_output.name])
    
    return send_file(temp_output.name, as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000)
```

## Best Practices

1. **Test First**: Try with a small file first
2. **Check Output**: Review generated markdown for quality
3. **Backup Originals**: Keep original files safe
4. **Organize Output**: Use subdirectories for different projects
5. **Monitor Logs**: Check `logs/` if something goes wrong
6. **Resource Aware**: Large files need more memory/time

---

For more details, see:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [USAGE.md](USAGE.md) - Detailed usage examples

