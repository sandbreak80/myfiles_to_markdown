# Ollama Requirements

## Overview

This project uses **Ollama** running on your **host machine** (not in Docker) to provide AI enhancements like summaries, tags, descriptions, and image understanding.

## ⚠️ Hardware Requirements

### Minimum Recommended Hardware

**For reliable performance, you need:**

- **CPU:** Apple M2 Pro or equivalent Intel/AMD
- **RAM:** 16 GB minimum (32 GB recommended)
- **Storage:** 10 GB free disk space
- **OS:** macOS (M1/M2), Linux, or Windows 11

### Why These Requirements?

Running local AI models requires significant resources:
- **Ollama + models:** 6-8 GB RAM during processing
- **Docker containers:** 2-4 GB RAM
- **System overhead:** 4-6 GB RAM
- **Total RAM needed:** 12-18 GB active use

**On systems with < 16GB RAM:**
- Processing will be **very slow**
- System may **freeze or crash**
- Vision AI (llava:7b) may **fail to run**

### Tested Configurations

| Hardware | RAM | Status | Notes |
|----------|-----|--------|-------|
| **MacBook Pro M2 Pro** | 16 GB | ✅ **Recommended** | Good performance |
| **MacBook Pro M1 Max** | 32 GB | ✅ **Excellent** | Best performance |
| **MacBook Air M2** | 8 GB | ⚠️ **Not recommended** | Very slow, may crash |
| **Intel i7 (recent)** | 16 GB | ✅ **Works** | Slower than M-series |
| **Intel i5** | 8 GB | ❌ **Will struggle** | Too slow |

### Performance by Hardware

**MacBook Pro M2 Pro (16GB):**
- Small PDF: ~30 seconds ✓
- Large PDF: ~90 seconds ✓
- PPTX with llava:7b: ~30 sec/image ✓

**MacBook Air M2 (8GB):**
- Small PDF: ~60 seconds ⚠️
- Large PDF: ~3-5 minutes ⚠️
- PPTX with llava:7b: May crash ❌

**If you have less than 16GB RAM:**
- Use text-only model (no vision)
- Process files one at a time
- Close other applications
- Expect slower performance

## Required Setup

### 1. Install Ollama

**Download and install Ollama:**
- **Mac/Linux:** [https://ollama.ai/download](https://ollama.ai/download)
- **Windows:** [https://ollama.ai/download](https://ollama.ai/download)

### 2. Start Ollama Service

Ollama must be running **before** you use the converter.

```bash
# Start Ollama (runs in background)
ollama serve

# Or on Mac, Ollama starts automatically after installation
```

**Verify it's running:**
```bash
curl http://localhost:11434/api/tags
# Should return JSON with model list
```

## Required Models

### Model 1: Text Generation (REQUIRED)

**Purpose:** Generate summaries, tags, and descriptions

**Recommended:** `llama3.2:latest` (2GB)

```bash
# Install the model
ollama pull llama3.2:latest

# Or use alternative:
ollama pull llama3.2:3b      # Smaller, faster (2GB)
ollama pull llama3.1:latest   # Larger, better quality (4.7GB)
```

**Configuration:** Set in `config/config.yaml`
```yaml
ai:
  model: "llama3.2:latest"
```

### Model 2: Vision/Image Understanding (RECOMMENDED)

**Purpose:** Understand images in presentations and documents (OCR fallback)

**Recommended:** `llava:7b` (4.7GB)

```bash
# Install vision model
ollama pull llava:7b

# Or use alternatives:
ollama pull llama3.2-vision   # Newer, better (2.2GB)
ollama pull llava:13b         # Larger, better quality (8GB)
ollama pull bakllava          # Alternative (4.7GB)
```

**What happens without a vision model:**
- Text extraction still works via OCR (Tesseract)
- Image-heavy slides may have poor quality descriptions
- You'll see: `[Image - install llama3.2-vision: ollama pull llama3.2-vision]`

**Priority order** (tries in this order):
1. `llava:7b` (if you already have it)
2. `llava`
3. `llama3.2-vision`
4. `llava:13b`
5. `bakllava`

## Verify Installation

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# List installed models
ollama list

# Expected output:
# NAME                ID              SIZE    MODIFIED
# llama3.2:latest     a80c4f17acd5    2.0 GB  2 weeks ago
# llava:7b            8dd30f6b0cb1    4.7 GB  5 days ago
```

## Performance & Resource Usage

### Text Model (llama3.2:latest)
- **RAM:** ~3-4 GB during generation
- **Speed:** 2-10 seconds per operation
- **Usage:** Every document (summaries, tags, descriptions)

### Vision Model (llava:7b)
- **RAM:** ~6-8 GB during generation  
- **Speed:** 20-30 seconds per image
- **Usage:** Only for image-heavy slides (presentations, diagrams)

### Total Disk Space
- **Minimum:** 2 GB (text model only)
- **Recommended:** 7 GB (text + vision)
- **Optimal:** 12+ GB (text + multiple vision models)

## Common Issues

### Issue 1: "Ollama is not running"
```bash
# Solution: Start Ollama
ollama serve

# Or restart it
pkill ollama && ollama serve
```

### Issue 2: "Model not found"
```bash
# Solution: Pull the model
ollama pull llama3.2:latest
ollama pull llava:7b
```

### Issue 3: Port 11434 already in use
```bash
# Solution: Check what's using the port
lsof -i :11434

# Kill the process if needed
pkill ollama
ollama serve
```

### Issue 4: Docker can't reach host Ollama
The converter uses `host.docker.internal:11434` to reach your host machine's Ollama.

**Mac/Windows:** Should work automatically  
**Linux:** May need:
```bash
# Add to docker-compose.yml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Model Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `llama3.2:3b` | 2 GB | Fast | Good | Quick processing |
| `llama3.2:latest` | 2 GB | Fast | Good | **Recommended default** |
| `llama3.1:latest` | 4.7 GB | Medium | Better | Higher quality summaries |
| `llava:7b` | 4.7 GB | Medium | Good | **Vision (recommended)** |
| `llama3.2-vision` | 2.2 GB | Fast | Good | Vision (newer) |
| `llava:13b` | 8 GB | Slow | Best | Vision (highest quality) |

## Configuration

Edit `config/config.yaml` to change models:

```yaml
ollama:
  host: "http://localhost:11434"  # Default
  model: "llama3.2:latest"         # Text model
  timeout: 120

ai:
  enabled: true
  model: "llama3.2:latest"  # Change to your preferred model
  generate_summary: true
  generate_tags: true
  max_tags: 10
```

## Minimal Setup (Text Only)

If you only want basic AI features without image understanding:

```bash
# Just install the text model
ollama pull llama3.2:latest

# Start Ollama
ollama serve

# Convert documents (OCR fallback for images)
./convert.sh document.pdf
```

## Optimal Setup (Full Features)

For best results with image-heavy presentations:

```bash
# Install both models
ollama pull llama3.2:latest
ollama pull llava:7b

# Start Ollama
ollama serve

# Convert documents (AI vision for images)
./convert.sh presentation.pptx
```

## Testing Your Setup

```bash
# Test text generation
ollama run llama3.2:latest "Write a 1-sentence summary of AI benefits"

# Test vision (if installed)
ollama run llava:7b "Describe this image" --image test.png

# Test the converter
./convert.sh test_document.pdf
```

## Environment Variables

You can override the Ollama host:

```bash
# Use different Ollama instance
export OLLAMA_HOST="http://192.168.1.100:11434"
./convert.sh document.pdf

# Or in docker-compose.yml
environment:
  - OLLAMA_HOST=http://custom-host:11434
```

## Upgrading Models

```bash
# Update to latest version
ollama pull llama3.2:latest
ollama pull llava:7b

# Remove old versions
ollama rm old-model-name

# Check what's installed
ollama list
```

## Support

- **Ollama Issues:** [https://github.com/ollama/ollama/issues](https://github.com/ollama/ollama/issues)
- **Model Library:** [https://ollama.ai/library](https://ollama.ai/library)
- **This Project:** See `README.md` for converter-specific help

