"""PDF document converter."""

from pathlib import Path
from typing import Dict
from loguru import logger
import fitz  # PyMuPDF
from PIL import Image
import io

from .base_converter import BaseConverter, DocumentContent


class PDFConverter(BaseConverter):
    """Converts PDF documents to markdown."""
    
    def __init__(self, config: Dict):
        """Initialize PDF converter.
        
        Args:
            config: Processing configuration dictionary
        """
        super().__init__(config)
    
    def convert(self, file_path: Path) -> DocumentContent:
        """Convert PDF to markdown content.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            DocumentContent object with extracted content
        """
        logger.info(f"Converting PDF: {file_path}")
        content = DocumentContent()
        
        try:
            # Open PDF with PyMuPDF
            doc = fitz.open(file_path)
            
            # Extract metadata
            metadata = doc.metadata
            if metadata:
                content.title = metadata.get('title', file_path.stem)
                content.set_metadata('author', metadata.get('author', ''))
                content.set_metadata('subject', metadata.get('subject', ''))
                content.set_metadata('page_count', doc.page_count)
            else:
                content.title = file_path.stem
                content.set_metadata('page_count', doc.page_count)
            
            # Process each page
            image_count = 0
            for page_num, page in enumerate(doc, 1):
                logger.debug(f"Processing page {page_num}/{doc.page_count}")
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    content.add_text(f"## Page {page_num}\n\n{text}")
                
                # Extract images if enabled
                if self.extract_images:
                    image_list = page.get_images()
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]
                            
                            # Convert to PIL Image
                            pil_image = Image.open(io.BytesIO(image_bytes))
                            
                            # Try OCR on the image
                            ocr_text = self.perform_ocr(pil_image)
                            
                            # Save image reference
                            image_info = {
                                'page': page_num,
                                'index': image_count,
                                'has_ocr_text': bool(ocr_text),
                                'ocr_text': ocr_text,
                                'image': pil_image,
                                'format': image_ext
                            }
                            content.images.append(image_info)
                            image_count += 1
                            
                        except Exception as e:
                            logger.warning(f"Failed to extract image on page {page_num}: {e}")
            
            doc.close()
            logger.info(f"PDF conversion complete. Extracted {image_count} images")
            
        except Exception as e:
            logger.error(f"Error converting PDF: {e}")
            content.add_text(f"Error converting PDF: {str(e)}")
        
        return content

