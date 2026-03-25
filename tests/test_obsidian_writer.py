"""Tests for obsidian_writer.py."""

import html
from pathlib import Path
from unittest.mock import MagicMock
from converters.base_converter import DocumentContent
from obsidian_writer import ObsidianWriter


def _make_writer(tmp_dir, obsidian_config):
    ai = MagicMock()
    return ObsidianWriter(obsidian_config, ai, tmp_dir)


class TestFrontmatter:
    def test_basic_frontmatter(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        dc = DocumentContent()
        dc.title = "Test Doc"
        dc.add_text("Body content here.")
        source = Path("/fake/test.pdf")

        out = w.write_document(dc, source)
        text = out.read_text()
        assert 'title: Test Doc' in text
        assert 'source_file: test.pdf' in text
        assert 'source_type: pdf' in text
        assert 'processed:' in text

    def test_source_type_lowercase(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        dc = DocumentContent()
        dc.title = "Test"
        dc.add_text("Body")
        source = Path("/fake/file.PPTX")
        out = w.write_document(dc, source)
        text = out.read_text()
        assert 'source_type: pptx' in text

    def test_ai_analysis_in_frontmatter(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        dc = DocumentContent()
        dc.title = "AI Test"
        dc.add_text("Some content.")
        ai = {
            'description': 'A document about testing.',
            'summary': 'This doc covers tests.',
            'tags': ['testing', 'unit-tests'],
            'word_count': 42,
        }
        out = w.write_document(dc, Path("/f/t.pdf"), ai)
        text = out.read_text()
        assert 'description: A document about testing.' in text
        assert 'testing' in text
        assert 'unit-tests' in text
        assert 'word_count: 42' in text

    def test_no_ai(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        dc = DocumentContent()
        dc.title = "No AI"
        dc.add_text("Simple body.")
        out = w.write_document(dc, Path("/f/t.pdf"), None)
        text = out.read_text()
        assert 'summary' not in text.split('---')[1]  # not in frontmatter


class TestMarkdownBody:
    def test_html_unescape(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        dc = DocumentContent()
        dc.title = "HTML Test"
        dc.add_text("Sales &amp; Marketing &lt;team&gt;")
        out = w.write_document(dc, Path("/f/t.pdf"))
        text = out.read_text()
        assert 'Sales & Marketing <team>' in text
        assert '&amp;' not in text

    def test_image_placeholder_removal(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        dc = DocumentContent()
        dc.title = "Img Test"
        dc.add_text("Before <!-- image --> After")
        out = w.write_document(dc, Path("/f/t.pdf"))
        text = out.read_text()
        assert '<!-- image -->' not in text
        assert 'Before' in text and 'After' in text

    def test_summary_callout(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        dc = DocumentContent()
        dc.title = "Sum"
        dc.add_text("Body")
        ai = {'summary': 'A great summary.', 'description': 'd', 'tags': [], 'word_count': 5}
        out = w.write_document(dc, Path("/f/t.pdf"), ai)
        text = out.read_text()
        assert '> [!summary] Summary' in text
        assert '> A great summary.' in text


class TestSanitizeFilename:
    def test_removes_invalid_chars(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        result = w._sanitize_filename('file<>:"/\\|?*name')
        # All invalid chars replaced with _, then consecutive underscores collapsed
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert 'file' in result and 'name' in result

    def test_normal_filename(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        assert w._sanitize_filename('my_document') == 'my_document'


class TestDecorativeImageFilter:
    def test_decorative_detected(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        img = {'enhanced_description': 'A plain white background with no visible content', 'ocr_text': ''}
        assert w._is_decorative_image(img) is True

    def test_non_decorative(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        img = {'enhanced_description': 'A bar chart showing quarterly revenue', 'ocr_text': ''}
        assert w._is_decorative_image(img) is False

    def test_decorative_with_ocr_kept(self, tmp_dir, sample_obsidian_config):
        w = _make_writer(tmp_dir, sample_obsidian_config)
        img = {'enhanced_description': 'white background', 'ocr_text': 'Important text overlay here'}
        assert w._is_decorative_image(img) is False
