# MyFiles to Markdown - API Reference

**Base URL:** `http://localhost:3143`

Converts documents to Obsidian-compatible markdown with optional AI enhancement (summaries, tags, image descriptions) powered by local Ollama.

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
| `500` | Conversion failed |
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

### `GET /api/jobs` — List All Jobs

Returns all jobs and their current status.

#### Response `200`

```json
{
  "jobs": [
    {
      "id": "179bf408-a96d-4f91-a2c0-30983a839c4d",
      "filename": "report.pdf",
      "status": "completed",
      "created_at": "2026-03-24T18:20:34.631000",
      "started_at": "2026-03-24T18:20:34.632000",
      "completed_at": "2026-03-24T18:21:04.500000",
      "output_file": "/app/output/report.md",
      "output_filename": "report.md",
      "ai_enhancement": true,
      "ai_image_processing": true
    }
  ]
}
```

---

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

### `GET /api/stats` — Processing Statistics

Returns aggregate job counts.

#### Response `200`

```json
{
  "total": 15,
  "queued": 0,
  "processing": 1,
  "completed": 13,
  "failed": 1
}
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

## Rate Limits / Timeouts

- No rate limiting is enforced
- Synchronous `/api/convert` has a **5-minute server-side timeout** — returns 504 if exceeded
- Large PDFs (80+ pages) use lightweight extraction mode automatically
- Set HTTP client timeout to at least **120 seconds** for AI-enabled conversions (300s for large PDFs)
- For large batches, use the async `/api/upload` flow instead
- GPU acceleration (NVIDIA) is enabled — typical conversion times:
  - Small docs (< 30 pages): seconds
  - Large docs (30-80 pages): 30-90 seconds
  - Very large docs (80+ pages): 2-5 minutes
