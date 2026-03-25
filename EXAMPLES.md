# Usage Examples

Real-world examples of using the document converter.

## Basic Usage

### Convert a Single PDF

```bash
./convert.sh document.pdf
```

**Output:**
- `output/document.md` - Converted markdown
- `output/attachments/document_img_*.png` - Extracted images

### Convert a Word Document

```bash
./convert.sh report.docx
```

Same output pattern as PDF.

### Convert a PowerPoint

```bash
./convert.sh presentation.pptx
```

## Custom Output Locations

### Save to Specific Directory

```bash
./convert.sh document.pdf ~/Documents/converted/document.md
```

### Save to Obsidian Vault

```bash
./convert.sh meeting-notes.docx ~/Obsidian/MyVault/Meetings/2025-11-10.md
```

### Save with Custom Name

```bash
./convert.sh "Q3 Report.pdf" output/quarterly-report-2025-q3.md
```

## Batch Processing

### Convert Multiple Files

```bash
# Copy all PDFs to input/
cp ~/Documents/*.pdf input/

# Convert all at once
docker-compose up converter
```

### Convert by Type

```bash
# PDFs only
cp ~/Documents/Reports/*.pdf input/

# Word docs only
cp ~/Documents/Drafts/*.docx input/

# Everything
cp ~/Documents/*.{pdf,docx,pptx} input/
```

## Automation Examples

### Shell Script - Convert Folder

```bash
#!/bin/bash
# convert-folder.sh - Convert all documents in a folder

FOLDER="$1"

if [ -z "$FOLDER" ]; then
    echo "Usage: $0 <folder>"
    exit 1
fi

for file in "$FOLDER"/*.{pdf,docx,pptx}; do
    if [ -f "$file" ]; then
        echo "Converting: $file"
        ./convert.sh "$file"
    fi
done

echo "Done! Check output/ directory"
```

**Usage:**
```bash
chmod +x convert-folder.sh
./convert-folder.sh ~/Documents/Reports
```

### Python Script - Automated Conversion

```python
#!/usr/bin/env python3
"""
auto-convert.py - Watch folder and convert new documents
"""

import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DocumentHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        if path.suffix.lower() in ['.pdf', '.docx', '.pptx']:
            print(f"New file detected: {path}")
            subprocess.run(['./convert.sh', str(path)])

if __name__ == "__main__":
    watch_path = Path.home() / "Documents" / "ToConvert"
    watch_path.mkdir(exist_ok=True)
    
    event_handler = DocumentHandler()
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=False)
    observer.start()
    
    print(f"Watching: {watch_path}")
    print("Drop files here to convert automatically...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

**Usage:**
```bash
# Install watchdog
pip install watchdog

# Run watcher
python3 auto-convert.py

# Drop files in ~/Documents/ToConvert/
```

### Make Commands

```bash
# Convert single file
make convert FILE=document.pdf

# Convert with relative path
make convert FILE=../Downloads/report.docx

# Convert with absolute path
make convert FILE=/home/user/document.pdf
```

## Integration Examples

### Obsidian Daily Note

Convert meeting notes directly to today's daily note:

```bash
#!/bin/bash
# convert-to-daily.sh

TODAY=$(date +%Y-%m-%d)
VAULT="$HOME/Obsidian/MyVault"
DAILY="$VAULT/Daily Notes/$TODAY.md"

./convert.sh "$1" "$DAILY"

echo "Converted to daily note: $DAILY"
```

**Usage:**
```bash
./convert-to-daily.sh meeting-recording.pdf
```

### Email Attachment Workflow

```bash
#!/bin/bash
# Convert email attachments

DOWNLOAD_DIR="$HOME/Downloads"
VAULT="$HOME/Obsidian/MyVault/Inbox"

# Find PDFs downloaded today
find "$DOWNLOAD_DIR" -name "*.pdf" -mtime -1 | while read file; do
    echo "Converting: $file"
    basename=$(basename "$file" .pdf)
    ./convert.sh "$file" "$VAULT/$basename.md"
done
```

### Dropbox Auto-Convert

```bash
#!/bin/bash
# Monitor Dropbox folder for new documents

DROPBOX="$HOME/Dropbox/ToConvert"
OUTPUT="$HOME/Dropbox/Converted"

inotifywait -m -e create "$DROPBOX" --format '%f' | while read file; do
    if [[ $file == *.pdf ]] || [[ $file == *.docx ]]; then
        echo "New file: $file"
        ./convert.sh "$DROPBOX/$file" "$OUTPUT/${file%.*}.md"
    fi
done
```

## Advanced Configuration Examples

### High Quality Mode

Edit `config/config.yaml`:

```yaml
ollama:
  model: "llama3.2:latest"  # Larger model
  temperature: 0.5

processing:
  ocr:
    enabled: true
    language: "eng"
  
  ai:
    generate_summary: true
    generate_tags: true
    max_tags: 15
    describe_images: true
```

### Fast Mode (No AI)

```yaml
processing:
  ai:
    generate_summary: false
    generate_tags: false
    describe_images: false
```

### Multi-Language OCR

```yaml
processing:
  ocr:
    enabled: true
    language: "eng+fra+deu+spa"  # English, French, German, Spanish
```

## Specialized Workflows

### Academic Papers

```bash
# Convert research papers with detailed tagging
./convert.sh paper.pdf ~/Research/Papers/2025/smith-et-al-ml.md
```

Config for academic papers:

```yaml
processing:
  ai:
    generate_summary: true
    max_tags: 20  # More tags for research papers
    
obsidian:
  frontmatter:
    add_ai_summary: true
    add_ai_tags: true
    # Tags will include research topics
```

### Legal Documents

```bash
# Convert legal documents
./convert.sh contract.pdf ~/Legal/Contracts/vendor-agreement-2025.md
```

### Meeting Minutes

```bash
# Convert meeting recordings/transcripts
./convert.sh "Team Meeting 2025-11-10.docx" \
    ~/Obsidian/Meetings/2025-11-10-team.md
```

### Book Chapters

```bash
# Convert book chapters
for chapter in ~/Books/MyBook/Chapter*.docx; do
    num=$(basename "$chapter" .docx | sed 's/Chapter //')
    ./convert.sh "$chapter" ~/Writing/MyBook/chapters/$num.md
done
```

## Batch Operations

### Convert All Documents in Project

```bash
#!/bin/bash
# convert-project.sh - Convert all documents in a project

PROJECT="$1"
OUTPUT="$PROJECT/markdown"

mkdir -p "$OUTPUT"

find "$PROJECT" -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.pptx" \) | while read file; do
    relative=$(realpath --relative-to="$PROJECT" "$file")
    output_path="$OUTPUT/${relative%.*}.md"
    output_dir=$(dirname "$output_path")
    
    mkdir -p "$output_dir"
    
    echo "Converting: $relative"
    ./convert.sh "$file" "$output_path"
done
```

**Usage:**
```bash
./convert-project.sh ~/Projects/ClientWork
```

### Parallel Conversion

```bash
#!/bin/bash
# parallel-convert.sh - Convert multiple files in parallel

parallel -j 4 ./convert.sh ::: input/*.pdf
```

Requires GNU parallel: `sudo apt-get install parallel`

## Output Customization

### Organize by Date

```bash
#!/bin/bash
# organize-by-date.sh

TODAY=$(date +%Y-%m-%d)
OUTPUT_DIR="output/$TODAY"

mkdir -p "$OUTPUT_DIR"

./convert.sh "$1"

# Move output to date folder
mv output/*.md "$OUTPUT_DIR/"
```

### Organize by Type

```bash
#!/bin/bash

FILE="$1"
EXT="${FILE##*.}"

case $EXT in
    pdf)
        OUTPUT="output/pdfs/"
        ;;
    docx)
        OUTPUT="output/documents/"
        ;;
    pptx)
        OUTPUT="output/presentations/"
        ;;
esac

mkdir -p "$OUTPUT"
./convert.sh "$FILE" "$OUTPUT/$(basename "${FILE%.*}").md"
```

## Troubleshooting Examples

### Check Conversion Quality

```bash
# Convert and immediately view
./convert.sh document.pdf && cat output/document.md | less
```

### Compare Original vs Converted

```bash
# Extract text from original
pdftotext original.pdf original.txt

# Convert with our tool
./convert.sh original.pdf

# Compare
diff original.txt <(sed '/^---$/,/^---$/d' output/original.md)
```

### Test AI Quality

```bash
# Convert without AI
# Edit config: ai.generate_summary = false
./convert.sh doc.pdf

# Convert with AI
# Edit config: ai.generate_summary = true
./convert.sh doc.pdf

# Compare outputs
```

## Real-World Complete Example

```bash
#!/bin/bash
# complete-workflow.sh - Full conversion workflow

set -e

INPUT="$1"
PROJECT="QuarterlyReport"

# Create project structure
mkdir -p ~/Obsidian/Projects/$PROJECT/{source,converted,attachments}

# Copy source
cp "$INPUT" ~/Obsidian/Projects/$PROJECT/source/

# Convert
./convert.sh "$INPUT" ~/Obsidian/Projects/$PROJECT/converted/report.md

# Move attachments
if [ -d "output/attachments" ]; then
    mv output/attachments/* ~/Obsidian/Projects/$PROJECT/attachments/
fi

# Open in Obsidian
echo "Conversion complete!"
echo "File: ~/Obsidian/Projects/$PROJECT/converted/report.md"
```

---

These examples show the flexibility of the converter. Mix and match patterns to fit your workflow!

For more information:
- [CLI_USAGE.md](CLI_USAGE.md) - Detailed CLI reference
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup

