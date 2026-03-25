# Hardware Requirements

## ⚠️ Important: System Requirements

This application runs AI models **locally on your machine**. This requires significant computing power and memory.

## Minimum Recommended Hardware

### ✅ Recommended Configuration

| Component | Requirement |
|-----------|-------------|
| **CPU** | Apple M2 Pro or equivalent |
| **RAM** | **16 GB minimum** |
| **Storage** | 10 GB free space |
| **OS** | macOS, Linux, or Windows 11 |

### Why These Requirements?

**Memory Breakdown During Processing:**

```
Ollama (text model):        ~2-3 GB
Ollama (vision model):      ~6-8 GB
Docker containers:          ~2-4 GB
System overhead:            ~4-6 GB
─────────────────────────────────────
Total RAM needed:           12-18 GB active
```

## Tested Configurations

### ✅ Works Great

**MacBook Pro M2 Pro - 16GB RAM**
- Processing time: Normal (30-90 sec for PDFs)
- Vision AI: Works (30 sec per image)
- System stability: Excellent
- **Status:** ✅ **Recommended minimum**

**MacBook Pro M1 Max - 32GB RAM**
- Processing time: Fast
- Vision AI: Works great
- System stability: Excellent
- **Status:** ✅ **Ideal configuration**

**High-end Intel/AMD - 16GB+ RAM**
- Processing time: Good (slower than M-series)
- Vision AI: Works
- System stability: Good
- **Status:** ✅ **Works, but slower**

### ⚠️ May Struggle

**MacBook Air M2 - 8GB RAM**
- Processing time: Very slow (2-3x longer)
- Vision AI: May crash
- System stability: Unstable under load
- **Status:** ⚠️ **Not recommended**

**Older Intel i5/i7 - 8GB RAM**
- Processing time: Very slow
- Vision AI: Will likely fail
- System stability: Poor
- **Status:** ⚠️ **Too slow**

### ❌ Will Not Work Well

**Any System < 8GB RAM**
- **Status:** ❌ **Do not attempt**
- Ollama models won't load properly
- System will freeze/crash
- Not worth trying

## Performance Benchmarks

### On MacBook Pro M2 Pro (16GB RAM)

| Document Type | Size | Processing Time |
|---------------|------|-----------------|
| Small PDF (2 pages) | 75 KB | ~30 seconds |
| Medium PDF (30 pages) | 4.5 MB | ~90 seconds |
| DOCX with images | 500 KB | ~15 seconds |
| PPTX (text slides) | 600 KB | ~20 seconds |
| PPTX (2 image slides) | 600 KB | ~60 seconds |
| PPTX (50 image slides) | 50 MB | ~25 minutes |

### On MacBook Air M2 (8GB RAM)

| Document Type | Processing Time | Issues |
|---------------|-----------------|--------|
| Small PDF | ~60 seconds | Slow but works |
| Medium PDF | ~3-5 minutes | Very slow |
| PPTX with images | May crash | Memory errors |
| Vision AI | Usually fails | Out of memory |

## Resource Usage

### With Text Model Only (llama3.2:latest)

**RAM Usage:**
- Idle: ~2 GB
- Processing: ~4-6 GB
- Peak: ~8 GB

**Works on:** 8GB+ RAM (but 16GB recommended)

### With Vision Model (llava:7b)

**RAM Usage:**
- Idle: ~2 GB
- Processing: ~8-12 GB
- Peak: ~14-16 GB

**Requires:** 16GB+ RAM minimum

## If You Have Less Than 16GB RAM

### Option 1: Text-Only Mode

Skip the vision model and use OCR only:

```bash
# Only install text model
ollama pull llama3.2:latest

# Don't install llava:7b
# OCR will be used for images instead
```

**Trade-offs:**
- ✅ Uses less RAM (~6-8 GB)
- ✅ More stable
- ❌ Poor quality on image-heavy presentations
- ❌ No speaker notes understanding

### Option 2: Use Smaller Models

```bash
# Smaller text model
ollama pull llama3.2:3b  # 2GB instead of 4GB

# Skip vision entirely
```

**Trade-offs:**
- ✅ Uses less RAM
- ❌ Lower quality summaries and tags

### Option 3: Process One File at a Time

```bash
# Close ALL other applications
# Process single files only
./convert.sh document.pdf

# Don't batch process
```

### Option 4: Use Cloud Service (Future)

If your hardware can't handle it:
- Consider upgrading to 16GB+ RAM
- Or wait for cloud-hosted version
- Or use a more powerful computer

## Cloud/Server Deployment

### If Running on a Server

**Minimum specs:**
- 4-core CPU
- 16 GB RAM
- 20 GB disk space
- Ubuntu 20.04+ or similar

**Recommended:**
- 8-core CPU
- 32 GB RAM
- 50 GB SSD
- GPU optional (not currently utilized)

## Upgrade Recommendations

### If You're Buying New Hardware

**For this application:**

| Budget | Recommendation |
|--------|----------------|
| **Entry** | MacBook Air M3 - 16GB RAM (~$1,400) |
| **Recommended** | MacBook Pro M2 Pro - 16GB RAM (~$2,000) |
| **Ideal** | MacBook Pro M2 Max - 32GB RAM (~$3,000) |
| **PC** | High-end Intel/AMD - 32GB RAM (~$1,500) |

**RAM is more important than CPU for AI models!**

### For Existing Machines

**Can you upgrade RAM?**
- Apple Silicon Macs: ❌ No (soldered)
- Intel Macs: ⚠️ Some models (2012-2019)
- PCs/Workstations: ✅ Yes (usually)

If you can upgrade: **Add more RAM** (32GB total is ideal)

## Frequently Asked Questions

### Q: Can I run this on my MacBook Air M2 (8GB)?

**A:** Technically yes, but:
- It will be **very slow**
- Vision AI will **likely crash**
- You should use text-only mode
- **Not recommended** for regular use

### Q: Do I need a GPU?

**A:** No. Ollama uses CPU/unified memory on Apple Silicon. GPU support is not required.

### Q: What about Windows?

**A:** Works on Windows 11 with WSL2, but:
- Requires 16GB+ RAM
- Slightly slower than native Linux/Mac
- Docker Desktop needed

### Q: Can I use a desktop PC?

**A:** Yes! Any modern desktop with:
- 16GB+ RAM
- Recent CPU (Intel i5/i7, AMD Ryzen 5/7)
- Will work fine

### Q: What if I have 12GB RAM?

**A:** Borderline. You can try:
- Text model only (no vision)
- Close all other apps
- Process one file at a time
- Expect some slowness

## Summary

### ✅ Recommended: MacBook Pro M2 Pro + 16GB RAM

**You can reliably run:**
- Text model ✓
- Vision model ✓
- Batch processing ✓
- All features ✓

### ⚠️ Minimum: 16GB RAM (any modern CPU)

**You can run:**
- Text model ✓
- Vision model ✓ (slower on non-M-series)
- Most features ✓

### ❌ Not Recommended: < 16GB RAM

**You will experience:**
- Very slow processing ❌
- Frequent crashes ❌
- Vision AI failures ❌
- Frustration ❌

## Final Recommendation

**If you're serious about using this tool regularly:**

→ **Get 16GB+ RAM minimum**  
→ **MacBook Pro M2 Pro is the sweet spot**  
→ **32GB RAM is ideal for heavy use**

**If you have < 16GB RAM:**

→ **Use text-only mode**  
→ **Process one file at a time**  
→ **Consider upgrading hardware**

