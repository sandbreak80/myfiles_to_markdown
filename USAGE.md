# Usage Guide

Detailed usage instructions and examples.

## Basic Usage

### Convert Single Document

```bash
# Place document in input
cp document.pdf input/

# Run converter
docker-compose up converter
```

### Convert Multiple Documents

```bash
# Copy all documents
cp ~/Documents/*.pdf input/
cp ~/Documents/*.docx input/

# Convert all at once
docker-compose up converter
```

### Continuous Processing

Keep the converter running to process files as you add them:

```bash
docker-compose up converter
# Add files to input/ folder while it's running
```

## Configuration

### Change AI Model

Edit `config/config.yaml`:

```yaml
ollama:
  model: "mistral:latest"
```

Then pull the model:

```bash
./scripts/pull_model.sh mistral:latest
```

### Disable AI Features

For faster processing without AI:

```yaml
processing:
  ai:
    generate_summary: false
    generate_tags: false
    describe_images: false
```

### OCR Settings

Configure OCR for different languages:

```yaml
processing:
  ocr:
    enabled: true
    language: "eng"  # eng, fra, deu, spa, etc.
    min_confidence: 60
```

Multiple languages:

```yaml
ocr:
  language: "eng+fra+deu"  # English, French, German
```

### Image Handling

```yaml
processing:
  images:
    extract: true
    max_size_mb: 10
    describe_failed_ocr: true
```

### Output Customization

```yaml
obsidian:
  frontmatter:
    add_source_file: true
    add_ai_summary: true
    add_ai_tags: true
  
  attachments_folder: "attachments"  # Change folder name
  embed_images: true
```

## Advanced Features

### Custom Output Directory

Edit `docker-compose.yml`:

```yaml
services:
  converter:
    volumes:
      - ./input:/app/input
      - /custom/path/output:/app/output  # Custom output
```

### Direct to Obsidian Vault

```yaml
volumes:
  - ./input:/app/input
  - ~/Documents/ObsidianVault/Imports:/app/output
```

### Process Subdirectories

The converter automatically processes subdirectories:

```
input/
├── project1/
│   ├── doc1.pdf
│   └── doc2.docx
└── project2/
    └── report.pdf
```

All files will be converted and flattened in output.

### Preserve Directory Structure (Coming Soon)

Future feature to maintain folder structure in output.

## File Format Support

### PDF Files

- ✅ Text extraction
- ✅ Image extraction
- ✅ Metadata extraction
- ✅ Multi-page support
- ✅ OCR on embedded images
- ⚠️ Form fields (basic support)

### Word Documents (.docx)

- ✅ Text extraction
- ✅ Heading preservation
- ✅ Table conversion
- ✅ Image extraction
- ✅ Metadata
- ⚠️ Complex formatting (simplified)

### PowerPoint (.pptx)

- ✅ Slide text
- ✅ Slide titles
- ✅ Speaker notes
- ✅ Images
- ✅ Slide numbers
- ⚠️ Animations (not preserved)

### Excel (.xlsx) - Basic Support

- ⚠️ Limited support (planned improvement)

## Output Examples

### PDF to Markdown

**Input**: `research-paper.pdf`

**Output**: `research-paper.md`

```markdown
---
title: "Machine Learning in Healthcare"
source_file: "research-paper.pdf"
source_type: "pdf"
author: "Dr. Smith"
page_count: 15
processed: "2025-11-10 14:30:00"
ai_summary: "This paper explores applications of machine learning..."
tags:
  - machine-learning
  - healthcare
  - ai
  - research
word_count: 4523
---

> [!summary] AI Summary
> This research paper investigates the applications of machine 
> learning in modern healthcare...

## Page 1

# Machine Learning in Healthcare
## Abstract

Recent advances in machine learning...
```

### PowerPoint to Markdown

**Input**: `quarterly-review.pptx`

**Output**: `quarterly-review.md`

```markdown
---
title: "Q3 2025 Business Review"
source_file: "quarterly-review.pptx"
source_type: "pptx"
slide_count: 12
processed: "2025-11-10 15:00:00"
ai_summary: "Quarterly business review covering revenue..."
tags:
  - business
  - quarterly
  - review
  - revenue
---

> [!summary] AI Summary
> This presentation reviews Q3 2025 business performance...

## Slide 1

**Q3 2025 Business Review**

Presented by: Sales Team
Date: November 10, 2025

---

## Slide 2

**Revenue Overview**

- Q3 Revenue: $2.5M
- Growth: 15% YoY
- Key Markets: US, EU

![[attachments/quarterly-review_img_001.png]]
**Description:** Revenue growth chart showing upward trend
```

## Performance Tips

### Optimize for Speed

1. Use smaller models:
   ```yaml
   model: "llama3.2:3b"
   ```

2. Disable AI features:
   ```yaml
   ai:
     generate_summary: false
   ```

3. Disable image extraction:
   ```yaml
   images:
     extract: false
   ```

### Optimize for Quality

1. Use larger models:
   ```yaml
   model: "llama3.2:latest"
   ```

2. Enable all features:
   ```yaml
   ai:
     generate_summary: true
     generate_tags: true
     describe_images: true
   ```

3. Use vision model for images:
   ```bash
   ./scripts/pull_model.sh llava:latest
   ```

### Batch Processing Best Practices

1. **Organize by type**: Group similar documents
2. **Start small**: Test with a few files first
3. **Monitor resources**: Check Docker Desktop for memory usage
4. **Process overnight**: Large batches can take time

## Integration with Obsidian

### Setup Obsidian Vault Integration

1. Create or use existing vault
2. Update docker-compose.yml:

```yaml
volumes:
  - ./input:/app/input
  - ~/ObsidianVault/Converted:/app/output
```

3. Run converter
4. Open Obsidian - files appear automatically!

### Obsidian Features

The generated markdown works great with:

- **Dataview**: Query by tags, dates, metadata
- **Graph View**: See connections
- **Search**: Full-text search
- **Templates**: Apply your own templates
- **Tags**: Auto-generated tags work natively

### Example Dataview Query

```dataview
TABLE source_type, processed, tags
FROM "Converted"
WHERE contains(tags, "business")
SORT processed DESC
```

## Maintenance

### Clean Up Old Files

```bash
# Remove processed files
./scripts/clean.sh

# Or manually
rm -rf output/*
rm -rf logs/*
```

### Update Models

```bash
# Pull latest version
./scripts/pull_model.sh llama3.2:latest
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose build --no-cache

# Restart
docker-compose up converter
```

## Monitoring and Logs

### View Live Logs

```bash
# All services
docker-compose logs -f

# Just converter
docker-compose logs -f converter

# Just Ollama
docker-compose logs -f ollama
```

### Log Files

Application logs are stored in `logs/` directory:

```bash
ls logs/
# converter_2025-11-10_14-30-00.log
```

### Debug Mode

Set in config:

```yaml
logging:
  level: "DEBUG"
```

## Troubleshooting

### Issue: "Permission denied"

```bash
# Fix permissions
chmod +x scripts/*.sh
```

### Issue: "Port already in use"

Change Ollama port in docker-compose.yml:

```yaml
ports:
  - "11435:11434"  # Use different port
```

### Issue: "Out of disk space"

Clean up Docker:

```bash
docker system prune -a
```

### Issue: "Conversion failed"

Check logs:

```bash
docker-compose logs converter
```

Common causes:
- Corrupted source file
- Unsupported format
- Memory limit reached

## API Usage (Coming Soon)

Future feature to expose REST API for programmatic access.

## Command Reference

```bash
# Setup
./scripts/setup.sh                    # Initial setup
./scripts/pull_model.sh MODEL         # Pull specific model

# Running
./scripts/run.sh                      # Run conversion
docker-compose up converter           # Same as above
docker-compose up -d converter        # Run in background

# Maintenance
./scripts/clean.sh                    # Clean output/logs
docker-compose down                   # Stop services
docker-compose restart ollama         # Restart Ollama

# Monitoring
docker-compose ps                     # Check status
docker-compose logs -f converter      # View logs
docker stats                          # Resource usage
```

## Best Practices

1. **Test first**: Always test with a small sample
2. **Backup originals**: Keep source files safe
3. **Review output**: AI isn't perfect, review results
4. **Organize input**: Use clear file names
5. **Update models**: Newer models are better
6. **Monitor resources**: Watch memory usage
7. **Read logs**: Logs help debug issues

## Getting Help

1. Check logs: `docker-compose logs -f`
2. Read README.md
3. Check GitHub issues
4. Open new issue with logs

---

For more information, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).

