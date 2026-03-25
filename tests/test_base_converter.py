"""Tests for base_converter.py — DocumentContent and BaseConverter."""

from converters.base_converter import DocumentContent, BaseConverter
from pathlib import Path
from PIL import Image


class TestDocumentContent:
    def test_init_defaults(self):
        dc = DocumentContent()
        assert dc.text == ""
        assert dc.images == []
        assert dc.metadata == {}
        assert dc.title == ""

    def test_add_text(self):
        dc = DocumentContent()
        dc.add_text("Hello")
        dc.add_text("World")
        assert "Hello" in dc.get_text()
        assert "World" in dc.get_text()

    def test_add_image(self):
        dc = DocumentContent()
        dc.add_image("/path/to/img.png", "A cat")
        assert len(dc.images) == 1
        assert dc.images[0] == ("/path/to/img.png", "A cat")

    def test_set_metadata(self):
        dc = DocumentContent()
        dc.set_metadata("author", "TestUser")
        assert dc.metadata["author"] == "TestUser"

    def test_get_text_strips(self):
        dc = DocumentContent()
        dc.add_text("  padded  ")
        assert dc.get_text() == "padded"

    def test_get_text_empty(self):
        dc = DocumentContent()
        assert dc.get_text() == ""


class TestBaseConverter:
    def test_cannot_instantiate_directly(self, sample_config):
        """BaseConverter is abstract and cannot be instantiated."""
        import pytest
        with pytest.raises(TypeError):
            BaseConverter(sample_config)

    def test_sanitize_filename(self, sample_config):
        class Stub(BaseConverter):
            def convert(self, fp):
                pass
        s = Stub(sample_config)
        assert s.sanitize_filename('file<name>:test') == 'file_name__test'
        assert s.sanitize_filename('normal_file') == 'normal_file'

    def test_ocr_disabled(self, sample_config):
        class Stub(BaseConverter):
            def convert(self, fp):
                pass
        sample_config['ocr']['enabled'] = False
        s = Stub(sample_config)
        img = Image.new('RGB', (10, 10))
        assert s.perform_ocr(img) == ""
