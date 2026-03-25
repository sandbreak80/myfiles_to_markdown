# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyFiles to Markdown converts office documents (PDF, DOCX, PPTX, HTML, CSV, XLSX, images, Jupyter notebooks, emails) to Obsidian-compatible markdown with local AI enhancement via Ollama. Everything runs in Docker containers — no cloud services.

## Build & Run Commands

```bash
# First-time setup (pulls Ollama + models, builds containers)
./scripts/setup.sh

# Build Docker containers
make build
# or: docker-compose build

# Convert a single file (most common workflow)
./convert.sh document.pdf
./convert.sh document.pdf output/custom-name.md
make convert FILE=document.pdf

# Batch convert everything in input/
docker-compose up converter
make run

# Start the web UI (port 3143)
docker-compose up web

# View logs
make logs                    # all services
make logs-converter          # converter only

# Stop / restart
make stop
make restart

# Clean output and logs
make clean
```

There is no test suite. `make test` only validates docker-compose config.

## Architecture

The app runs inside Docker. The `converter` service runs `src/main.py`; the `web` service runs `src/web_app.py` (Flask on port 5000, exposed as 3143). Both connect to a host-accessible Ollama instance for AI features.

### Processing Pipeline

1. **`src/main.py` — `DocumentProcessor`**: Orchestrator. Routes files to the right converter by extension, runs AI enhancement, then writes output.
2. **`src/converters/`**: Each converter extends `BaseConverter` (in `base_converter.py`) and implements `convert(file_path) -> DocumentContent`.
   - `DoclingUnifiedConverter` (in `docling_converter.py`) — handles PDF, DOCX, PPTX, HTML via IBM's Docling library. This is the primary converter.
   - Specialized converters: `CsvConverter`, `XlsxConverter`, `ImageConverter`, `JupyterConverter`, `EmailConverter`.
3. **`src/ai_enhancer.py` — `AIEnhancer`**: Calls Ollama to generate summaries, tags, descriptions, and image analysis (vision models). Falls back gracefully if Ollama is unavailable.
4. **`src/obsidian_writer.py` — `ObsidianWriter`**: Writes markdown with YAML frontmatter (title, tags, summary) and Obsidian-style image embeds (`![[attachments/...]]`).
5. **`src/config_manager.py`**: Loads `config/config.yaml`.

### Key Data Type

`DocumentContent` (in `base_converter.py`) is the shared interchange format between converters and the writer. It holds `.text`, `.images`, `.metadata`, and `.title`.

### Configuration

All settings live in `config/config.yaml` — Ollama host/model, supported formats, OCR settings, AI toggle, Obsidian frontmatter options. Paths are Docker-internal (`/app/input`, `/app/output`).

### Adding a New Converter

1. Create `src/converters/<format>_converter.py` inheriting `BaseConverter`
2. Implement `convert(file_path) -> DocumentContent`
3. Export from `src/converters/__init__.py`
4. Add routing logic in `DocumentProcessor.process_file()` in `src/main.py`
