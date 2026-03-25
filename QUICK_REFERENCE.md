# Quick Reference Card

## ⚠️ Before You Start

**Minimum Hardware:**
- Apple M2 Pro (or equivalent) with 16GB RAM
- 10 GB free disk space

Systems with < 16GB RAM will be very slow or may crash.

## ⚡ TL;DR Setup

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull models
ollama pull llama3.2:latest  # 2GB - REQUIRED
ollama pull llava:7b          # 4.7GB - for image understanding

# 3. Start Ollama
ollama serve

# 4. Build & run converter
docker-compose build converter
./convert.sh document.pdf
```

## 📋 Model Requirements

| Model | Size | Purpose | Required? |
|-------|------|---------|-----------|
| **llama3.2:latest** | 2 GB | Summaries, tags, descriptions | ✅ YES |
| **llava:7b** | 4.7 GB | Image understanding (presentations) | ⭐ RECOMMENDED |

## 🚀 Common Commands

### Single File Conversion
```bash
./convert.sh document.pdf                    # → output/document.md
./convert.sh presentation.pptx                # → output/presentation.md
./convert.sh report.docx ~/Obsidian/report.md # Custom output
```

### Batch Conversion
```bash
cp ~/Downloads/*.{pdf,docx,pptx} input/
docker-compose run --rm converter python src/main.py
```

### Check Ollama Status
```bash
ollama list                        # Show installed models
curl http://localhost:11434/api/tags   # Check if running
ollama serve                       # Start Ollama
```

## 📊 What Gets Extracted

| Source | Extracted |
|--------|-----------|
| **PDF** | Text, tables, layout, images (when possible) |
| **DOCX** | Text, formatting, images, tables |
| **PPTX** | Slide content, images, **speaker notes** |
| **All** | AI summary, tags, descriptions |

## 🎯 Processing Times

| Document Type | Size | Time |
|---------------|------|------|
| Small PDF (2 pages) | 75 KB | ~30 sec |
| Medium PDF (30 pages) | 4.5 MB | ~90 sec |
| DOCX with text | 500 KB | ~10 sec |
| **PPTX (text slides)** | 600 KB | ~15 sec |
| **PPTX (2 image slides)** | 600 KB | ~1 min |
| **PPTX (50 image slides)** | 50 MB | ~25 min |

> ⚡ **Tip:** Image-heavy presentations use AI vision (llava:7b) which takes 20-30 sec per image

## 📁 Output Structure

```
output/
├── document.md              # Main markdown file
└── attachments/
    ├── document_img_001.png
    └── document_img_002.png
```

## 🔍 Markdown Features

Every converted file includes:

```markdown
---
title: Document Title
description: AI-generated one-sentence description
summary: AI-generated 100-word summary
tags:
  - hyphenated-tags
  - obsidian-compatible
source_file: original.pdf
source_type: pdf
word_count: 1234
processed: '2025-11-11 00:00:00'
---

> [!summary] Summary
> AI-generated summary here (max 100 words)

## Document Content

Your converted content here...

## Images

### Image 1
![[attachments/filename_img_001.png]]

> AI vision description or OCR text

**Speaker Notes:** (for PPTX)
> Presenter notes from slides
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
ai:
  model: "llama3.2:latest"  # Change text model
  enabled: true              # Toggle AI features
  max_tags: 10              # Number of tags

processing:
  supported_formats:
    - pdf
    - docx
    - pptx
    - html
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama not running" | `ollama serve` |
| "Model not found" | `ollama pull llama3.2:latest` |
| Poor image quality | `ollama pull llava:7b` |
| Slow processing | Normal for image-heavy files |
| Missing speaker notes | Check original PPTX has notes |

📖 **Full guide:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 🔗 Links

- **Ollama Setup:** [OLLAMA_REQUIREMENTS.md](OLLAMA_REQUIREMENTS.md)
- **Full README:** [README.md](README.md)
- **Docling Info:** [DOCLING_INFO.md](DOCLING_INFO.md)
- **Examples:** [EXAMPLES.md](EXAMPLES.md)

## 💡 Pro Tips

1. **Install llava:7b for presentations** - Much better than OCR alone
2. **Batch overnight** - Process large batches when you're away
3. **Text files are fast** - PDFs and DOCX process in seconds
4. **Check speaker notes** - PPTX files extract presenter notes automatically
5. **Use with Obsidian** - Output is optimized for Obsidian vaults

