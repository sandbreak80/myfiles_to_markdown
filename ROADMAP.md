# Roadmap

## Current — v2.1.0

FastAPI, multi-user, GPU accelerated, chunked uploads, 71 E2E tests, 98.3% word recall accuracy.

## Next — v2.2

- **Webhook callbacks**: POST to a URL when async jobs complete (for n8n/automation)
- **Authentication**: API key or Bearer token support for multi-tenant deployments
- **Job expiry**: Auto-delete completed jobs and output files after configurable TTL
- **PPTX slide screenshots**: Render full slide images alongside extracted text
- **Batch progress**: Return per-file progress for multi-file uploads
- **Retry on Ollama failure**: Auto-retry AI enhancement if Ollama is temporarily unavailable

## Future — v3.0

- **OCR pipeline**: Dedicated OCR mode for scanned PDFs with configurable language packs
- **Custom AI prompts**: User-defined prompts for summary/tag generation
- **Output format options**: Plain markdown (no frontmatter), JSON-only, or structured data
- **Streaming responses**: Stream conversion progress for large files instead of blocking
- **Persistent job store**: SQLite or Redis for job history that survives container restarts
- **Rate limiting**: Per-IP or per-API-key rate limits for public deployments
- **Docker health checks**: Liveness and readiness probes for Kubernetes deployments

## Known Limitations

- **PDF processing speed**: Large PDFs (80+ pages) take 2-5 minutes even in LITE mode. Docling's layout analysis is CPU-bound.
- **GPU VRAM sharing**: Docling and Ollama cannot share the same GPU — Docling is forced to CPU via `DOCLING_DEVICE=cpu`. Requires a separate Ollama host for GPU inference.
- **Scanned PDFs**: OCR accuracy depends on scan quality. Handwritten text is not supported.
- **HTML entity edge cases**: Unicode math symbols (`&minus;`, `&deg;`) resolve to unicode codepoints, not ASCII equivalents.
- **No persistent storage**: Jobs and output files are in-memory/filesystem only. Container restart loses all state.
- **Single-process**: Uvicorn runs single-process. High-concurrency deployments should use a reverse proxy with multiple container replicas.
- **Cloudflare 100MB limit**: Files over ~45MB must use the chunked upload flow. The web UI handles this automatically; API consumers must implement chunking.
