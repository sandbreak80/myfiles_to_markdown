"""Base converter class for all document types."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import pytesseract
from PIL import Image


class DocumentContent:
    """Container for extracted document content."""
    
    def __init__(self):
        self.text = ""
        self.images = []  # List of (image_data, description) tuples
        self.metadata = {}
        self.title = ""
        
    def add_text(self, text: str):
        """Add text content."""
        self.text += text + "\n\n"
    
    def add_image(self, image_path: str, description: str = ""):
        """Add image with optional description."""
        self.images.append((image_path, description))
    
    def set_metadata(self, key: str, value: any):
        """Set metadata field."""
        self.metadata[key] = value
    
    def get_text(self) -> str:
        """Get all text content."""
        return self.text.strip()


class BaseConverter(ABC):
    """Base class for document converters."""
    
    def __init__(self, config: Dict):
        """Initialize converter.
        
        Args:
            config: Processing configuration dictionary
        """
        self.config = config
        self.ocr_enabled = config.get('ocr', {}).get('enabled', True)
        self.ocr_language = config.get('ocr', {}).get('language', 'eng')
        self.extract_images = config.get('images', {}).get('extract', True)
        logger.info(f"{self.__class__.__name__} initialized")
    
    @abstractmethod
    def convert(self, file_path: Path) -> DocumentContent:
        """Convert document to markdown content.
        
        Args:
            file_path: Path to document file
            
        Returns:
            DocumentContent object with extracted content
        """
        pass
    
    def perform_ocr(self, image: Image.Image) -> str:
        """Perform OCR on an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Extracted text
        """
        if not self.ocr_enabled:
            return ""
        
        try:
            text = pytesseract.image_to_string(image, lang=self.ocr_language)
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return ""
    
    def save_image(self, image: Image.Image, output_dir: Path, base_name: str, index: int) -> str:
        """Save extracted image to file.
        
        Args:
            image: PIL Image object
            output_dir: Directory to save image
            base_name: Base name for the file
            index: Image index
            
        Returns:
            Path to saved image
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            image_filename = f"{base_name}_image_{index}.png"
            image_path = output_dir / image_filename
            image.save(image_path, "PNG")
            logger.debug(f"Saved image: {image_path}")
            return str(image_path)
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return ""
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

