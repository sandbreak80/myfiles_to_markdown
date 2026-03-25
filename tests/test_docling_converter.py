"""Tests for docling_converter.py — Docling unified converter."""

from pathlib import Path
from converters.docling_converter import DoclingUnifiedConverter


class TestDoclingInit:
    def test_fast_mode_default(self, sample_config):
        conv = DoclingUnifiedConverter(sample_config)
        assert conv.large_pdf_threshold == 30
        assert conv.xlarge_pdf_threshold == 80

    def test_custom_thresholds(self, sample_config):
        sample_config['docling'] = {
            'table_mode': 'accurate',
            'large_pdf_page_threshold': 10,
            'xlarge_pdf_page_threshold': 50,
        }
        conv = DoclingUnifiedConverter(sample_config)
        assert conv.large_pdf_threshold == 10
        assert conv.xlarge_pdf_threshold == 50


class TestDoclingPdfConversion:
    def test_small_pdf(self, sample_config, make_pdf):
        conv = DoclingUnifiedConverter(sample_config)
        path = make_pdf()
        result = conv.convert(path)
        # Minimal PDF should produce some content (even if minimal)
        assert result is not None
        assert result.title is not None

    def test_supports_format(self, sample_config):
        conv = DoclingUnifiedConverter(sample_config)
        assert conv.supports_format(Path("test.pdf")) is True
        assert conv.supports_format(Path("test.docx")) is True
        assert conv.supports_format(Path("test.pptx")) is True
        assert conv.supports_format(Path("test.mp4")) is False
        assert conv.supports_format(Path("test.csv")) is False


class TestDoclingDocxConversion:
    def test_docx_conversion(self, sample_config, make_docx):
        conv = DoclingUnifiedConverter(sample_config)
        path = make_docx()
        result = conv.convert(path)
        text = result.get_text()
        assert 'Test Document' in text or 'test' in text.lower()
        assert len(text) > 10
