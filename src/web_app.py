"""Web UI and API for document conversion — FastAPI, multi-user safe."""

import os
import shutil
import uuid
import threading
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

import sys
sys.path.insert(0, '/app/src')
from main import DocumentProcessor

# ─── Constants ───────────────────────────────────────────────────

UPLOAD_FOLDER = Path('/app/uploads')
API_UPLOAD_FOLDER = Path('/app/uploads/_api_tmp')
CHUNK_UPLOAD_FOLDER = Path('/app/uploads/_chunks')
OUTPUT_FOLDER = Path('/app/output')

for d in [UPLOAD_FOLDER, API_UPLOAD_FOLDER, CHUNK_UPLOAD_FOLDER, OUTPUT_FOLDER]:
    d.mkdir(parents=True, exist_ok=True)

SUPPORTED_FORMATS = [
    'pdf', 'docx', 'pptx', 'html', 'htm', 'csv', 'xlsx', 'xls',
    'png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'gif', 'webp',
    'ipynb', 'eml', 'msg', 'mbox'
]

CONVERSION_TIMEOUT = 300
CHUNK_SIZE_LIMIT = 50 * 1024 * 1024
MAX_FILE_SIZE = 500 * 1024 * 1024
MAX_CONCURRENT_CONVERSIONS = 3

# Semaphore to limit concurrent conversions (prevent GPU/RAM OOM)
_conversion_semaphore = threading.Semaphore(MAX_CONCURRENT_CONVERSIONS)

# ─── Job tracking ────────────────────────────────────────────────

jobs: Dict[str, Dict] = {}
jobs_lock = threading.Lock()

chunked_uploads: Dict[str, Dict] = {}
chunks_lock = threading.Lock()


class JobStatus:
    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


# ─── Helpers ─────────────────────────────────────────────────────

def _validate_ext(filename: str) -> str:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext if ext in SUPPORTED_FORMATS else ''


def _no_cache_headers():
    return {
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
        'Pragma': 'no-cache',
        'Expires': '0',
    }


def _unique_path(base_dir: Path, filename: str) -> Path:
    """Create a collision-safe file path using a UUID prefix."""
    prefix = uuid.uuid4().hex[:12]
    return base_dir / f"{prefix}_{filename}"


def process_file_job(job_id: str, file_path: Path,
                     ai_enhancement: bool = True, ai_image_processing: bool = True):
    """Process a file in the background with concurrency limiting."""
    with jobs_lock:
        jobs[job_id]['status'] = JobStatus.PROCESSING
        jobs[job_id]['started_at'] = datetime.now().isoformat()

    acquired = _conversion_semaphore.acquire(timeout=CONVERSION_TIMEOUT)
    if not acquired:
        with jobs_lock:
            jobs[job_id]['status'] = JobStatus.FAILED
            jobs[job_id]['error'] = 'Server busy — too many concurrent conversions'
            jobs[job_id]['completed_at'] = datetime.now().isoformat()
        return

    try:
        logger.info(f"Processing job {job_id}: {file_path.name}")
        processor = DocumentProcessor()
        if not ai_enhancement:
            processor.ai_enabled = False

        success = processor.process_file(file_path, enable_ai_images=ai_image_processing)

        if success:
            # Output file uses the uploaded file's stem (which already has UUID prefix)
            output_file = OUTPUT_FOLDER / f"{file_path.stem}.md"
            with jobs_lock:
                jobs[job_id]['status'] = JobStatus.COMPLETED
                jobs[job_id]['completed_at'] = datetime.now().isoformat()
                jobs[job_id]['output_file'] = str(output_file)
                jobs[job_id]['output_filename'] = jobs[job_id]['original_filename'].rsplit('.', 1)[0] + '.md'
            logger.success(f"Job {job_id} completed")
        else:
            with jobs_lock:
                jobs[job_id]['status'] = JobStatus.FAILED
                jobs[job_id]['error'] = 'Conversion failed'
                jobs[job_id]['completed_at'] = datetime.now().isoformat()
    except Exception as e:
        logger.error(f"Job {job_id} error: {e}")
        with jobs_lock:
            jobs[job_id]['status'] = JobStatus.FAILED
            jobs[job_id]['error'] = str(e)
            jobs[job_id]['completed_at'] = datetime.now().isoformat()
    finally:
        _conversion_semaphore.release()
        if file_path.exists():
            file_path.unlink()


# ─── App ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MyFiles to Markdown API v2.1.0 starting")
    yield
    logger.info("Shutting down")

app = FastAPI(
    title="MyFiles to Markdown API",
    version="2.1.0",
    description="Convert documents to Obsidian-compatible markdown with AI enhancement. Multi-user safe.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="/app/web/static"), name="static")


@app.middleware("http")
async def add_no_cache(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/") or request.url.path == "/health" or request.url.path.startswith("/static/"):
        for k, v in _no_cache_headers().items():
            response.headers[k] = v
    return response


# ─── Web UI ──────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path("/app/web/templates/index.html")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ─── Health ──────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "myfiles-to-markdown", "version": "2.1.0"}


# ─── Sync Convert ───────────────────────────────────────────────

@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    ai_enhancement: str = Form("true"),
    ai_image_processing: str = Form("true"),
    output_format: str = Form("markdown"),
):
    """Synchronous conversion. Upload a file, get markdown back. Multi-user safe."""
    filename = file.filename or ""
    file_ext = _validate_ext(filename)
    if not file_ext:
        raw_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else '(none)'
        raise HTTPException(status_code=415, detail={
            "error": f"Unsupported file format: .{raw_ext}",
            "supported_formats": SUPPORTED_FORMATS,
        })

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail={"error": "File exceeds 500 MB limit"})

    # UUID-prefixed path prevents collisions between concurrent users
    file_path = _unique_path(API_UPLOAD_FOLDER, filename)
    file_path.write_bytes(content)

    ai_on = ai_enhancement.lower() == "true"
    ai_img = ai_image_processing.lower() == "true"

    try:
        acquired = _conversion_semaphore.acquire(timeout=10)
        if not acquired:
            raise HTTPException(status_code=503, detail={
                "error": "Server busy. Too many concurrent conversions. Try again shortly."
            })

        try:
            processor = DocumentProcessor()
            if not ai_on:
                processor.ai_enabled = False

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(processor.process_file, file_path, ai_img)
                try:
                    success = future.result(timeout=CONVERSION_TIMEOUT)
                except concurrent.futures.TimeoutError:
                    raise HTTPException(status_code=504, detail={
                        "error": f"Conversion timed out after {CONVERSION_TIMEOUT}s.",
                        "filename": filename,
                    })
        finally:
            _conversion_semaphore.release()

        if not success:
            raise HTTPException(status_code=500, detail={"error": f"Conversion failed for {filename}"})

        output_file = OUTPUT_FOLDER / f"{file_path.stem}.md"
        if not output_file.exists():
            raise HTTPException(status_code=500, detail={"error": "Output file not generated"})

        markdown_content = output_file.read_text(encoding='utf-8')

        if output_format.lower() == "json":
            return JSONResponse(
                content={
                    "filename": filename,
                    "output_filename": filename.rsplit('.', 1)[0] + '.md',
                    "markdown": markdown_content,
                    "status": "completed",
                },
                headers=_no_cache_headers(),
            )
        else:
            return Response(
                content=markdown_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'inline; filename="{filename.rsplit(".", 1)[0]}.md"',
                    **_no_cache_headers(),
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync conversion error: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
    finally:
        if file_path.exists():
            file_path.unlink()
        stem = file_path.stem
        out_md = OUTPUT_FOLDER / f"{stem}.md"
        if out_md.exists():
            out_md.unlink()
        att_dir = OUTPUT_FOLDER / "attachments"
        if att_dir.exists():
            for att in att_dir.glob(f"{stem}_img_*"):
                att.unlink()


# ─── Chunked Upload ─────────────────────────────────────────────

@app.post("/api/upload/init")
async def chunked_upload_init(
    filename: str = Form(...),
    total_size: int = Form(...),
    total_chunks: int = Form(...),
    ai_enhancement: str = Form("true"),
    ai_image_processing: str = Form("true"),
):
    """Initialize a chunked upload session."""
    if not _validate_ext(filename):
        raise HTTPException(status_code=415, detail={
            "error": "Unsupported file format",
            "supported_formats": SUPPORTED_FORMATS,
        })
    if total_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail={"error": "File exceeds 500 MB limit"})

    upload_id = str(uuid.uuid4())
    chunk_dir = CHUNK_UPLOAD_FOLDER / upload_id
    chunk_dir.mkdir(parents=True, exist_ok=True)

    with chunks_lock:
        chunked_uploads[upload_id] = {
            "filename": filename,
            "total_size": total_size,
            "total_chunks": total_chunks,
            "received_chunks": 0,
            "ai_enhancement": ai_enhancement.lower() == "true",
            "ai_image_processing": ai_image_processing.lower() == "true",
            "chunk_dir": str(chunk_dir),
            "created_at": datetime.now().isoformat(),
        }

    return JSONResponse(content={"upload_id": upload_id}, headers=_no_cache_headers())


@app.post("/api/upload/chunk/{upload_id}")
async def chunked_upload_chunk(
    upload_id: str,
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...),
):
    """Upload a single chunk."""
    with chunks_lock:
        upload = chunked_uploads.get(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail={"error": "Upload session not found"})

    chunk_data = await chunk.read()
    if len(chunk_data) > CHUNK_SIZE_LIMIT + 1024:
        raise HTTPException(status_code=413, detail={"error": "Chunk exceeds 50 MB limit"})

    chunk_path = Path(upload["chunk_dir"]) / f"chunk_{chunk_index:04d}"
    chunk_path.write_bytes(chunk_data)

    with chunks_lock:
        chunked_uploads[upload_id]["received_chunks"] += 1
        received = chunked_uploads[upload_id]["received_chunks"]
        total = chunked_uploads[upload_id]["total_chunks"]

    return JSONResponse(content={"received": received, "total": total}, headers=_no_cache_headers())


@app.post("/api/upload/complete/{upload_id}")
async def chunked_upload_complete(upload_id: str):
    """Reassemble chunks and start processing."""
    with chunks_lock:
        upload = chunked_uploads.get(upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail={"error": "Upload session not found"})

    if upload["received_chunks"] < upload["total_chunks"]:
        raise HTTPException(status_code=400, detail={
            "error": f"Missing chunks: received {upload['received_chunks']}/{upload['total_chunks']}"
        })

    chunk_dir = Path(upload["chunk_dir"])
    # UUID-prefixed path for collision safety
    file_path = _unique_path(API_UPLOAD_FOLDER, upload["filename"])

    with open(file_path, 'wb') as out:
        for i in range(upload["total_chunks"]):
            cp = chunk_dir / f"chunk_{i:04d}"
            if not cp.exists():
                raise HTTPException(status_code=400, detail={"error": f"Missing chunk {i}"})
            out.write(cp.read_bytes())

    shutil.rmtree(chunk_dir, ignore_errors=True)
    with chunks_lock:
        chunked_uploads.pop(upload_id, None)

    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "filename": file_path.name,
            "original_filename": upload["filename"],
            "status": JobStatus.QUEUED,
            "created_at": datetime.now().isoformat(),
        }

    thread = threading.Thread(
        target=process_file_job,
        args=(job_id, file_path, upload["ai_enhancement"], upload["ai_image_processing"]),
    )
    thread.daemon = True
    thread.start()

    return JSONResponse(
        content={"job_id": job_id, "filename": upload["filename"]},
        headers=_no_cache_headers(),
    )


# ─── Async Upload ───────────────────────────────────────────────

@app.post("/api/upload")
async def upload_files(request: Request):
    """Upload one or more files for background processing."""
    form = await request.form()
    files = [v for k, v in form.multi_items() if k == "files[]" and hasattr(v, 'filename')]

    if not files:
        raise HTTPException(status_code=400, detail={"error": "No files provided"})

    ai_on = str(form.get("ai_enhancement", "true")).lower() == "true"
    ai_img = str(form.get("ai_image_processing", "true")).lower() == "true"

    job_ids = []
    skipped = []

    for file in files:
        if not hasattr(file, 'filename') or not file.filename:
            continue

        filename = file.filename
        if not _validate_ext(filename):
            skipped.append(filename)
            continue

        # UUID-prefixed path for collision safety
        file_path = _unique_path(API_UPLOAD_FOLDER, filename)
        content = await file.read()
        file_path.write_bytes(content)

        job_id = str(uuid.uuid4())
        with jobs_lock:
            jobs[job_id] = {
                "id": job_id,
                "filename": file_path.name,
                "original_filename": filename,
                "status": JobStatus.QUEUED,
                "created_at": datetime.now().isoformat(),
            }

        thread = threading.Thread(
            target=process_file_job,
            args=(job_id, file_path, ai_on, ai_img),
        )
        thread.daemon = True
        thread.start()
        job_ids.append(job_id)

    result = {"message": f"Uploaded {len(job_ids)} file(s)", "job_ids": job_ids}
    if skipped:
        result["skipped"] = skipped
        result["skipped_reason"] = "unsupported format"

    return JSONResponse(content=result, headers=_no_cache_headers())


# ─── Jobs ────────────────────────────────────────────────────────

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": "Job not found"})
    # Return sanitized view (no internal paths)
    return JSONResponse(content={
        "id": job["id"],
        "filename": job.get("original_filename", job["filename"]),
        "status": job["status"],
        "created_at": job.get("created_at"),
        "started_at": job.get("started_at"),
        "completed_at": job.get("completed_at"),
        "error": job.get("error"),
    }, headers=_no_cache_headers())


@app.get("/api/download/{job_id}")
async def download_file(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"error": "Job not found"})
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail={"error": "Job not completed"})

    output_file = Path(job["output_file"])
    if not output_file.exists():
        raise HTTPException(status_code=404, detail={"error": "Output file not found"})

    download_name = job.get("output_filename", output_file.name)
    return FileResponse(path=output_file, filename=download_name, media_type="text/markdown")


# ─── Error handlers ─────────────────────────────────────────────

@app.exception_handler(413)
async def request_entity_too_large(request, exc):
    return JSONResponse(status_code=413, content={"error": "File too large. Maximum size is 500MB"})


# ─── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("APP_PORT", os.environ.get("FLASK_PORT", "5000")))
    logger.info(f"Starting FastAPI on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
