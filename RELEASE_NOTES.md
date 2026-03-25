# Release Notes

## Version 1.0.0 - Initial Release

**Release Date:** November 11, 2025

### 🎉 Features

#### Document Conversion
- **Docling-powered conversion** for PDF, DOCX, PPTX, HTML
- **Superior table extraction** - Handles complex tables with proper formatting
- **Layout-aware processing** - Understands document structure
- **Built-in OCR** - Automatic text extraction from images
- **Speaker notes extraction** - PowerPoint presenter notes included

#### AI Enhancement (Local Ollama)
- **Automatic summaries** - 100-word AI-generated summaries
- **Smart tagging** - AI-generated keywords (Obsidian-compatible)
- **Image understanding** - Vision AI (llava:7b) for image-heavy presentations
- **Descriptions** - One-sentence document descriptions
- **OCR + Vision fallback** - Best quality for any content type

#### Output Format
- **Obsidian-compatible markdown** - YAML frontmatter, wikilinks
- **Hyphenated tags** - Work with Obsidian tag system
- **Callout syntax** - `> [!summary]` for summaries
- **Table of contents ready** - Proper heading structure
- **Image attachments** - Organized in attachments/ folder

#### Modes
- **CLI mode** - Convert single files: `./convert.sh document.pdf`
- **Batch mode** - Process entire directories
- **Custom output** - Specify output location
- **Flexible configuration** - YAML config file

### 📊 Tested Formats

| Format | Status | Notes |
|--------|--------|-------|
| **PDF** | ✅ Excellent | Fast, great tables, 30-90 sec |
| **DOCX** | ✅ Excellent | Fast, 10-20 sec |
| **PPTX** | ✅ Excellent | Speaker notes + vision AI |
| **HTML** | ✅ Good | Web content extraction |

### 🎯 Performance

**Tested on MacBook Pro M2 Pro (16GB RAM):**
- Small PDF (2 pages): ~30 seconds
- Medium PDF (30 pages): ~90 seconds
- DOCX with images: ~15 seconds
- PPTX text slides: ~20 seconds
- PPTX image slides: ~30 sec per image

### 🖥️ System Requirements

**Minimum:**
- CPU: Apple M2 Pro or equivalent Intel/AMD
- RAM: 16 GB minimum (32 GB recommended)
- Storage: 10 GB free disk space
- OS: macOS, Linux, or Windows 11

**Required Software:**
- Docker and Docker Compose
- Ollama with models:
  - llama3.2:latest (2GB) - REQUIRED
  - llava:7b (4.7GB) - RECOMMENDED

### 📚 Documentation

- `README.md` - Project overview and quick start
- `HOW_TO_USE.md` - Complete usage guide
- `QUICK_REFERENCE.md` - Command cheat sheet
- `HARDWARE_REQUIREMENTS.md` - Detailed hardware specs
- `OLLAMA_REQUIREMENTS.md` - Model setup guide
- `TROUBLESHOOTING.md` - Common issues and solutions
- `DOCLING_INFO.md` - Why we use Docling
- `EXAMPLES.md` - Real-world usage examples

### 🔧 Technical Stack

- **Python 3.11+**
- **Docling 2.61+** - IBM's document understanding library
- **Ollama** - Local LLM inference
- **Docker** - Containerized deployment
- **python-pptx** - PowerPoint image extraction fallback
- **Tesseract OCR** - Text extraction from images
- **llava:7b** - Vision language model

### 🎨 Key Innovations

1. **Vision-first for presentations** - Always try AI vision before OCR for better quality
2. **Speaker notes extraction** - Automatic extraction of PowerPoint presenter notes
3. **Hybrid OCR + Vision** - Best of both worlds
4. **Obsidian optimization** - Tags, frontmatter, and wikilinks done right
5. **Simple setup** - One Ollama command instead of complex vLLM setup

### ✅ Testing

Tested with real-world documents:
- ✅ **161-page training PDF** (26MB, 1,768 lines markdown, 12 min)
- ✅ 29-page benefits enrollment guide (971 lines markdown)
- ✅ Technical assessment PDF (89 lines)
- ✅ PowerPoint presentations (76 lines with vision AI)
- ✅ Word documents (270 lines)
- ✅ Small PDFs (92 lines)

**Stress Test:** Successfully converted a 26MB, 161-page complex PDF with tables in 12 minutes!

### 🐛 Known Limitations

1. **Large image-heavy presentations** take time (30 sec per image)
2. **Requires 16GB RAM minimum** for vision AI
3. **Some embedded PDF images** may not extract
4. **OCR quality** varies with image quality
5. **First run downloads** OCR models automatically

### 🔮 Future Enhancements

- Batch progress indicator
- Web interface
- Cloud deployment option
- Additional output formats (HTML, JSON)
- Custom AI prompts
- Image compression options
- Multi-language support
- GPU acceleration

### 📦 Installation

See `README.md` and `HOW_TO_USE.md` for complete setup instructions.

**Quick start:**
```bash
# Install Ollama
ollama pull llama3.2:latest
ollama pull llava:7b
ollama serve

# Build converter
docker-compose build converter

# Convert a file
./convert.sh document.pdf
```

### 🙏 Acknowledgments

- **IBM Docling** - Excellent document processing library
- **Ollama** - Simple local LLM inference
- **python-pptx** - PowerPoint manipulation
- **Tesseract** - OCR engine

### 📄 License

MIT License - See LICENSE file

### 🐛 Bug Reports

Check `TROUBLESHOOTING.md` first, then open an issue with:
- OS and hardware specs
- Ollama version and models
- Sample file (if possible)
- Full error message
- Log output

---

**Version 1.0.0** - Ready for production use! 🚀

