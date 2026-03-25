"""Extended obsidian_writer tests — image handling, table cleaning, metadata edge cases."""

from pathlib import Path
from unittest.mock import MagicMock
from PIL import Image
from converters.base_converter import DocumentContent
from obsidian_writer import ObsidianWriter


def _make_writer(tmp_dir, config=None):
    if config is None:
        config = {
            'frontmatter': {
                'add_source_file': True, 'add_created_date': True,
                'add_processed_date': True, 'add_ai_summary': True, 'add_ai_tags': True,
            },
            'preserve_filename': True, 'sanitize_filenames': True,
            'attachments_folder': 'attachments', 'embed_images': True,
        }
    return ObsidianWriter(config, MagicMock(), tmp_dir)


class TestImageSaving:
    def test_save_image(self, tmp_dir):
        w = _make_writer(tmp_dir)
        img = Image.new('RGB', (50, 50), color='blue')
        path = w._save_image(img, 'test_doc', 1)
        assert path != ""
        assert Path(path).exists()
        assert 'test_doc_img_001.png' in path

    def test_save_image_creates_dir(self, tmp_dir):
        w = _make_writer(tmp_dir)
        img = Image.new('RGB', (10, 10))
        path = w._save_image(img, 'doc', 5)
        assert Path(path).exists()


class TestImageEmbedding:
    def test_images_embedded_in_output(self, tmp_dir):
        w = _make_writer(tmp_dir)
        dc = DocumentContent()
        dc.title = "ImgDoc"
        dc.add_text("Main content.")
        img = Image.new('RGB', (20, 20))
        dc.images = [{
            'index': 0, 'image': img, 'caption': 'Test chart',
            'filename': 'chart.png', 'path': '/tmp/chart.png',
            'format': 'PNG', 'size': (20, 20),
            'has_ocr_text': False, 'ocr_text': '',
            'enhanced_description': 'A test chart showing data',
        }]
        out = w.write_document(dc, Path("/f/doc.pdf"))
        text = out.read_text()
        assert '![[attachments/' in text
        assert 'A test chart showing data' in text
        assert '## Images' in text

    def test_images_with_speaker_notes(self, tmp_dir):
        w = _make_writer(tmp_dir)
        dc = DocumentContent()
        dc.title = "PPT"
        dc.add_text("Slide content.")
        img = Image.new('RGB', (20, 20))
        dc.images = [{
            'index': 0, 'image': img, 'caption': '',
            'filename': 'slide.png', 'path': '/tmp/slide.png',
            'format': 'PNG', 'size': (20, 20),
            'has_ocr_text': False, 'ocr_text': '',
            'enhanced_description': 'Slide with title',
            'speaker_notes': 'Talk about the quarterly results.',
        }]
        out = w.write_document(dc, Path("/f/pres.pptx"))
        text = out.read_text()
        assert '**Speaker Notes:**' in text
        assert 'quarterly results' in text

    def test_images_with_ocr_text_fallback(self, tmp_dir):
        w = _make_writer(tmp_dir)
        dc = DocumentContent()
        dc.title = "OCR"
        dc.add_text("Body.")
        img = Image.new('RGB', (20, 20))
        dc.images = [{
            'index': 0, 'image': img, 'caption': '',
            'filename': 'ocr.png', 'path': '/tmp/ocr.png',
            'format': 'PNG', 'size': (20, 20),
            'has_ocr_text': True, 'ocr_text': 'OCR extracted content here',
            'enhanced_description': '',
        }]
        out = w.write_document(dc, Path("/f/doc.pdf"))
        text = out.read_text()
        assert 'OCR extracted content here' in text

    def test_no_images_no_section(self, tmp_dir):
        w = _make_writer(tmp_dir)
        dc = DocumentContent()
        dc.title = "NoImg"
        dc.add_text("Just text.")
        dc.images = []
        out = w.write_document(dc, Path("/f/doc.pdf"))
        text = out.read_text()
        assert '## Images' not in text

    def test_embed_images_disabled(self, tmp_dir):
        config = {
            'frontmatter': {
                'add_source_file': True, 'add_created_date': True,
                'add_processed_date': True, 'add_ai_summary': True, 'add_ai_tags': True,
            },
            'preserve_filename': True, 'sanitize_filenames': True,
            'attachments_folder': 'attachments', 'embed_images': False,
        }
        w = _make_writer(tmp_dir, config)
        dc = DocumentContent()
        dc.title = "NoEmbed"
        dc.add_text("Body.")
        img = Image.new('RGB', (20, 20))
        dc.images = [{
            'index': 0, 'image': img, 'caption': 'test',
            'filename': 'x.png', 'path': '/tmp/x.png',
            'format': 'PNG', 'size': (20, 20),
            'has_ocr_text': False, 'ocr_text': '',
        }]
        out = w.write_document(dc, Path("/f/doc.pdf"))
        text = out.read_text()
        assert '## Images' not in text


class TestMalformedTableCleaning:
    def test_isolated_pipe_removed(self, tmp_dir):
        w = _make_writer(tmp_dir)
        text = "Some text\n| broken fragment |\nMore text"
        result = w._clean_malformed_tables(text)
        assert '| broken fragment |' not in result

    def test_valid_table_preserved(self, tmp_dir):
        w = _make_writer(tmp_dir)
        text = "| H1 | H2 |\n|---|---|\n| A | B |"
        result = w._clean_malformed_tables(text)
        assert '| H1 | H2 |' in result
        assert '| A | B |' in result

    def test_normal_text_unchanged(self, tmp_dir):
        w = _make_writer(tmp_dir)
        text = "Normal paragraph.\n\nAnother paragraph."
        result = w._clean_malformed_tables(text)
        assert result == text


class TestMetadataEdgeCases:
    def test_complex_metadata_types(self, tmp_dir):
        w = _make_writer(tmp_dir)
        dc = DocumentContent()
        dc.title = "Meta"
        dc.add_text("Body")
        dc.metadata = {
            'simple_str': 'hello',
            'number': 42,
            'boolean': True,
            'list_val': ['a', 'b', 'c'],
            'dict_val': {'key': 'value'},
            'complex_obj': object(),
        }
        out = w.write_document(dc, Path("/f/t.pdf"))
        text = out.read_text()
        assert 'simple_str: hello' in text
        assert 'number: 42' in text

    def test_auto_generated_filename(self, tmp_dir):
        config = {
            'frontmatter': {
                'add_source_file': True, 'add_created_date': True,
                'add_processed_date': True, 'add_ai_summary': True, 'add_ai_tags': True,
            },
            'preserve_filename': False, 'sanitize_filenames': True,
            'attachments_folder': 'attachments', 'embed_images': True,
        }
        w = _make_writer(tmp_dir, config)
        dc = DocumentContent()
        dc.title = "Auto"
        dc.add_text("Body")
        out = w.write_document(dc, Path("/f/t.pdf"))
        assert 'document_' in out.name
