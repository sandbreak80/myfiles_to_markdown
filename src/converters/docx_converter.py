"""DOCX document converter."""

from pathlib import Path
from typing import Dict
from loguru import logger
from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from PIL import Image
import io

from .base_converter import BaseConverter, DocumentContent


class DocxConverter(BaseConverter):
    """Converts DOCX documents to markdown."""
    
    def __init__(self, config: Dict):
        """Initialize DOCX converter.
        
        Args:
            config: Processing configuration dictionary
        """
        super().__init__(config)
    
    def convert(self, file_path: Path) -> DocumentContent:
        """Convert DOCX to markdown content.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            DocumentContent object with extracted content
        """
        logger.info(f"Converting DOCX: {file_path}")
        content = DocumentContent()
        
        try:
            # Open DOCX
            doc = Document(file_path)
            
            # Extract metadata
            core_props = doc.core_properties
            content.title = core_props.title or file_path.stem
            content.set_metadata('author', core_props.author or '')
            content.set_metadata('subject', core_props.subject or '')
            content.set_metadata('created', str(core_props.created) if core_props.created else '')
            
            # Process document elements
            image_count = 0
            
            for element in doc.element.body:
                # Handle paragraphs
                if isinstance(element, CT_P):
                    paragraph = Paragraph(element, doc)
                    text = paragraph.text.strip()
                    
                    if text:
                        # Check if it's a heading
                        if paragraph.style.name.startswith('Heading'):
                            level = paragraph.style.name.replace('Heading ', '')
                            try:
                                heading_level = int(level)
                                content.add_text(f"{'#' * heading_level} {text}")
                            except ValueError:
                                content.add_text(text)
                        else:
                            content.add_text(text)
                
                # Handle tables
                elif isinstance(element, CT_Tbl):
                    table = Table(element, doc)
                    table_md = self._table_to_markdown(table)
                    content.add_text(table_md)
            
            # Extract images
            if self.extract_images:
                for rel in doc.part.rels.values():
                    if "image" in rel.target_ref:
                        try:
                            image_data = rel.target_part.blob
                            pil_image = Image.open(io.BytesIO(image_data))
                            
                            # Try OCR
                            ocr_text = self.perform_ocr(pil_image)
                            
                            image_info = {
                                'index': image_count,
                                'has_ocr_text': bool(ocr_text),
                                'ocr_text': ocr_text,
                                'image': pil_image,
                                'format': pil_image.format
                            }
                            content.images.append(image_info)
                            image_count += 1
                            
                        except Exception as e:
                            logger.warning(f"Failed to extract image: {e}")
            
            logger.info(f"DOCX conversion complete. Extracted {image_count} images")
            
        except Exception as e:
            logger.error(f"Error converting DOCX: {e}")
            content.add_text(f"Error converting DOCX: {str(e)}")
        
        return content
    
    def _table_to_markdown(self, table: Table) -> str:
        """Convert a table to markdown format.
        
        Args:
            table: python-docx Table object
            
        Returns:
            Markdown formatted table
        """
        if not table.rows:
            return ""
        
        markdown = "\n"
        
        # Header row
        header_cells = [cell.text.strip() for cell in table.rows[0].cells]
        markdown += "| " + " | ".join(header_cells) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(header_cells)) + " |\n"
        
        # Data rows
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            markdown += "| " + " | ".join(cells) + " |\n"
        
        markdown += "\n"
        return markdown

