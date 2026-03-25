"""Main application entry point for document to markdown conversion."""

import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional
from loguru import logger
import magic

from config_manager import ConfigManager
from ai_enhancer import AIEnhancer
from obsidian_writer import ObsidianWriter
from converters import DoclingUnifiedConverter, CsvConverter, ImageConverter, JupyterConverter, EmailConverter, XlsxConverter


class DocumentProcessor:
    """Main document processing orchestrator."""
    
    def __init__(self, config_path: str = "/app/config/config.yaml"):
        """Initialize document processor.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config_manager = ConfigManager(config_path)
        
        # Get configuration sections (before logging setup)
        self.paths = self.config_manager.get_paths()
        self.processing_config = self.config_manager.get_processing_config()
        self.obsidian_config = self.config_manager.get_obsidian_config()
        self.ollama_config = self.config_manager.get_ollama_config()
        
        # Setup logging
        self._setup_logging()
        
        logger.info("=" * 80)
        logger.info("MyFiles to Markdown - Document Converter")
        logger.info("=" * 80)
        
        # Initialize components
        logger.info("Initializing components...")
        
        # AI Enhancer
        self.ai_enhancer = AIEnhancer(self.ollama_config)
        
        # Check Ollama availability
        if not self._wait_for_ollama():
            logger.error("Ollama is not available. AI features will be disabled.")
            self.ai_enabled = False
        else:
            self.ai_enabled = True
        
        # Output directory
        self.output_dir = Path(self.paths['output_dir'])
        
        # Obsidian Writer
        self.obsidian_writer = ObsidianWriter(
            self.obsidian_config,
            self.ai_enhancer,
            self.output_dir
        )
        
        # Initialize converters
        self.unified_converter = DoclingUnifiedConverter(self.processing_config)
        self.csv_converter = CsvConverter(self.processing_config)
        self.image_converter = ImageConverter(self.processing_config)
        self.jupyter_converter = JupyterConverter(self.processing_config)
        self.email_converter = EmailConverter(self.processing_config)
        self.xlsx_converter = XlsxConverter(self.processing_config)
        
        # Format mapping for supported extensions
        self.supported_formats = self.processing_config.get('supported_formats', [
            'pdf', 'docx', 'pptx', 'html', 'htm', 'csv', 'xlsx', 'xls',
            'png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'gif', 'webp',
            'ipynb', 'eml', 'msg', 'mbox'
        ])
        
        logger.info("Initialization complete!")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path(self.paths['log_dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # Add file handler
        logger.add(
            log_dir / "converter_{time}.log",
            rotation="10 MB",
            retention="7 days",
            level="DEBUG"
        )
    
    def _wait_for_ollama(self, max_retries: int = 10, delay: int = 5) -> bool:
        """Wait for Ollama to be available.
        
        Args:
            max_retries: Maximum number of retries
            delay: Delay between retries in seconds
            
        Returns:
            True if Ollama is available, False otherwise
        """
        logger.info("Checking Ollama availability...")
        
        for attempt in range(max_retries):
            if self.ai_enhancer.check_ollama_available():
                logger.info("Ollama is ready!")
                return True
            
            if attempt < max_retries - 1:
                logger.info(f"Waiting for Ollama... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
        
        return False
    
    def process_file(self, file_path: Path, enable_ai_images: bool = True) -> bool:
        """Process a single file.
        
        Args:
            file_path: Path to file to process
            enable_ai_images: Whether to enable AI vision for images
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"\nProcessing: {file_path.name}")
        
        try:
            # Determine file type
            file_ext = file_path.suffix[1:].lower()
            
            if file_ext not in self.supported_formats:
                logger.warning(f"Unsupported file type: {file_ext}")
                return False
            
            # Route to appropriate converter based on file type
            if file_ext == 'csv':
                content = self.csv_converter.convert(file_path)
            elif file_ext in ['xlsx', 'xls']:
                content = self.xlsx_converter.convert(file_path)
            elif file_ext in ['png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'gif', 'webp']:
                content = self.image_converter.convert(file_path)
            elif file_ext == 'ipynb':
                content = self.jupyter_converter.convert(file_path)
            elif file_ext in ['eml', 'msg', 'mbox']:
                content = self.email_converter.convert(file_path)
            else:
                # Use unified Docling converter for PDF, DOCX, PPTX, HTML
                content = self.unified_converter.convert(file_path)
            
            # AI enhancement if enabled
            ai_analysis = None
            if self.ai_enabled and self.processing_config.get('ai', {}).get('generate_summary', True):
                logger.info("Performing AI analysis...")
                text = content.get_text()
                if text and len(text) > 100:
                    ai_analysis = self.ai_enhancer.analyze_document(
                        text,
                        max_tags=self.processing_config.get('ai', {}).get('max_tags', 10)
                    )
                
                # Process images with OCR + AI vision (if enabled by user)
                if content.images and enable_ai_images:
                    logger.info(f"Enhancing {len(content.images)} images with OCR + AI vision...")
                    doc_context = content.title or file_path.stem
                    
                    for img_info in content.images:
                        # Get enhanced description using OCR + vision
                        enhanced_desc = self.ai_enhancer.describe_image(
                            image_path=img_info.get('path', ''),
                            ocr_text=img_info.get('ocr_text', ''),
                            context=doc_context
                        )
                        # Store enhanced description
                        img_info['enhanced_description'] = enhanced_desc
                        
                    logger.info(f"✓ Enhanced {len(content.images)} images")
                elif content.images and not enable_ai_images:
                    logger.info(f"AI image processing disabled - keeping OCR text only for {len(content.images)} images")
            
            # Write Obsidian markdown
            output_path = self.obsidian_writer.write_document(
                content,
                file_path,
                ai_analysis
            )
            
            logger.success(f"✓ Successfully converted: {file_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to process {file_path.name}: {e}")
            return False
    
    def discover_files(self, input_dir: Path) -> List[Path]:
        """Discover files to process in input directory.
        
        Args:
            input_dir: Input directory path
            
        Returns:
            List of file paths
        """
        supported_exts = self.processing_config.get('supported_formats', [])
        files = []
        
        for ext in supported_exts:
            pattern = f"*.{ext}"
            files.extend(input_dir.rglob(pattern))
        
        logger.info(f"Found {len(files)} files to process")
        return files
    
    def convert_single_file(self, input_file: Path, output_file: Optional[Path] = None) -> bool:
        """Convert a single file.
        
        Args:
            input_file: Path to input file
            output_file: Optional output path, defaults to same name with .md extension
            
        Returns:
            True if successful, False otherwise
        """
        if not input_file.exists():
            logger.error(f"Input file does not exist: {input_file}")
            return False
        
        # Process the file
        success = self.process_file(input_file)
        
        if success and output_file:
            # If custom output location specified, move the file
            expected_output = self.output_dir / f"{input_file.stem}.md"
            if expected_output.exists() and output_file != expected_output:
                import shutil
                output_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(expected_output), str(output_file))
                logger.info(f"Output moved to: {output_file}")
        
        return success
    
    def run(self, input_file: Optional[str] = None):
        """Run the document processor.
        
        Args:
            input_file: Optional single file to process. If not provided, processes input directory.
        """
        # Single file mode
        if input_file:
            file_path = Path(input_file)
            logger.info(f"Processing single file: {file_path}")
            
            if self.convert_single_file(file_path):
                output_path = self.output_dir / f"{file_path.stem}.md"
                logger.success(f"\n✓ Conversion successful!")
                logger.info(f"Input:  {file_path}")
                logger.info(f"Output: {output_path}")
                return 0
            else:
                logger.error(f"\n✗ Conversion failed!")
                return 1
        
        # Batch directory mode
        input_dir = Path(self.paths['input_dir'])
        
        if not input_dir.exists():
            logger.error(f"Input directory does not exist: {input_dir}")
            logger.info("Creating input directory. Please add files and restart.")
            input_dir.mkdir(parents=True, exist_ok=True)
            return 1
        
        # Discover files
        files = self.discover_files(input_dir)
        
        if not files:
            logger.warning("No files found to process.")
            logger.info(f"Supported formats: {', '.join(self.supported_formats)}")
            logger.info(f"Add files to: {input_dir}")
            logger.info("\nUsage: docker run ... /app/input/yourfile.pdf")
            return 1
        
        # Process files
        logger.info(f"\nProcessing {len(files)} files...")
        logger.info(f"Output directory: {self.output_dir}\n")
        
        success_count = 0
        fail_count = 0
        
        for file_path in files:
            logger.info(f"\n[{success_count + fail_count + 1}/{len(files)}] Processing: {file_path.name}")
            if self.process_file(file_path):
                success_count += 1
            else:
                fail_count += 1
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("Processing Complete!")
        logger.info("=" * 80)
        logger.info(f"Total files: {len(files)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {fail_count}")
        logger.info(f"Output location: {self.output_dir}")
        logger.info("=" * 80)
        
        return 0 if fail_count == 0 else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert documents to Obsidian-compatible markdown with AI enhancement'
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input file to convert (PDF, DOCX, PPTX, HTML). If not provided, processes input directory.'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (optional, defaults to input name with .md extension)'
    )
    parser.add_argument(
        '-c', '--config',
        default='/app/config/config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    try:
        processor = DocumentProcessor(args.config)
        
        # Single file mode
        if args.input_file:
            input_path = Path(args.input_file)
            output_path = Path(args.output) if args.output else None
            
            if output_path:
                success = processor.convert_single_file(input_path, output_path)
            else:
                success = processor.convert_single_file(input_path)
            
            sys.exit(0 if success else 1)
        
        # Batch mode
        else:
            exit_code = processor.run()
            sys.exit(exit_code)
            
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()

