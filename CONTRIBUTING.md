# Contributing to MyFiles to Markdown

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check existing issues to avoid duplicates
2. Open a new issue with:
   - Clear description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - System information (OS, Docker version)
   - Relevant logs

### Feature Requests

We welcome feature requests! Please:

1. Check if the feature is already requested
2. Describe the use case
3. Explain why it would be valuable
4. Provide examples if possible

### Pull Requests

#### Before Starting

1. Open an issue to discuss major changes
2. Check that your idea aligns with project goals
3. Review existing code style

#### Development Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a pull request

#### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Comment complex logic

#### Testing

Before submitting:

1. Test with various document types
2. Verify Docker containers build
3. Check logs for errors
4. Test configuration changes
5. Update documentation

### Areas for Contribution

#### High Priority

- [ ] Additional file format support (RTF, ODT, etc.)
- [ ] Improved Excel/spreadsheet conversion
- [ ] Better table formatting
- [ ] Unit tests
- [ ] Integration tests

#### Medium Priority

- [ ] Web page extraction
- [ ] GUI interface
- [ ] API endpoint
- [ ] Progress tracking
- [ ] Incremental processing
- [ ] Custom AI prompts

#### Documentation

- [ ] More usage examples
- [ ] Video tutorials
- [ ] Troubleshooting guide
- [ ] Architecture documentation
- [ ] Translation to other languages

#### Nice to Have

- [ ] Performance optimizations
- [ ] Better error handling
- [ ] Configuration validation
- [ ] Health check endpoints
- [ ] Metrics and monitoring

## Development Setup

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd myfiles_to_markdown

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests (when available)
pytest
```

### Docker Development

```bash
# Build containers
docker-compose build

# Run with live code reloading
docker-compose up
```

### Project Structure

```
myfiles_to_markdown/
├── src/
│   ├── main.py              # Entry point
│   ├── config_manager.py    # Configuration
│   ├── ai_enhancer.py       # Ollama integration
│   ├── obsidian_writer.py   # Output writer
│   └── converters/          # Document converters
│       ├── base_converter.py
│       ├── pdf_converter.py
│       ├── docx_converter.py
│       └── pptx_converter.py
├── config/
│   └── config.yaml          # Default configuration
├── scripts/                 # Helper scripts
├── tests/                   # Tests (to be added)
└── docs/                    # Documentation
```

## Code Review Process

Pull requests will be reviewed for:

1. **Functionality**: Does it work as intended?
2. **Code Quality**: Is it clean and maintainable?
3. **Documentation**: Is it well documented?
4. **Tests**: Are there appropriate tests?
5. **Style**: Does it follow project conventions?

## Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: Add RTF file support
fix: Handle corrupt PDF files gracefully
docs: Update installation instructions
refactor: Simplify converter initialization
test: Add PDF converter tests
```

Prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style/formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

## Questions?

- Open an issue for general questions
- Check existing documentation
- Review closed issues for similar problems

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to MyFiles to Markdown! 🎉

