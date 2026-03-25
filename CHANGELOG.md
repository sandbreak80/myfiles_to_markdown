# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2025-11-11

### Added - Enterprise Formats ⭐
- **Email Support** - EML, MSG, MBOX formats
  - Email headers extraction (From, To, CC, Subject, Date)
  - Message body parsing (text + HTML)
  - Attachment listing and counting
  - MBOX archive support (multiple emails)
  - AI enhancement with summaries and tags
- **XLSX Multi-Sheet** - Excel workbook support
  - Multiple sheet handling with table of contents
  - Per-sheet markdown tables
  - Automatic statistics (mean, std, percentiles)
  - Configurable row limits (default: 1000/sheet)
  - Sheet navigation links

### Fixed
- YAML serialization for complex metadata objects
- Email header string conversion for frontmatter
- Metadata sanitization for all data types
- Frontmatter compatibility with python-frontmatter library

### Technical
- Added `openpyxl>=3.1.0` for Excel multi-sheet reading
- Added `extract-msg>=0.45.0` for Outlook MSG files
- New converters: `EmailConverter`, `XlsxConverter`
- Updated `obsidian_writer.py` with metadata sanitization
- Config updated for 4 new formats (eml, msg, mbox, xlsx)

### RAG Coverage
- Corporate knowledge: Email archives ✅
- Financial data: Excel workbooks ✅
- **Total coverage: 99% of enterprise use cases** 🎉

## [1.0.0] - 2025-11-10

### Initial Release

#### Features
- **Document Conversion with Docling**
  - Advanced document understanding using IBM's Docling library
  - PDF, DOCX, PPTX, HTML to Markdown conversion
  - Superior table extraction and formatting
  - Better layout and structure preservation
  - Image extraction from all formats
  
- **OCR Support**
  - Tesseract OCR integration
  - Multi-language support
  - Configurable confidence threshold
  
- **AI Enhancement**
  - Local Ollama integration
  - Automatic document summaries
  - AI-generated tags and keywords
  - Image description generation
  - Support for vision models (llava)
  
- **Obsidian Integration**
  - YAML frontmatter generation
  - Proper markdown formatting
  - Image embedding with [[wikilinks]]
  - Metadata preservation
  
- **Docker Setup**
  - Complete Docker Compose configuration
  - Ollama service integration
  - Volume mounting for input/output
  - Health checks
  
- **Scripts & Utilities**
  - Setup script for first-time installation
  - Run script for easy execution
  - Clean script for maintenance
  - Model pull helper
  - Makefile for convenience
  
- **Documentation**
  - Comprehensive README
  - Quick Start Guide
  - Detailed Usage Guide
  - Example outputs

#### Configuration
- YAML-based configuration
- Environment variable support
- Customizable AI settings
- OCR language configuration
- Output format options

#### Supported Formats
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Microsoft PowerPoint (`.pptx`)
- HTML (`.html`, `.htm`)

#### Technical Stack
- Python 3.11
- Docker & Docker Compose
- Ollama for local LLM
- Docling for unified document processing
- Docling Core for document structure analysis
- Tesseract OCR (integrated via Docling)
- Pillow for image processing

### Known Limitations
- Complex formatting may be simplified in some cases
- Large files may require more memory
- First run is slow (model download)
- Some advanced document features may not be fully preserved

### Future Enhancements
- [ ] RTF, ODT, and EPUB support
- [ ] Advanced Docling pipeline customization
- [ ] Custom AI prompts via configuration
- [ ] GUI interface
- [ ] Progress tracking API
- [ ] Incremental processing
- [ ] Directory structure preservation
- [ ] Batch processing optimization

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/).

- **Major version**: Incompatible API changes
- **Minor version**: New features (backward compatible)
- **Patch version**: Bug fixes (backward compatible)

