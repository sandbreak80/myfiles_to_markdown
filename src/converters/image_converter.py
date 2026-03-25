"""Direct image file converter using existing OCR and Vision AI."""

from pathlib import Path
from typing import Optional
from PIL import Image
from loguru import logger

from converters.base_converter import DocumentContent


class ImageConverter:
    """Convert image files directly using OCR and Vision AI."""
    
    def __init__(self, config: dict):
        """Initialize image converter.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif', '.webp'}
    
    def can_convert(self, file_path: Path) -> bool:
        """Check if file can be converted.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported format
        """
        return file_path.suffix.lower() in self.supported_formats
    
    def convert(self, file_path: Path) -> DocumentContent:
        """Convert image file to DocumentContent.
        
        Args:
            file_path: Path to image file
            
        Returns:
            DocumentContent object with image info
        """
        logger.info(f"Converting image: {file_path.name}")
        
        try:
            # Open image with PIL
            image = Image.open(file_path)
            
            # Get image info
            width, height = image.size
            format_name = image.format or 'Unknown'
            mode = image.mode  # RGB, RGBA, L, etc.
            
            logger.info(f"Image: {width}x{height}, format: {format_name}, mode: {mode}")
            
            # Build content
            content_parts = []
            content_parts.append(f"# {file_path.stem}\n")
            content_parts.append(f"**Image File**: {file_path.name}\n")
            content_parts.append(f"**Dimensions**: {width} × {height} pixels")
            content_parts.append(f"**Format**: {format_name}")
            content_parts.append(f"**Color Mode**: {mode}\n")
            
            # Note about AI processing
            content_parts.append("\n## Image Analysis\n")
            content_parts.append("*This image will be processed with OCR and Vision AI during conversion.*\n")
            
            full_text = "\n".join(content_parts)
            
            # Create DocumentContent with the image
            # The image will be processed by AI enhancer for description
            content = DocumentContent()
            content.title = file_path.stem
            content.text = full_text
            content.metadata = {
                'width': width,
                'height': height,
                'format': format_name,
                'mode': mode,
                'file_size': file_path.stat().st_size
            }
            content.images = [{
                'index': 0,
                'image': image.copy(),  # Keep image in memory for AI processing
                'caption': f"{file_path.name} ({width}x{height})",
                'filename': file_path.name,
                'path': str(file_path),
                'format': format_name,
                'size': (width, height),
                'has_ocr_text': False,  # Will be populated by AI enhancer
                'ocr_text': ''
            }]
            
            logger.success(f"Image loaded: {width}x{height}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to convert image {file_path.name}: {e}")
            # Return minimal content on error
            content = DocumentContent()
            content.title = file_path.stem
            content.text = f"# {file_path.stem}\n\nError loading image: {str(e)}"
            content.metadata = {'error': str(e)}
            return content

