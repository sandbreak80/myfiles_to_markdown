# MyFiles to Markdown

Convert your office documents and PDFs to Obsidian-compatible markdown with AI enhancement, all running locally using Docker and Ollama.

## 🎯 Features

- **Document Conversion with Docling**: Advanced document understanding using [IBM's Docling library](https://github.com/DS4SD/docling)
  - PDF, DOCX, PPTX, HTML support
  - Superior table extraction and formatting (handles complex tables!)
  - Layout-aware processing (understands document structure)
  - Built-in OCR integration
  - Production-ready conversion quality
  - [Why Docling?](DOCLING_INFO.md)
- **AI Enhancement** (Local Ollama):
  - Automatic document summaries
  - AI-generated tags and keywords
  - Image descriptions for embedded photos
- **Obsidian Compatible**: Outputs markdown with proper frontmatter for Obsidian vaults
- **100% Local**: All processing happens on your machine - no cloud services
- **Privacy First**: Your documents never leave your computer

## 📋 Prerequisites

### Hardware Requirements (Important!)

**Minimum Recommended:**
- **CPU:** Apple M2 Pro or equivalent Intel/AMD processor
- **RAM:** 16 GB minimum (32 GB recommended)
- **Storage:** 10 GB free disk space

**Why:** Running AI models locally requires significant memory. Systems with < 16GB RAM will be very slow or may crash.

**Tested on:** MacBook Pro M2 Pro with 16GB RAM ✅

### Software Requirements

- Docker and Docker Compose installed
- Ollama installed and running (see setup below)

## 🚀 Quick Start

### Two Ways to Use

1. **CLI Mode** (Recommended): Convert single files with a simple command
2. **Batch Mode**: Process entire directories

### CLI Mode - Convert a Single File

```bash
# First time setup
./scripts/setup.sh

# Convert a file
./convert.sh document.pdf

# Output appears at: output/document.md
```

That's it! The markdown file is ready to use.

### Batch Mode - Process Directory

```bash
# First time setup
./scripts/setup.sh

# Add files to input/
cp ~/Documents/*.pdf input/

# Convert all
docker-compose up converter
```

## 📖 Detailed Setup

### 1. Clone or Create Project

```bash
cd myfiles_to_markdown
```

### 2. Pull Ollama Model (First Time Setup)

The application will automatically pull the model, but you can pre-download it:

```bash
docker-compose up ollama -d
docker exec -it myfiles_ollama ollama pull llama3.2:latest
```

For vision capabilities (image descriptions), also pull:

```bash
docker exec -it myfiles_ollama ollama pull llava:latest
```

### 3. Convert Your Files

**Option A: Single File (Simple)**

```bash
./convert.sh ~/Documents/report.pdf
# Output: output/report.md
```

**Option B: Custom Output Location**

```bash
./convert.sh report.pdf ~/Obsidian/MyVault/report.md
```

**Option C: Batch Processing**

```bash
# Add files to input/
cp ~/Documents/*.pdf input/

# Convert all
docker-compose up converter
```

Supported formats:
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Microsoft PowerPoint (`.pptx`)
- HTML (`.html`, `.htm`)

### 4. Get Your Markdown Files

Converted files will be in the `output` directory:

```bash
ls output/
# report.md

ls output/attachments/
# report_img_001.png
# report_img_002.png
```

## 📁 Project Structure

```
myfiles_to_markdown/
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Python app container
├── requirements.txt        # Python dependencies
├── config/
│   └── config.yaml        # Application configuration
├── src/
│   ├── main.py           # Main application
│   ├── config_manager.py # Configuration handling
│   ├── ai_enhancer.py    # Ollama AI integration
│   ├── obsidian_writer.py # Markdown output writer
│   └── converters/       # Document converters
│       ├── base_converter.py
│       ├── pdf_converter.py
│       ├── docx_converter.py
│       └── pptx_converter.py
├── input/                 # Place your documents here
├── output/               # Converted markdown files
│   └── attachments/      # Extracted images
└── logs/                 # Application logs
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

### Ollama Settings

```yaml
ollama:
  host: "http://ollama:11434"
  model: "llama3.2:latest"  # Change model here
  temperature: 0.7
```

Available models:
- `llama3.2:latest` - Good balance (recommended)
- `llama3.2:3b` - Faster, less accurate
- `mistral:latest` - Alternative model
- `llava:latest` - For image descriptions (vision model)

### Processing Settings

```yaml
processing:
  ocr:
    enabled: true
    language: "eng"  # Change for other languages
  
  ai:
    generate_summary: true
    generate_tags: true
    max_tags: 10
```

### Obsidian Settings

```yaml
obsidian:
  frontmatter:
    add_ai_summary: true
    add_ai_tags: true
  attachments_folder: "attachments"
```

## 🔧 Advanced Usage

### Using Different Ollama Models

To use a different model:

1. Edit `config/config.yaml`:
   ```yaml
   ollama:
     model: "mistral:latest"
   ```

2. Pull the model:
   ```bash
   docker exec -it myfiles_ollama ollama pull mistral:latest
   ```

3. Restart the converter:
   ```bash
   docker-compose restart converter
   ```

### Batch Processing

The converter automatically processes all supported files in the `input` directory. Just add more files and run again.

### Continuous Processing

To keep the converter running and watch for new files:

```bash
docker-compose up converter
# Leave it running, add files to input/ as needed
```

### Custom Output Location

You can mount a different output directory by editing `docker-compose.yml`:

```yaml
volumes:
  - ./input:/app/input
  - /path/to/your/obsidian/vault:/app/output  # Your Obsidian vault
```

## 📝 Output Format

Each converted document includes:

### Frontmatter
```yaml
---
title: "Document Title"
source_file: "original.pdf"
source_type: "pdf"
processed: "2025-11-10 14:30:00"
ai_summary: "AI-generated summary..."
tags:
  - keyword1
  - keyword2
  - keyword3
---
```

### Content Structure
```markdown
> [!summary] AI Summary
> Concise AI-generated summary appears here

## Page 1
Document content...

## Page 2
More content...

---

## Images

### Image 1
![[attachments/document_img_001.png]]
**Description:** AI-generated description of the image
```

## 🐛 Troubleshooting

### Ollama Not Starting

If Ollama fails to start:

```bash
# Check logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Wait for health check
docker-compose ps
```

### Model Not Found

Pull the model manually:

```bash
docker exec -it myfiles_ollama ollama pull llama3.2:latest
```

### Out of Memory

If you get OOM errors:

1. Use a smaller model:
   ```yaml
   model: "llama3.2:3b"  # Smaller, faster
   ```

2. Increase Docker memory limit in Docker Desktop settings

### Slow Processing

- First run is slow (downloading models)
- Subsequent runs are much faster
- Consider using smaller models for speed
- Disable AI features if not needed:
  ```yaml
  processing:
    ai:
      generate_summary: false
      generate_tags: false
  ```

## 🔒 Security & Privacy

- **100% Local**: No data leaves your machine
- **No Cloud Services**: Everything runs in Docker containers
- **No API Keys**: Uses local Ollama, no external APIs
- **Your Data**: Stays on your computer

## 🛠️ Development

### Running Tests

```bash
# Coming soon
```

### Adding New Converters

1. Create new converter in `src/converters/`
2. Inherit from `BaseConverter`
3. Implement `convert()` method
4. Register in `main.py`

## 📚 Tech Stack

- **Python 3.11**: Core application
- **Docker**: Containerization
- **Ollama**: Local LLM inference
- **Docling**: IBM's advanced document understanding library
- **Docling Core**: Document structure analysis
- **Tesseract**: OCR engine (integrated via Docling)
- **Pillow**: Image processing

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional file format support (RTF, ODT, EPUB, etc.)
- [ ] Advanced Docling pipeline customization
- [ ] Custom AI prompts
- [ ] GUI interface
- [ ] Progress tracking
- [ ] Incremental processing (skip already converted)
- [ ] Batch processing optimization

## ⭐ Why This Exists

To help users:
- Migrate documents to Obsidian
- Make documents AI-ready for RAG systems
- Search and organize document collections
- Extract insights from office files
- Maintain privacy while using AI

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Made with ❤️ for the Obsidian and AI communities**

