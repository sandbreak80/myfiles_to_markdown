# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Docker installed and running
- At least 8GB RAM available
- ~5GB disk space for models

## Step-by-Step Setup

### 1. Initial Setup (First Time Only)

Run the setup script:

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

This will:
- Verify Docker is installed
- Start Ollama service
- Download the AI model (~2-3 GB)
- Create necessary directories

**Note**: Model download takes 5-15 minutes depending on your internet speed.

### 2. Add Your Documents

```bash
# Copy documents to input folder
cp ~/Documents/my-report.pdf input/
cp ~/Documents/presentation.pptx input/
```

Supported formats: `.pdf`, `.docx`, `.pptx`, `.html`

### 3. Convert Documents

```bash
./scripts/run.sh
```

Or manually:

```bash
docker-compose up converter
```

### 4. Get Your Results

```bash
ls output/
# my-report.md
# presentation.md

ls output/attachments/
# my-report_img_001.png
# presentation_img_001.png
```

## What You Get

Each markdown file includes:

```markdown
---
title: "My Report"
source_file: "my-report.pdf"
processed: "2025-11-10 14:30:00"
ai_summary: "This document discusses..."
tags:
  - analysis
  - business
  - quarterly
---

> [!summary] AI Summary
> Concise overview of the document...

## Page 1
Your content here...
```

## Next Steps

### Configure AI Model

Edit `config/config.yaml`:

```yaml
ollama:
  model: "llama3.2:latest"  # Try different models
  temperature: 0.7
```

Available models:
- `llama3.2:latest` - Best balance (default)
- `llama3.2:3b` - Faster, lighter
- `mistral:latest` - Alternative
- `llava:latest` - For image descriptions

### Batch Processing

Just keep adding files to `input/` and run the converter again:

```bash
cp ~/Documents/*.pdf input/
./scripts/run.sh
```

### Use with Obsidian

Point output to your Obsidian vault:

Edit `docker-compose.yml`:

```yaml
volumes:
  - ./input:/app/input
  - ~/Obsidian/MyVault:/app/output  # Your vault path
```

Then convert:

```bash
docker-compose up converter
```

Files appear directly in your vault!

## Common Commands

```bash
# Setup (first time only)
./scripts/setup.sh

# Convert documents
./scripts/run.sh

# Pull a different model
./scripts/pull_model.sh mistral:latest

# Clean up output and logs
./scripts/clean.sh

# Stop all services
docker-compose down

# View logs
docker-compose logs -f converter
```

## Troubleshooting

### "Ollama not available"

```bash
# Restart Ollama
docker-compose restart ollama

# Wait 10 seconds then try again
./scripts/run.sh
```

### "Model not found"

```bash
# Pull model manually
./scripts/pull_model.sh llama3.2:latest
```

### Out of memory

Use a smaller model in `config/config.yaml`:

```yaml
ollama:
  model: "llama3.2:3b"  # Smaller, faster
```

### Slow processing

First run is always slower (model loading). Subsequent runs are faster.

Disable AI features for speed:

```yaml
processing:
  ai:
    generate_summary: false
    generate_tags: false
```

## Tips

1. **Start small**: Test with 1-2 documents first
2. **Check logs**: `docker-compose logs -f` to see progress
3. **Organize input**: Use subdirectories in `input/` to organize by project
4. **Backup important files**: Keep originals safe
5. **GPU acceleration**: For faster processing, use Ollama with GPU support

## Support

- Read the full [README.md](README.md)
- Check [USAGE.md](USAGE.md) for advanced features
- Open an issue on GitHub

---

Happy converting! 🚀

