"""Document converters package."""

from .docling_converter import (
    DoclingUnifiedConverter,
    DoclingPDFConverter,
    DoclingDocxConverter,
    DoclingPptxConverter
)
from .csv_converter import CsvConverter
from .image_converter import ImageConverter
from .jupyter_converter import JupyterConverter
from .email_converter import EmailConverter
from .xlsx_converter import XlsxConverter

# Aliases for compatibility
PDFConverter = DoclingPDFConverter
DocxConverter = DoclingDocxConverter
PptxConverter = DoclingPptxConverter

__all__ = [
    'DoclingUnifiedConverter',
    'PDFConverter',
    'DocxConverter',
    'PptxConverter',
    'CsvConverter',
    'ImageConverter',
    'JupyterConverter',
    'EmailConverter',
    'XlsxConverter'
]

