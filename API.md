# MyFiles to Markdown - API Reference

**Base URL:** `http://localhost:3143`

**Interactive docs:** `/docs` (Swagger UI) | `/openapi.json` (OpenAPI 3.1 spec)

Converts documents to Obsidian-compatible markdown with optional AI enhancement (summaries, tags, image descriptions) powered by Ollama. FastAPI, multi-user safe, GPU accelerated, chunked uploads for Cloudflare tunnels.

## Supported File Formats

| Category | Extensions |
|----------|-----------|
| Documents | `.pdf`, `.docx`, `.pptx`, `.html`, `.htm` |
| Spreadsheets | `.csv`, `.xlsx`, `.xls` |
| Images | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`, `.bmp`, `.gif`, `.webp` |
| Notebooks | `.ipynb` |
| Email | `.eml`, `.msg`, `.mbox` |

**Max file size:** 500 MB

---

## Endpoints

### `POST /api/convert` — Synchronous Conversion

Uploads a file, converts it to markdown, and returns the result in a single request. **Best for n8n and automation workflows.**

**Content-Type:** `multipart/form-data`

#### Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `file` | file | Yes | — | The document to convert |
| `ai_enhancement` | string | No | `"true"` | Enable AI summaries and tags (`"true"` / `"false"`) |
| `ai_image_processing` | string | No | `"true"` | Enable AI vision for image descriptions (`"true"` / `"false"`) |
| `output_format` | string | No | `"markdown"` | Response format: `"markdown"` or `"json"` |

#### Response — `output_format=markdown` (default)

**Content-Type:** `text/markdown`

Returns raw markdown text with YAML frontmatter:

```markdown
---
title: Document_Name
source_file: document.pdf
source_type: pdf
processed: '2026-03-24 18:26:28'
page_count: 3
word_count: 1250
summary: AI-generated summary of the document...
description: One-sentence description.
tags:
  - keyword-one
  - keyword-two
---

> [!summary] Summary
> AI-generated summary appears here

## Section Heading

Document content in markdown...
```

#### Response — `output_format=json`

**Content-Type:** `application/json`

```json
{
  "filename": "document.pdf",
  "output_filename": "document.md",
  "markdown": "---\ntitle: Document_Name\n...\n---\n\n## Content here...",
  "status": "completed"
}
```

#### Error Response

```json
{
  "error": "Description of what went wrong"
}
```

| Status Code | Meaning |
|-------------|---------|
| `200` | Conversion successful |
| `400` | No file provided or invalid request |
| `413` | File exceeds 500 MB limit |
| `415` | Unsupported file format (returns `supported_formats` list) |
| `422` | Missing required field (no file attached) |
| `500` | Conversion failed |
| `503` | Server busy — too many concurrent conversions (max 3) |
| `504` | Conversion timed out (5 min limit — file too large or complex) |

#### Examples

**curl — get markdown:**
```bash
curl -X POST http://localhost:3143/api/convert \
  -F "file=@report.pdf"
```

**curl — get JSON, no AI:**
```bash
curl -X POST http://localhost:3143/api/convert \
  -F "file=@report.pdf" \
  -F "ai_enhancement=false" \
  -F "output_format=json"
```

**Python:**
```python
import requests

response = requests.post(
    "http://localhost:3143/api/convert",
    files={"file": open("report.pdf", "rb")},
    data={"output_format": "json", "ai_enhancement": "true"}
)
result = response.json()
markdown = result["markdown"]
```

**JavaScript/Node:**
```javascript
const form = new FormData();
form.append("file", fs.createReadStream("report.pdf"));
form.append("output_format", "json");

const res = await fetch("http://localhost:3143/api/convert", {
  method: "POST",
  body: form,
});
const { markdown } = await res.json();
```

**n8n HTTP Request node:**
- Method: `POST`
- URL: `http://localhost:3143/api/convert`
- Body Content Type: `Form-Data/Multipart`
- Parameters:
  - `file` (type: file) — binary data from previous node
  - `output_format` — `json`
  - `ai_enhancement` — `true` or `false`

---

### `POST /api/upload` — Async Upload

Uploads one or more files for background processing. Returns immediately with job IDs for polling.

**Content-Type:** `multipart/form-data`

#### Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `files[]` | file(s) | Yes | — | One or more files to convert |
| `ai_enhancement` | string | No | `"true"` | Enable AI summaries and tags |
| `ai_image_processing` | string | No | `"true"` | Enable AI vision for images |

#### Response `200`

```json
{
  "message": "Uploaded 2 file(s)",
  "job_ids": [
    "179bf408-a96d-4f91-a2c0-30983a839c4d",
    "a3b2c1d0-e4f5-6789-abcd-ef0123456789"
  ],
  "skipped": ["video.mp4"],
  "skipped_reason": "unsupported format"
}
```

`skipped` and `skipped_reason` only appear when files with unsupported formats are included in the upload.

#### Example

```bash
curl -X POST http://localhost:3143/api/upload \
  -F "files[]=@report.pdf" \
  -F "files[]=@slides.pptx" \
  -F "ai_enhancement=true"
```

---

### Chunked Upload (files > 45 MB)

For files that exceed Cloudflare tunnel limits (~100MB), use the three-step chunked upload flow.

#### Step 1: `POST /api/upload/init`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filename` | string | Yes | Original filename |
| `total_size` | integer | Yes | Total file size in bytes |
| `total_chunks` | integer | Yes | Number of chunks |
| `ai_enhancement` | string | No | `"true"` / `"false"` |

Response: `{"upload_id": "uuid"}`

#### Step 2: `POST /api/upload/chunk/{upload_id}`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chunk_index` | integer | Yes | Zero-based chunk index |
| `chunk` | file | Yes | Chunk binary data (max 50MB) |

Response: `{"received": 2, "total": 3}`

#### Step 3: `POST /api/upload/complete/{upload_id}`

Reassembles chunks and starts background processing.

Response: `{"job_id": "uuid", "filename": "report.pdf"}`

#### Example

```bash
# Init
UPLOAD_ID=$(curl -s -X POST http://localhost:3143/api/upload/init \
  -F "filename=large_report.pdf" \
  -F "total_size=80000000" \
  -F "total_chunks=2" | jq -r '.upload_id')

# Upload chunks (45MB each)
curl -X POST "http://localhost:3143/api/upload/chunk/$UPLOAD_ID" \
  -F "chunk_index=0" -F "chunk=@chunk_0.bin"
curl -X POST "http://localhost:3143/api/upload/chunk/$UPLOAD_ID" \
  -F "chunk_index=1" -F "chunk=@chunk_1.bin"

# Complete
JOB_ID=$(curl -s -X POST "http://localhost:3143/api/upload/complete/$UPLOAD_ID" | jq -r '.job_id')

# Poll
curl -s "http://localhost:3143/api/jobs/$JOB_ID"
```

---

### `GET /api/jobs/{job_id}` — Get Job Status

Returns the status of a specific job. Jobs are only accessible by ID (no list endpoint for multi-user privacy).

### `GET /api/jobs/{job_id}` — Get Job Status

Returns the status and details of a specific job.

#### Path Parameters

| Parameter | Description |
|-----------|-------------|
| `job_id` | UUID returned from `/api/upload` |

#### Response `200`

```json
{
  "id": "179bf408-a96d-4f91-a2c0-30983a839c4d",
  "filename": "report.pdf",
  "status": "completed",
  "created_at": "2026-03-24T18:20:34.631000",
  "started_at": "2026-03-24T18:20:34.632000",
  "completed_at": "2026-03-24T18:21:04.500000",
  "output_file": "/app/output/report.md",
  "output_filename": "report.md"
}
```

#### Job Status Values

| Status | Meaning |
|--------|---------|
| `queued` | Job accepted, waiting to start |
| `processing` | Conversion in progress |
| `completed` | Done — file ready for download |
| `failed` | Conversion failed (check `error` field) |

#### Error Response `404`

```json
{
  "error": "Job not found"
}
```

---

### `GET /api/download/{job_id}` — Download Result

Downloads the converted markdown file for a completed job.

#### Path Parameters

| Parameter | Description |
|-----------|-------------|
| `job_id` | UUID of a completed job |

#### Response `200`

**Content-Type:** `text/markdown`

Returns the `.md` file as a download attachment.

#### Error Responses

| Status | Body |
|--------|------|
| `400` | `{"error": "Job not completed"}` |
| `404` | `{"error": "Job not found"}` or `{"error": "Output file not found"}` |

#### Example — Async Workflow (upload, poll, download)

```bash
# 1. Upload
JOB_ID=$(curl -s -X POST http://localhost:3143/api/upload \
  -F "files[]=@report.pdf" | jq -r '.job_ids[0]')

# 2. Poll until completed
while true; do
  STATUS=$(curl -s http://localhost:3143/api/jobs/$JOB_ID | jq -r '.status')
  [ "$STATUS" = "completed" ] && break
  [ "$STATUS" = "failed" ] && echo "FAILED" && exit 1
  sleep 2
done

# 3. Download
curl -s http://localhost:3143/api/download/$JOB_ID -o report.md
```

---

### `GET /health` — Health Check

#### Response `200`

```json
{
  "status": "healthy",
  "service": "myfiles-to-markdown",
  "version": "1.3.0"
}
```

---

## Markdown Output Format

All converted documents produce markdown with YAML frontmatter. When AI enhancement is enabled, the frontmatter includes `summary`, `description`, and `tags`.

### Frontmatter Fields

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| `title` | string | Yes | Derived from filename |
| `source_file` | string | Yes | Original filename |
| `source_type` | string | Yes | File extension (pdf, docx, etc.) |
| `processed` | string | Yes | Timestamp of conversion |
| `page_count` | integer | When available | Number of pages |
| `word_count` | integer | When AI enabled | Word count of extracted text |
| `summary` | string | When AI enabled | AI-generated summary (max 100 words) |
| `description` | string | When AI enabled | One-sentence AI description |
| `tags` | list | When AI enabled | AI-generated hyphenated keywords |

### Content Structure

- Headings preserved from document structure
- Tables converted to markdown tables (Docling extraction)
- Images saved to `attachments/` with Obsidian embed syntax `![[attachments/file_img_001.png]]`
- AI image descriptions appended below each image (when vision model available)

---

## Debug / Observability

### `GET /api/debug/recent` — Recent Conversions

Last 100 conversions with performance timing. For troubleshooting.

```json
{
  "conversions": [
    {
      "file": "report.pdf",
      "format": "pdf",
      "size": 3020396,
      "output_size": 17837,
      "status": "completed",
      "elapsed": 55.08,
      "ai": false,
      "timestamp": "2026-03-26T05:49:04.123456"
    }
  ],
  "count": 1
}
```

### `GET /api/debug/files` — Debug File Retention

Lists the last 10 input files kept on disk for debugging failed conversions.

```json
{
  "debug_files": [
    {"name": "20260326_053117_report.pdf", "size": 3020396, "modified": "2026-03-26T05:31:17"}
  ],
  "retention": 10
}
```

---

## Rate Limits / Timeouts

- Max 3 concurrent conversions (returns 503 when full)
- Synchronous `/api/convert` has a **10-minute server-side timeout** — returns 504 if exceeded
- PDFs over 20 pages use lightweight extraction mode automatically (no table structure)
- Set HTTP client timeout to at least **120 seconds** for small files, **600 seconds** for large PDFs
- For large batches, use the async `/api/upload` flow instead
- GPU acceleration (NVIDIA RTX 4070) for Docling layout analysis — typical conversion times:
  - Small docs (< 10 pages): seconds
  - Medium docs (10-20 pages): 10-30 seconds
  - Large docs (20+ pages): 30-90 seconds
  - Very large PDFs (100+ pages): 2-5 minutes
