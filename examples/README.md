# Example n8n Workflows

Seven production-ready n8n workflows built with best practices: error handling, retry logic, health checks, failure alerts, and proper timeout management.

## Workflows

### 1. Simple Document Conversion
Webhook trigger with **health check** before conversion. Retries 3x on failure with 5s backoff. Returns proper error JSON on failure instead of crashing.

### 2. Email Attachment Processor
Monitors Gmail for attachments. Filters supported formats, converts with retry, saves to Google Drive. **Alerts on Slack** when conversion fails (disabled by default — enable and configure credentials).

### 3. RAG Knowledge Base Builder
Scheduled daily at 2 AM. Converts a Drive folder into a vector database with AI enhancement. Uses **upsert** (safe to re-run), **batching** (1 file at a time with 2s interval), and `continueOnFail` so one bad file doesn't kill the batch.

### 4. Slack Document Bot
Users share files in a channel. Bot sends an **immediate ack** (avoids Slack's 3-second timeout), then converts async and replies with the result. Separate success/error replies.

### 5. Async Upload with Poll Loop
Production-grade async pattern: upload -> **poll loop with max attempts** (60 iterations x 5s = 5 min max) -> download. Returns `202 Accepted` immediately to the webhook caller.

### 6. Batch Processor with Error Recovery
Processes mixed file types. **Each file independent** (`continueOnFail=true`) — one failure doesn't stop the batch. Smart AI routing: documents get AI enhancement, spreadsheets/images get fast mode. Logs every result to Google Sheets.

### 7. Health Monitor & Alert
Runs every 5 minutes. Checks API health and pulls recent conversion stats from `/api/debug/recent`. **Alerts on Slack** if the service is down.

## Best Practices Applied

| Practice | Where |
|----------|-------|
| Health check before processing | Workflows 1, 7 |
| `continueOnFail` on HTTP nodes | All conversion nodes |
| Retry with backoff (3x, 5-15s) | All conversion nodes |
| Immediate webhook ack (202) | Workflows 5, 6 |
| 600s timeout (matches API) | All conversion nodes |
| Batching with interval | Workflows 3, 6 |
| Separate error routing | All workflows |
| Failure alerts (Slack) | Workflows 2, 7 |
| Poll loop with max attempts | Workflow 5 |
| Upsert (idempotent writes) | Workflow 3 |

## Setup

1. Set `MD_API_URL` environment variable in n8n to your API URL
2. Import the workflow JSON from `n8n_showcase_workflows.json`
3. Connect credentials (Gmail, Google Drive, Slack, etc.) as needed
4. Enable disabled alert nodes after configuring credentials
5. Activate the workflow

## API Quick Reference

| Endpoint | Method | Timeout | Use Case |
|----------|--------|---------|----------|
| `/api/convert` | POST | 10 min | Sync: upload file, get markdown |
| `/api/upload` | POST | 30s | Async: upload, get job ID |
| `/api/jobs/{id}` | GET | - | Poll job status |
| `/api/download/{id}` | GET | - | Download markdown |
| `/api/debug/recent` | GET | - | Last 100 conversions with timing |
| `/api/debug/files` | GET | - | Debug file retention |
| `/health` | GET | - | Service health check |
| `/docs` | GET | - | Interactive Swagger UI |
