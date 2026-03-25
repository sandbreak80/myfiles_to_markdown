# Troubleshooting Guide

## Ollama Issues

### Error: "Ollama is not running"

**Symptoms:**
```
Error: Ollama is not running!
Please start Ollama first
```

**Solutions:**

1. **Start Ollama:**
   ```bash
   ollama serve
   ```

2. **Check if it's running:**
   ```bash
   curl http://localhost:11434/api/tags
   # Should return JSON with model list
   ```

3. **Restart Ollama:**
   ```bash
   pkill ollama
   ollama serve
   ```

4. **Check port 11434:**
   ```bash
   lsof -i :11434
   # Should show ollama process
   ```

---

### Error: "Model not found"

**Symptoms:**
```
Model llama3.2:latest not found
Attempting to pull llama3.2:latest...
```

**Solution:**
```bash
# Pull the required models
ollama pull llama3.2:latest
ollama pull llava:7b

# Verify installation
ollama list
```

---

### Error: "Docker can't connect to host Ollama"

**Symptoms:**
```
ERROR: Could not connect to http://host.docker.internal:11434
```

**Solutions:**

**Mac/Windows:**
```bash
# Should work automatically, verify Ollama is running:
curl http://localhost:11434/api/tags
```

**Linux:**
Add to `docker-compose.yml`:
```yaml
services:
  converter:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

---

## Docker Issues

### Error: "Port 11434 already in use"

**Symptoms:**
```
Error: ports are not available: exposing port TCP 0.0.0.0:11434
```

**Cause:** Ollama is already running on the host (which is correct!)

**Solution:** 
This is expected! The converter is designed to connect to your **host's Ollama**, not run Ollama in Docker. No action needed if `ollama serve` is running on your host.

---

### Error: "No space left on device"

**Symptoms:**
```
ERROR: failed to solve: no space left on device
```

**Solutions:**

1. **Clean Docker:**
   ```bash
   docker system prune -a
   docker volume prune
   ```

2. **Check disk space:**
   ```bash
   df -h
   ```

3. **Models too large:**
   - llama3.2:latest = 2 GB
   - llava:7b = 4.7 GB
   - Docker images = ~2 GB
   - **Total needed:** ~10 GB free

---

## Conversion Issues

### Issue: Poor OCR quality on presentations

**Symptoms:**
- Garbled text like "SONI xn", "Broakouss #4"
- Presentation slides not readable

**Solution:**
Install vision model for better image understanding:
```bash
ollama pull llava:7b
# Or
ollama pull llama3.2-vision

# Then reconvert:
./convert.sh presentation.pptx
```

---

### Issue: No speaker notes in output

**Symptoms:**
- PowerPoint speaker notes missing from markdown

**Expected behavior:**
Speaker notes should appear in the Images section:
```markdown
**Speaker Notes:**
> Week at a glance, tech elevate attendees...
```

**Troubleshooting:**
1. Check if slides have speaker notes in original PPTX
2. Verify python-pptx is installed (it should be automatically)
3. Check logs for: `Extracted X chars of speaker notes`

---

### Issue: Images not extracted

**Symptoms:**
- `<!-- image -->` placeholders in markdown
- No images in `output/attachments/`

**Solutions:**

**For PPTX:**
- Fallback to python-pptx should happen automatically
- Check logs for: `Attempting PPTX image extraction with python-pptx`

**For PDF:**
- Some PDFs have embedded images that can't be extracted
- Vision model won't help here (images aren't accessible)

**For DOCX:**
- Most images should extract fine
- Check if images are actually embedded vs. linked

---

### Issue: Conversion is very slow

**Expected times:**
- Small PDF (2 pages): ~30-40 seconds
- Large PDF (29 pages): ~90 seconds
- PPTX with 2 images: ~1 minute
- PPTX with 50 images: ~25-30 minutes (AI vision)

**If slower than expected:**

1. **Check CPU usage:**
   ```bash
   top | grep ollama
   # Ollama uses ~100-200% CPU during generation
   ```

2. **Check if using vision model:**
   Vision AI (llava:7b) takes 20-30 seconds per image

3. **Disable AI features temporarily:**
   Edit `config/config.yaml`:
   ```yaml
   ai:
     enabled: false  # Skip AI enhancements for speed
   ```

---

## Output Issues

### Issue: Summary says "no document provided"

**Symptoms:**
```markdown
> Unfortunately, there is no document to summarize...
```

**Cause:** Document has < 50 words (image-heavy presentation)

**Solution:** This is expected for image-only slides. The vision AI descriptions provide the content.

---

### Issue: Tags have spaces

**Symptoms:**
```yaml
tags:
  - ai prompting  # WRONG
```

**Expected:**
```yaml
tags:
  - ai-prompting  # CORRECT
```

**Solution:** This should be automatic. If you see spaces, please report as a bug.

---

### Issue: Images not showing in Obsidian

**Symptoms:**
- `![[attachments/image.png]]` shows as broken link

**Solutions:**

1. **Copy attachments folder:**
   ```bash
   cp -r output/attachments ~/ObsidianVault/
   ```

2. **Or move entire output:**
   ```bash
   cp output/*.md ~/ObsidianVault/
   cp -r output/attachments ~/ObsidianVault/
   ```

3. **Check Obsidian settings:**
   - Settings → Files and Links → Default location for new attachments
   - Set to `attachments` subfolder

---

## Performance Optimization

### Speed up conversions

1. **Use smaller model:**
   ```yaml
   # config/config.yaml
   ai:
     model: "llama3.2:3b"  # Faster but slightly lower quality
   ```

2. **Disable vision for text-heavy docs:**
   Only PDFs and DOCXs = no vision needed, very fast

3. **Batch process overnight:**
   ```bash
   # Process large batches when you're not using the computer
   cp ~/Documents/*.* input/
   docker-compose run --rm converter python src/main.py
   ```

---

### Reduce memory usage

1. **Use smaller models:**
   - `llama3.2:3b` instead of `llama3.2:latest`
   - Skip vision model if not needed

2. **Process one file at a time:**
   ```bash
   for file in ~/Documents/*.pdf; do
       ./convert.sh "$file"
   done
   ```

---

## Debugging

### Enable debug logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Run conversion
./convert.sh document.pdf

# Or edit config/config.yaml
logging:
  level: DEBUG
```

### Check conversion logs

```bash
# View real-time logs
tail -f logs/converter.log

# Check Docker logs
docker-compose logs converter

# Check specific conversion
grep "Processing:" logs/converter.log
```

### Test individual components

```bash
# Test Ollama directly
ollama run llama3.2:latest "Test prompt"

# Test vision model
ollama run llava:7b "Describe this" --image test.png

# Test Docker connectivity
docker run --rm --add-host=host.docker.internal:host-gateway alpine \
  wget -O- http://host.docker.internal:11434/api/tags
```

---

## Getting Help

### Before reporting an issue

1. Check Ollama is running: `ollama list`
2. Check Docker is running: `docker ps`
3. Check disk space: `df -h`
4. Review logs: `tail -f logs/converter.log`
5. Try with a simple test file first

### Include in bug reports

- Operating system and version
- Docker version: `docker --version`
- Ollama version: `ollama --version`
- Models installed: `ollama list`
- Command you ran
- Error messages (full output)
- Sample file (if possible)

### Resources

- **Ollama:** [https://ollama.ai/](https://ollama.ai/)
- **Docling:** [https://github.com/DS4SD/docling](https://github.com/DS4SD/docling)
- **This project:** Check README.md and documentation

