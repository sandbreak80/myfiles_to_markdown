# Example n8n Workflows

Seven ready-to-use n8n workflows demonstrating the MyFiles to Markdown API.

## Workflows

### 1. Simple Document Conversion
Webhook trigger — upload a file, get markdown back. The building block for everything else.

### 2. Email Attachment Processor
Monitors Gmail for new attachments. Auto-converts PDF/DOCX/PPTX to markdown and saves to Google Drive. Filters unsupported formats automatically.

### 3. RAG Knowledge Base Builder
Bulk-converts a Google Drive folder into a structured knowledge base. Extracts AI summaries and tags from each document, then stores in a vector database for RAG/LLM retrieval.

### 4. Slack Document Bot
Users drop files in a Slack channel. Bot converts them and replies with the AI summary. Ideal for team document sharing.

### 5. Scheduled Report Converter
Runs daily at 6 AM. Picks up new files from a Drive folder, converts with AI enhancement, and emails summaries to stakeholders.

### 6. Chunked Upload for Large Files
Handles files over 45MB by splitting into chunks. Required when behind Cloudflare tunnels with 100MB upload limits. Uses the three-step init/chunk/complete flow.

### 7. Multi-Format Batch Processor
Routes different file types through different conversion paths — documents get AI enhancement, spreadsheets and images get fast conversion without AI.

## Setup

1. Set the `MD_API_URL` environment variable in n8n to your API URL
2. Import the workflow JSON from `n8n_showcase_workflows.json`
3. Connect your Gmail/Google Drive/Slack credentials as needed
4. Activate the workflow

## API Quick Reference

| Endpoint | Method | Use Case |
|----------|--------|----------|
| `/api/convert` | POST | Sync: upload file, get markdown back |
| `/api/upload` | POST | Async: upload file(s), get job IDs |
| `/api/upload/init` | POST | Chunked: start upload session |
| `/api/upload/chunk/{id}` | POST | Chunked: upload 45MB chunk |
| `/api/upload/complete/{id}` | POST | Chunked: reassemble and process |
| `/api/jobs/{id}` | GET | Poll job status |
| `/api/download/{id}` | GET | Download completed markdown |
| `/docs` | GET | Interactive Swagger UI |

## Supported Formats

PDF, DOCX, PPTX, HTML, CSV, XLSX, XLS, PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP, IPYNB, EML, MSG, MBOX
