# MyFiles to Markdown - Project Overview

## Project Summary

**MyFiles to Markdown** is a local, privacy-focused document conversion tool that transforms office documents and PDFs into Obsidian-compatible markdown with AI enhancement.

### Key Goals

1. **Privacy First**: All processing happens locally - no cloud services
2. **AI Enhancement**: Automatic summaries, tags, and image descriptions
3. **Obsidian Integration**: Perfect markdown for Obsidian vaults
4. **Easy to Use**: Simple Docker setup, no complex configuration
5. **Comprehensive**: Support for common office formats

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    User's Computer                       │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Ollama     │◄────────│  Converter   │             │
│  │  Container   │  AI API │   Container  │             │
│  │              │         │              │             │
│  │  - LLM       │         │ - Python App │             │
│  │  - Models    │         │ - Converters │             │
│  └──────────────┘         │ - OCR        │             │
│                            └──────┬───────┘             │
│                                   │                     │
│  ┌──────────────┐         ┌──────▼───────┐             │
│  │    Input     │────────►│   Output     │             │
│  │  Documents   │         │   Markdown   │             │
│  └──────────────┘         └──────────────┘             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: User places documents in `input/` folder
2. **Detection**: Application scans for supported files
3. **Conversion**: 
   - Document → Text extraction
   - Document → Image extraction
   - Images → OCR processing
4. **AI Enhancement**:
   - Text → AI summary
   - Text → AI tags
   - Images → AI descriptions
5. **Output**: 
   - Markdown file with frontmatter
   - Extracted images in attachments folder
6. **Result**: Obsidian-compatible vault ready files

## Technical Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Runtime | Python 3.11 | Application logic |
| Container | Docker | Isolation & deployment |
| Orchestration | Docker Compose | Service management |
| AI | Ollama | Local LLM inference |
| Document Processing | Docling | Unified document understanding |
| Document Core | Docling Core | Document structure analysis |
| OCR | Tesseract | Text extraction (via Docling) |
| Images | Pillow | Image manipulation |
| Logging | Loguru | Application logging |

### File Format Support

| Format | Extension | Status | Features |
|--------|-----------|--------|----------|
| PDF | `.pdf` | ✅ Full | Text, images, metadata, tables, multi-page |
| Word | `.docx` | ✅ Full | Text, tables, images, headings |
| PowerPoint | `.pptx` | ✅ Full | Slides, notes, images |
| HTML | `.html`, `.htm` | ✅ Full | Web content conversion |

## Features in Detail

### 1. Document Conversion

#### Unified Docling Conversion
Docling provides advanced document understanding for all formats:

**PDF Conversion**
- Superior text extraction with layout analysis
- Advanced table detection and formatting
- Extracts embedded images
- Captures document metadata
- Handles multi-page documents with structure preservation

**DOCX Conversion**
- Preserves heading hierarchy
- Superior table conversion to markdown
- Extracts embedded images
- Maintains document structure
- Captures author and metadata

**PPTX Conversion**
- Converts each slide with layout awareness
- Extracts slide titles and content
- Includes speaker notes
- Extracts images from slides
- Maintains slide order and structure

**HTML Conversion**
- Web content to markdown
- Preserves semantic structure
- Handles complex layouts

### 2. OCR Processing

- Automatic text extraction from images
- Multi-language support
- Configurable confidence threshold
- Fallback to AI description if OCR fails
- Embedded image text preservation

### 3. AI Enhancement

#### Document Summaries
- Concise overview of content
- Key points extraction
- Context-aware summarization
- Configurable length

#### Tag Generation
- Automatic keyword extraction
- Relevant topic identification
- Configurable tag count
- Lowercase, clean format

#### Image Descriptions
- AI-generated alt text
- Context-aware descriptions
- Vision model support (llava)
- Fallback for failed OCR

### 4. Obsidian Integration

#### Frontmatter
```yaml
title: Document title
source_file: original.pdf
source_type: pdf
processed: 2025-11-10 14:30:00
ai_summary: AI-generated summary
tags: [keyword1, keyword2]
word_count: 1234
```

#### Markdown Features
- Proper heading hierarchy
- Table conversion
- Image embedding with [[wikilinks]]
- Summary callouts
- Clean, readable format

### 5. Configuration

#### Flexible Settings
- AI model selection
- OCR language configuration
- Output format customization
- Feature toggles
- Path configuration

#### Environment Variables
- Docker-compatible
- Override capability
- Secure credential handling

## Project Structure

```
myfiles_to_markdown/
├── docker-compose.yml       # Service orchestration
├── Dockerfile               # App container definition
├── requirements.txt         # Python dependencies
├── Makefile                 # Convenience commands
│
├── config/
│   └── config.yaml         # Application configuration
│
├── src/                    # Application source code
│   ├── main.py            # Entry point & orchestration
│   ├── config_manager.py  # Configuration handling
│   ├── ai_enhancer.py     # Ollama AI integration
│   ├── obsidian_writer.py # Markdown output generation
│   └── converters/        # Document converters
│       ├── __init__.py
│       ├── base_converter.py     # Base class
│       ├── pdf_converter.py      # PDF handler
│       ├── docx_converter.py     # Word handler
│       └── pptx_converter.py     # PowerPoint handler
│
├── scripts/               # Utility scripts
│   ├── setup.sh          # Initial setup
│   ├── run.sh            # Run converter
│   ├── clean.sh          # Cleanup
│   └── pull_model.sh     # Download AI models
│
├── input/                # Documents to convert (user-provided)
├── output/               # Converted markdown files
│   └── attachments/      # Extracted images
├── logs/                 # Application logs
│
└── docs/                 # Documentation
    ├── README.md         # Main documentation
    ├── QUICKSTART.md     # Getting started guide
    ├── USAGE.md          # Detailed usage
    ├── CONTRIBUTING.md   # Contribution guidelines
    └── CHANGELOG.md      # Version history
```

## Workflow

### First-Time Setup

1. Install Docker & Docker Compose
2. Run `make setup` or `./scripts/setup.sh`
3. Wait for model download (~2-3 GB)
4. Add documents to `input/`
5. Run `make run` or `./scripts/run.sh`

### Regular Usage

1. Add documents to `input/`
2. Run converter: `make run`
3. Get markdown from `output/`
4. Use in Obsidian vault

### Integration with Obsidian

1. Configure output path to Obsidian vault
2. Run converter
3. Files appear in Obsidian automatically
4. Use Dataview, tags, search, etc.

## Security & Privacy

### Privacy Features

✅ **100% Local Processing**
- No cloud services
- No external API calls
- No data transmission

✅ **No API Keys Required**
- Local Ollama instance
- No account creation
- No tracking

✅ **Data Stays Local**
- All files on your machine
- Docker containers isolated
- No persistent storage outside project

### Security Considerations

- Docker sandboxing
- Volume mount isolation
- No network exposure (except Ollama API locally)
- Open source - inspect the code
- No telemetry or analytics

## Performance

### Benchmarks (Approximate)

| Task | Time | Notes |
|------|------|-------|
| First setup | 10-15 min | Model download |
| PDF (10 pages) | 30-60 sec | With AI |
| DOCX (20 pages) | 20-40 sec | With AI |
| PPTX (15 slides) | 20-30 sec | With AI |
| Without AI | 5-10 sec | Much faster |

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB |
| Disk | 5 GB | 10 GB |
| CPU | 2 cores | 4+ cores |
| GPU | Not required | Speeds up AI |

### Optimization Tips

1. **Speed**: Use smaller models, disable AI
2. **Quality**: Use larger models, enable all features
3. **Batch**: Process multiple files together
4. **GPU**: Use Ollama with GPU support

## Extensibility

### Adding New Converters

1. Create new file in `src/converters/`
2. Inherit from `BaseConverter`
3. Implement `convert()` method
4. Register in `main.py`

### Custom AI Prompts

Edit `src/ai_enhancer.py` to customize:
- Summary generation prompts
- Tag extraction logic
- Image description templates

### Output Format

Modify `src/obsidian_writer.py` for:
- Custom frontmatter fields
- Different markdown structure
- Alternative image formats

## Limitations

### Current Limitations

1. **Excel**: Basic support only
2. **Complex Formatting**: Simplified in conversion
3. **Embedded Objects**: May not be preserved
4. **Large Files**: Memory constraints
5. **Encrypted Files**: Not supported

### Planned Improvements

- [ ] Better Excel/spreadsheet support
- [ ] RTF and ODT formats
- [ ] Web page extraction
- [ ] Custom AI prompts via config
- [ ] GUI interface
- [ ] API endpoints
- [ ] Progress tracking
- [ ] Incremental processing

## Use Cases

### 1. Obsidian Migration
Convert legacy documents into your Obsidian vault for note-taking and knowledge management.

### 2. AI/RAG Preparation
Prepare documents for AI ingestion and RAG (Retrieval-Augmented Generation) systems.

### 3. Document Search
Convert documents to searchable markdown for better discoverability.

### 4. Archive Modernization
Update old document formats to modern, portable markdown.

### 5. Knowledge Base
Build a markdown-based knowledge base from office documents.

## Community & Support

### Getting Help

1. Read documentation (README, QUICKSTART, USAGE)
2. Check CHANGELOG for known issues
3. Search existing GitHub issues
4. Open new issue with details

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to contribute
- Code style guidelines
- Development setup
- Pull request process

### Roadmap

See [GitHub Issues](link-to-issues) for:
- Planned features
- Known bugs
- Enhancement requests

## License

MIT License - See [LICENSE](LICENSE) file.

Free to use, modify, and distribute.

## Credits

Built with love for the Obsidian and AI communities.

### Technologies Used

- [Ollama](https://ollama.ai/) - Local LLM
- [Docling](https://github.com/DS4SD/docling) - IBM's document understanding library
- [Docling Core](https://github.com/DS4SD/docling-core) - Document structure analysis
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [Docker](https://www.docker.com/) - Containerization

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-10  
**Status**: Production Ready

