# How to Use MyFiles to Markdown

A complete guide to converting your documents to Obsidian-compatible markdown.

## 📋 Table of Contents

1. [Before You Start](#before-you-start)
2. [Initial Setup](#initial-setup)
3. [Converting Documents](#converting-documents)
4. [Understanding Output](#understanding-output)
5. [Using with Obsidian](#using-with-obsidian)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Before You Start

### Check Your Hardware

**Minimum Requirements:**
- MacBook Pro M2 Pro (or equivalent)
- 16 GB RAM
- 10 GB free disk space

**Quick check:**
```bash
# Check RAM
sysctl hw.memsize | awk '{print $2/1024/1024/1024 " GB"}'

# Check disk space
df -h .
```

If you have < 16GB RAM, see [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md) for alternatives.

---

## Initial Setup

### Step 1: Install Ollama

**Mac:**
```bash
# Download and install from:
https://ollama.ai/download

# Or use Homebrew:
brew install ollama
```

**Windows/Linux:** See [ollama.ai/download](https://ollama.ai/download)

### Step 2: Install AI Models

```bash
# Text model (REQUIRED - 2GB)
ollama pull llama3.2:latest

# Vision model (RECOMMENDED - 4.7GB)
ollama pull llava:7b

# Verify installation
ollama list
```

**Expected output:**
```
NAME                ID              SIZE
llama3.2:latest     a80c4f17acd5    2.0 GB
llava:7b            8dd30f6b0cb1    4.7 GB
```

### Step 3: Start Ollama

```bash
# Start Ollama service
ollama serve

# Or on Mac, it starts automatically
# Verify it's running:
curl http://localhost:11434/api/tags
```

### Step 4: Build the Converter

```bash
# Clone or navigate to project
cd myfiles_to_markdown

# Build Docker container
docker-compose build converter

# This takes 3-5 minutes on first run
```

**You're ready!** ✨

---

## Converting Documents

### Method 1: Single File (Recommended)

**Basic Usage:**
```bash
# Convert a file
./convert.sh document.pdf

# Output appears at:
# output/document.md
# output/attachments/
```

**Custom Output Location:**
```bash
# Specify output path
./convert.sh report.pdf ~/Documents/report.md

# For Obsidian vault:
./convert.sh meeting.docx ~/Obsidian/MyVault/Meetings/meeting.md
```

**Examples:**
```bash
# Convert PDF
./convert.sh ~/Downloads/report.pdf

# Convert PowerPoint
./convert.sh ~/Documents/presentation.pptx

# Convert Word document
./convert.sh ~/Desktop/notes.docx

# Convert multiple files one-by-one
for file in ~/Downloads/*.pdf; do
    ./convert.sh "$file"
done
```

### Method 2: Batch Processing

**Process entire directory:**
```bash
# 1. Copy files to input/
cp ~/Documents/*.pdf input/
cp ~/Documents/*.docx input/
cp ~/Documents/*.pptx input/

# 2. Run batch conversion
docker-compose run --rm converter python src/main.py

# 3. Results in output/
ls -lh output/
```

**Process and organize:**
```bash
# Organize by type
cp ~/Downloads/*.pdf input/
docker-compose run --rm converter python src/main.py
mv output/*.md ~/Obsidian/PDFs/

# Clean up for next batch
rm input/*
```

### What Gets Converted?

| Format | Extracted | Processing Time |
|--------|-----------|-----------------|
| **PDF** | Text, tables, images | 30-90 sec |
| **DOCX** | Text, formatting, images | 10-20 sec |
| **PPTX** | Slides, images, **speaker notes** | 15 sec - 25 min* |
| **HTML** | Text, structure | 5-10 sec |

*\*Depends on number of image slides (30 sec per image with vision AI)*

---

## Understanding Output

### Output Structure

```
output/
├── document.md              # Main markdown file
└── attachments/
    ├── document_img_001.png
    └── document_img_002.png
```

### Markdown Format

Every converted file includes:

**1. YAML Frontmatter**
```yaml
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
page_count: 10
processed: '2025-11-11 00:00:00'
---
```

**2. AI Summary Callout**
```markdown
> [!summary] Summary
> AI-generated summary here (max 100 words)
```

**3. Document Content**
```markdown
## Section Heading

Your document content...

| Tables | Are | Preserved |
|--------|-----|-----------|
| Data   | Here| Too      |
```

**4. Images (if any)**
```markdown
## Images

### Image 1
![[attachments/filename_img_001.png]]

> AI vision description or OCR text

**Speaker Notes:** (PowerPoint only)
> Presenter notes from the slide
```

### What AI Adds

**Description:** One-sentence overview
```yaml
description: This document is a guide for new employees...
```

**Summary:** 100-word summary
```yaml
summary: The guide outlines employee benefits including medical,
  dental, vision, and retirement plans. Employees can choose...
```

**Tags:** Obsidian-compatible keywords
```yaml
tags:
  - employee-benefits
  - health-insurance
  - 401k-contribution
```

---

## Using with Obsidian

### Option 1: Convert Directly to Vault

```bash
# Convert directly to Obsidian folder
./convert.sh document.pdf ~/Obsidian/MyVault/Documents/document.md

# Attachments go to:
# ~/Obsidian/MyVault/output/attachments/
```

### Option 2: Copy After Converting

```bash
# Convert first
./convert.sh document.pdf

# Then copy to vault
cp output/document.md ~/Obsidian/MyVault/
cp -r output/attachments ~/Obsidian/MyVault/
```

### Option 3: Batch Import

```bash
# Convert all files
./convert-batch.sh ~/Downloads

# Copy all results
cp output/*.md ~/Obsidian/MyVault/Imports/
cp -r output/attachments ~/Obsidian/MyVault/
```

### Configure Obsidian for Attachments

In Obsidian:
1. Settings → Files & Links
2. Default location for new attachments: `attachments`
3. New link format: `Relative path to file`

Now `![[attachments/image.png]]` will work perfectly!

### Using Tags in Obsidian

All tags are hyphenated and work with Obsidian:

```markdown
tags:
  - project-management  # Use #project-management
  - meeting-notes       # Use #meeting-notes
```

In Obsidian, you can:
- Click tags to see all related notes
- Use tag pane to browse
- Search by tag: `tag:#project-management`

---

## Tips & Best Practices

### 💡 General Tips

**1. Start Small**
```bash
# Test with one file first
./convert.sh test.pdf
# Check output quality before batch processing
```

**2. Close Other Apps**
```bash
# Free up RAM before large batches
# Close: Chrome, Slack, etc.
```

**3. Process Overnight**
```bash
# For large batches (100+ files)
nohup ./convert-batch.sh ~/Documents &
# Check progress: tail -f logs/converter.log
```

**4. Organize Input**
```bash
# Group by type for easier processing
mkdir input/pdfs input/docx input/pptx
cp ~/Downloads/*.pdf input/pdfs/
```

### 📄 Document-Specific Tips

**PDFs:**
- ✅ Fast processing (30-90 sec)
- ✅ Excellent table extraction
- ✅ Good for text-heavy documents
- ⚠️ Scanned PDFs take longer (OCR)

**Word Documents:**
- ✅ Very fast (10-20 sec)
- ✅ Formatting preserved
- ✅ Images extracted well

**PowerPoint:**
- ✅ Speaker notes extracted automatically
- ⚠️ Image slides take 30 sec each
- 💡 Text-heavy slides are fast
- 💡 Consider overnight for 50+ image slides

**HTML:**
- ✅ Fast conversion
- ✅ Good for web articles
- ⚠️ May include navigation elements

### 🎯 Performance Tips

**Speed Up Processing:**
```bash
# Disable AI for faster conversion
# Edit config/config.yaml:
ai:
  enabled: false  # Skip AI summaries/tags
```

**Save RAM:**
```bash
# Process one file at a time
for file in *.pdf; do
    ./convert.sh "$file"
    sleep 5  # Let RAM clear
done
```

**Optimize for Your Use Case:**

| Use Case | Recommended Setup |
|----------|-------------------|
| Quick conversion | Text model only, AI enabled |
| Text documents | Text model only, fast |
| Presentations | Text + vision models, slower |
| Batch overnight | Full setup, unattended |

---

## Troubleshooting

### Common Issues

**"Ollama is not running"**
```bash
# Solution:
ollama serve

# Verify:
ollama list
```

**"Model not found"**
```bash
# Solution:
ollama pull llama3.2:latest
ollama pull llava:7b
```

**"Very slow processing"**
- Close other applications
- Check RAM: `activity monitor` (Mac) or `htop` (Linux)
- Use text-only mode (skip vision model)
- Process fewer files at once

**"Poor image quality in presentations"**
- Make sure llava:7b is installed
- Check logs: `tail -f logs/converter.log`
- Verify vision model is being used

**"Images not showing in Obsidian"**
```bash
# Copy attachments to vault
cp -r output/attachments ~/Obsidian/MyVault/

# Update Obsidian settings:
# Settings → Files & Links → "attachments" folder
```

**"Out of memory"**
- Close all other applications
- Process one file at a time
- Restart computer to free RAM
- Consider upgrading to 32GB RAM

### Getting Help

**Check logs:**
```bash
# Real-time monitoring
tail -f logs/converter.log

# Search for errors
grep ERROR logs/converter.log
```

**Test individual components:**
```bash
# Test Ollama
ollama run llama3.2:latest "Test prompt"

# Test vision
ollama run llava:7b "Describe this"

# Test Docker
docker ps
```

**Still stuck?**
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [OLLAMA_REQUIREMENTS.md](OLLAMA_REQUIREMENTS.md)
3. See [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md)

---

## Quick Reference

### Most Common Commands

```bash
# Single file
./convert.sh document.pdf

# Custom output
./convert.sh input.pdf output.md

# Batch process
cp ~/Downloads/*.pdf input/
docker-compose run --rm converter python src/main.py

# Check status
ollama list
docker ps
ls -lh output/

# View logs
tail -f logs/converter.log
```

### File Locations

```
Project Structure:
├── input/          ← Put files here for batch
├── output/         ← Results go here
├── logs/           ← Conversion logs
└── config/         ← Settings
```

### Processing Times (16GB RAM)

- Small PDF (2 pages): ~30 sec
- Medium PDF (30 pages): ~90 sec
- Large PDF (161 pages): ~12 min
- DOCX: ~15 sec
- PPTX (text): ~20 sec
- PPTX (images): ~30 sec per image

**Real Example:** 26MB, 161-page training PDF with tables → 12 minutes

---

## Next Steps

**You're all set!** 

1. ✅ Convert your first document: `./convert.sh test.pdf`
2. ✅ Check the output: `cat output/test.md`
3. ✅ Import to Obsidian
4. ✅ Process your backlog

**Happy converting!** 🚀

For more details:
- [Quick Reference](QUICK_REFERENCE.md) - Command cheat sheet
- [Troubleshooting](TROUBLESHOOTING.md) - Fix common issues
- [Examples](EXAMPLES.md) - Real-world usage

