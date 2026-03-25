"""Tests for CSV, XLSX, and Image converters."""

from pathlib import Path
from converters.csv_converter import CsvConverter
from converters.xlsx_converter import XlsxConverter
from converters.image_converter import ImageConverter


class TestCsvConverter:
    def test_basic_conversion(self, sample_config, make_csv):
        conv = CsvConverter(sample_config)
        path = make_csv(rows=10)
        result = conv.convert(path)
        assert result.title == 'test'
        assert '10 rows' in result.text
        assert 'id' in result.text
        assert result.metadata['rows'] == 10
        assert result.metadata['columns'] == 3

    def test_truncation(self, sample_config, make_csv):
        sample_config['csv'] = {'max_rows': 5}
        conv = CsvConverter(sample_config)
        path = make_csv(rows=20)
        result = conv.convert(path)
        assert 'Showing first 5' in result.text
        assert result.metadata['rows'] == 20  # metadata has full count

    def test_no_truncation_small_file(self, sample_config, make_csv):
        sample_config['csv'] = {'max_rows': 100}
        conv = CsvConverter(sample_config)
        path = make_csv(rows=10)
        result = conv.convert(path)
        assert 'Showing first' not in result.text

    def test_column_info(self, sample_config, make_csv):
        conv = CsvConverter(sample_config)
        path = make_csv(rows=5)
        result = conv.convert(path)
        assert '**id**' in result.text
        assert '**name**' in result.text
        assert '**value**' in result.text

    def test_statistics(self, sample_config, make_csv):
        conv = CsvConverter(sample_config)
        path = make_csv(rows=10)
        result = conv.convert(path)
        assert '## Statistics' in result.text

    def test_bad_file(self, sample_config, tmp_dir):
        """Binary garbage is parsed by pandas as 0-row CSV, not an error."""
        conv = CsvConverter(sample_config)
        path = tmp_dir / 'bad.csv'
        path.write_bytes(b'\x00\x01\x02binary garbage')
        result = conv.convert(path)
        # pandas reads this as a 0-row file — not an error
        assert result.metadata['rows'] == 0


class TestXlsxConverter:
    def test_basic_conversion(self, sample_config, make_xlsx):
        conv = XlsxConverter(sample_config)
        path = make_xlsx(rows=10)
        result = conv.convert(path)
        assert result.title == 'test'
        assert result.metadata['sheet_count'] == 1
        assert 'TestSheet' in result.metadata['sheet_names']
        assert 'Person_0' in result.text

    def test_truncation(self, sample_config, make_xlsx):
        sample_config['xlsx'] = {'max_rows': 5, 'include_formulas': False}
        conv = XlsxConverter(sample_config)
        path = make_xlsx(rows=50)
        result = conv.convert(path)
        assert 'Showing first' in result.text or 'first 5' in result.text.lower()

    def test_metadata(self, sample_config, make_xlsx):
        conv = XlsxConverter(sample_config)
        path = make_xlsx(rows=5)
        result = conv.convert(path)
        assert 'file_size' in result.metadata
        assert result.metadata['sheet_count'] == 1

    def test_bad_file(self, sample_config, tmp_dir):
        conv = XlsxConverter(sample_config)
        path = tmp_dir / 'bad.xlsx'
        path.write_text('not an xlsx')
        result = conv.convert(path)
        assert 'Error' in result.text


class TestImageConverter:
    def test_png_conversion(self, sample_config, make_image):
        conv = ImageConverter(sample_config)
        path = make_image(fmt='PNG')
        result = conv.convert(path)
        assert result.title == 'test'
        assert '100 × 100' in result.text
        assert result.metadata['width'] == 100
        assert result.metadata['format'] == 'PNG'
        assert len(result.images) == 1

    def test_jpg_conversion(self, sample_config, make_image):
        conv = ImageConverter(sample_config)
        path = make_image(name='photo.jpg', fmt='JPEG')
        result = conv.convert(path)
        assert result.metadata['format'] == 'JPEG'

    def test_can_convert(self, sample_config):
        conv = ImageConverter(sample_config)
        assert conv.can_convert(Path('test.png')) is True
        assert conv.can_convert(Path('test.jpg')) is True
        assert conv.can_convert(Path('test.gif')) is True
        assert conv.can_convert(Path('test.pdf')) is False
        assert conv.can_convert(Path('test.mp4')) is False

    def test_image_metadata(self, sample_config, make_image):
        conv = ImageConverter(sample_config)
        path = make_image(width=200, height=300)
        result = conv.convert(path)
        assert result.metadata['width'] == 200
        assert result.metadata['height'] == 300
        assert result.metadata['mode'] == 'RGB'

    def test_bad_file(self, sample_config, tmp_dir):
        conv = ImageConverter(sample_config)
        path = tmp_dir / 'bad.png'
        path.write_text('not an image')
        result = conv.convert(path)
        assert 'Error' in result.text
