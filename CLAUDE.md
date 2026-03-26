# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyFiles to Markdown converts office documents (PDF, DOCX, PPTX, HTML, CSV, XLSX, images, Jupyter notebooks, emails) to Obsidian-compatible markdown with AI enhancement via Ollama. Runs as a FastAPI Docker container with GPU acceleration.

## Build & Run Commands

```bash
# Build Docker containers
docker compose build

# Start the web UI + API (port 3143)
docker compose up -d web

# View logs
docker compose logs -f web

# Stop
docker compose down web

# Run tests (from host, against live container)
python3 -m pytest tests/test_e2e_comprehensive.py -v     # 71 E2E tests
python3 -m pytest tests/test_e2e_api.py -v                # 32 API tests
python3 -m pytest tests/test_e2e_browser.py -v            # 8 Playwright browser tests

# Run unit tests (inside container)
docker exec myfiles_web pip install pytest pytest-cov
docker exec myfiles_web python -m pytest /app/tests/ --cov --cov-config=/app/.coveragerc
```

## Architecture

FastAPI app in Docker (`src/web_app.py`) with GPU access (NVIDIA runtime). Docling uses local GPU (RTX 4070) for layout analysis. Ollama runs on a separate host for AI inference.

### API Endpoints

- `POST /api/convert` — sync: upload file, get markdown back
- `POST /api/upload` — async: upload file(s), get job ID(s), poll for completion
- `POST /api/upload/init` + `/chunk/{id}` + `/complete/{id}` — chunked upload for files >45MB (Cloudflare tunnel safe)
- `GET /api/jobs/{id}` — poll job status (includes `elapsed_seconds`)
- `GET /api/download/{id}` — download completed markdown
- `GET /api/debug/recent` — last 100 conversions with timing, status, file size
- `GET /api/debug/files` — last 10 input files kept for debugging
- `GET /docs` — Swagger UI (auto-generated from code)
- `GET /openapi.json` — OpenAPI 3.1 spec (auto-generated)
- `GET /health` — health check

### Processing Pipeline

1. **`src/web_app.py`**: FastAPI endpoints, chunked upload, concurrency semaphore (max 3), UUID-prefixed paths for multi-user safety
2. **`src/main.py` — `DocumentProcessor`**: Routes files to converters by extension, runs AI enhancement
3. **`src/converters/`**: Each extends `BaseConverter`, implements `convert(path) -> DocumentContent`
   - `DoclingUnifiedConverter` — PDF, DOCX, PPTX, HTML via IBM Docling (three-tier: fast/accurate/lite by page count)
   - `CsvConverter`, `XlsxConverter`, `ImageConverter`, `JupyterConverter`, `EmailConverter`
4. **`src/ai_enhancer.py`**: Ollama integration — summaries, tags, descriptions, vision
5. **`src/obsidian_writer.py`**: Markdown output with YAML frontmatter, Obsidian image embeds, HTML entity unescaping

### Key Design Decisions

- **Docling on GPU** (`DOCLING_DEVICE=cuda`): Uses local RTX 4070 for layout analysis. Ollama runs on separate host to avoid VRAM conflicts.
- **UUID-prefixed file paths**: Prevents filename collisions between concurrent users
- **Concurrency semaphore** (3 max): Prevents GPU/RAM exhaustion under load
- **Chunked uploads** (45MB chunks): Works within Cloudflare tunnel's 100MB limit
- **No job list endpoint**: Jobs only accessible by ID for multi-user privacy

### Configuration

`config/config.yaml` — Ollama host/model, supported formats, OCR, AI toggle, CSV/XLSX row limits, Docling table mode and page thresholds.

`docker-compose.yml` — Set `OLLAMA_HOST` to your Ollama instance IP.

### Adding a New Converter

1. Create `src/converters/<format>_converter.py` inheriting `BaseConverter`
2. Implement `convert(file_path) -> DocumentContent`
3. Export from `src/converters/__init__.py`
4. Add routing logic in `DocumentProcessor.process_file()` in `src/main.py`
5. Add extension to `SUPPORTED_FORMATS` in `src/web_app.py`

### Test Suite

- 71 comprehensive E2E tests (input validation, conversion quality, edge cases, concurrency, security, performance)
- 32 API-specific E2E tests
- 8 Playwright browser tests
- 119 unit tests (77% coverage on active code)
