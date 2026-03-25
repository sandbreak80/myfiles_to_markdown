# Web UI Guide - v1.3.0

## 🌐 Access the Web Interface

**Local URL:** http://localhost:3143

## Features

### 🎨 Beautiful, Modern Interface
- Gradient design with smooth animations
- Drag-and-drop file upload
- Real-time processing status
- Auto-updating job queue
- One-click downloads

### 📁 Drag & Drop Upload
- Drag files directly onto the upload area
- Or click to browse and select files
- Upload multiple files at once
- Supports all 15+ formats

### 📊 Real-Time Status
- See all uploads in the processing queue
- Live status updates:
  - **Queued** - Waiting to process
  - **Processing** - Converting now
  - **Completed** - Ready to download
  - **Failed** - Error occurred
- Statistics dashboard at the top

### ⬇️ Easy Downloads
- Click "Download Markdown" button when conversion completes
- Files include AI summaries, tags, and descriptions
- Obsidian-compatible markdown format

---

## Supported Formats

The web UI supports all 15+ formats:

- **Documents:** PDF, DOCX, PPTX, HTML
- **Spreadsheets:** CSV, XLSX, XLS
- **Email:** EML, MSG, MBOX
- **Images:** PNG, JPG, JPEG, TIFF, BMP, GIF, WEBP
- **Code:** Jupyter Notebooks (.ipynb)

---

## How to Use

### 1. Start the Web UI

```bash
docker-compose up -d web
```

### 2. Open Your Browser

Navigate to: **http://localhost:3143**

### 3. Upload Files

**Option A: Drag & Drop**
- Drag one or more files onto the upload area
- Files start processing automatically

**Option B: Click to Browse**
- Click "Select Files" button
- Choose files from your computer
- Click Open

### 4. Monitor Progress

- Watch the status update in real-time
- Check the statistics at the top:
  - Total files processed
  - Currently queued
  - Currently processing
  - Completed
  - Failed

### 5. Download Results

- When status shows "Completed"
- Click the green "📥 Download Markdown" button
- File downloads to your browser's download folder

---

## Processing Times

| Format | Size | Estimated Time |
|--------|------|----------------|
| PDF (small) | 2 pages | ~30 seconds |
| PDF (medium) | 30 pages | ~90 seconds |
| PDF (large) | 161 pages | ~12 minutes |
| DOCX | Any | ~10-20 seconds |
| PPTX (text) | Any | ~20 seconds |
| PPTX (images) | Per image | ~30 seconds each |
| CSV | Any | ~5 seconds |
| XLSX | 3 sheets | ~10 seconds |
| Email | Single | ~15 seconds |
| Jupyter | 6 cells | ~10 seconds |
| Images | 400×300 | ~30 seconds |

---

## Tips & Tricks

### Batch Processing
- Upload multiple files at once
- They'll process in parallel
- Download each when ready

### Monitor Jobs
- The page auto-updates every 2 seconds
- No need to refresh manually
- Status changes appear automatically

### Optimal Workflow
1. Upload all your files at once
2. Let them process in the background
3. Download completed files as they finish
4. No waiting required!

---

## Troubleshooting

### Port Already in Use
If port 3143 is busy, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:5000"  # Change to any available port
```

Then restart:
```bash
docker-compose down web
docker-compose up -d web
```

### Web UI Not Loading
1. Check if container is running:
   ```bash
   docker ps | grep myfiles_web
   ```

2. Check logs:
   ```bash
   docker-compose logs web
   ```

3. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Upload Fails
- **File too large?** Max size is 100MB
- **Unsupported format?** Check supported formats list
- **Ollama not running?** Start Ollama first

### Processing Stuck
- Check Docker logs: `docker-compose logs web`
- Restart web service: `docker-compose restart web`
- Verify Ollama is responding

---

## Technical Details

### Architecture
- **Backend:** Flask (Python)
- **Frontend:** Vanilla JavaScript (no frameworks)
- **Processing:** Background threads
- **Storage:** Local filesystem
- **Updates:** Polling every 2 seconds

### Endpoints
- `GET /` - Main UI
- `POST /api/upload` - File upload
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/<id>` - Get job status
- `GET /api/download/<id>` - Download result
- `GET /api/stats` - Get statistics
- `GET /health` - Health check

### File Storage
- **Uploads:** `/app/uploads/` (inside container)
- **Output:** `/app/output/` (shared with host)
- **Logs:** `/app/logs/` (shared with host)

---

## Accessibility Features

### For Non-Technical Users
- Simple, intuitive interface
- No command-line required
- Visual feedback for all actions
- Clear status messages
- Easy file downloads

### For Power Users
- Batch upload support
- Real-time monitoring
- Full API access
- Docker integration
- CLI still available

---

## Security Notes

- **100% Local:** All processing happens on your machine
- **No Cloud:** Files never leave your computer
- **Privacy-First:** AI runs locally with Ollama
- **No Accounts:** No signup or login required
- **Open Source:** Full code transparency

---

## Comparison: Web UI vs CLI

| Feature | Web UI | CLI |
|---------|--------|-----|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Batch Processing** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Real-time Status** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Visual Feedback** | ⭐⭐⭐⭐⭐ | ⭐ |
| **Automation** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scripting** | ⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recommendation:**
- **Web UI:** Best for most users, especially non-technical
- **CLI:** Best for automation, scripting, batch jobs

---

## What's Next?

**Future Enhancements (v1.4+):**
- WebSocket for instant updates (no polling)
- Bulk download (zip all completed files)
- File preview before processing
- Processing history/analytics
- Custom AI settings per file
- Drag-and-drop from other apps

---

## Quick Reference

```bash
# Start web UI
docker-compose up -d web

# Stop web UI
docker-compose down web

# Restart web UI
docker-compose restart web

# View logs
docker-compose logs -f web

# Check health
curl http://localhost:3143/health
```

**Access:** http://localhost:3143

---

## Support

**Issues?**
- Check logs: `docker-compose logs web`
- Check Ollama: `curl http://localhost:11434/api/tags`
- Restart services: `docker-compose restart web`

**Questions?**
- Review this guide
- Check `README.md`
- See `TROUBLESHOOTING.md`

---

**Version 1.3.0** - Making document conversion accessible to everyone! 🚀

