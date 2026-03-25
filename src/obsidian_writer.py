"""Obsidian vault markdown writer with AI enhancement."""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
import frontmatter
from loguru import logger

from converters.base_converter import DocumentContent
from ai_enhancer import AIEnhancer


class ObsidianWriter:
    """Writes documents as Obsidian-compatible markdown with AI enhancements."""
    
    def __init__(self, config: Dict, ai_enhancer: AIEnhancer, output_dir: Path):
        """Initialize Obsidian writer.
        
        Args:
            config: Obsidian configuration dictionary
            ai_enhancer: AI enhancer instance
            output_dir: Output directory path
        """
        self.config = config
        self.ai_enhancer = ai_enhancer
        self.output_dir = Path(output_dir)
        self.attachments_dir = self.output_dir / config.get('attachments_folder', 'attachments')
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Obsidian writer initialized. Output: {self.output_dir}")
    
    def write_document(self, content: DocumentContent, source_file: Path, 
                      ai_analysis: Dict = None) -> Path:
        """Write document as Obsidian markdown with AI enhancements.
        
        Args:
            content: DocumentContent object
            source_file: Original source file path
            ai_analysis: Optional AI analysis results
            
        Returns:
            Path to created markdown file
        """
        logger.info(f"Writing Obsidian markdown for: {source_file.name}")
        
        # Generate filename
        if self.config.get('preserve_filename', True):
            base_name = source_file.stem
            if self.config.get('sanitize_filenames', True):
                base_name = self._sanitize_filename(base_name)
        else:
            base_name = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_file = self.output_dir / f"{base_name}.md"
        
        # Build frontmatter
        metadata = self._build_frontmatter(content, source_file, ai_analysis)
        
        # Build markdown body
        body = self._build_markdown_body(content, base_name, ai_analysis)
        
        # Create post with frontmatter
        post = frontmatter.Post(body, **metadata)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        logger.info(f"Markdown written to: {output_file}")
        return output_file
    
    def _build_frontmatter(self, content: DocumentContent, source_file: Path, 
                          ai_analysis: Dict = None) -> Dict:
        """Build frontmatter metadata.
        
        Args:
            content: DocumentContent object
            source_file: Source file path
            ai_analysis: AI analysis results
            
        Returns:
            Frontmatter dictionary
        """
        frontmatter_config = self.config.get('frontmatter', {})
        metadata = {}
        
        # Title
        metadata['title'] = content.title or source_file.stem
        
        # Source file
        if frontmatter_config.get('add_source_file', True):
            metadata['source_file'] = source_file.name
            metadata['source_type'] = source_file.suffix[1:].lower()  # Remove dot, normalize case
        
        # Dates
        if frontmatter_config.get('add_created_date', True):
            if 'created' in content.metadata and content.metadata['created']:
                metadata['created'] = content.metadata['created']
        
        if frontmatter_config.get('add_processed_date', True):
            metadata['processed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # AI enhancements
        if ai_analysis:
            # Short description
            if ai_analysis.get('description'):
                metadata['description'] = ai_analysis['description']
            
            # Summary (max 100 words)
            if frontmatter_config.get('add_ai_summary', True) and ai_analysis.get('summary'):
                metadata['summary'] = ai_analysis['summary']
            
            # Tags (Obsidian-compatible with hyphens)
            if frontmatter_config.get('add_ai_tags', True) and ai_analysis.get('tags'):
                metadata['tags'] = ai_analysis['tags']
            
            if 'word_count' in ai_analysis:
                metadata['word_count'] = ai_analysis['word_count']
        
        # Additional metadata from document (sanitize for YAML)
        for key, value in content.metadata.items():
            if key not in metadata and value is not None:
                # Ensure value is YAML-safe
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
                elif isinstance(value, (list, tuple)):
                    # Convert to list of simple types
                    metadata[key] = [str(v) if not isinstance(v, (str, int, float, bool)) else v for v in value]
                elif isinstance(value, dict):
                    # Convert dict values to simple types
                    metadata[key] = {k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v 
                                   for k, v in value.items()}
                else:
                    # Convert complex objects to string
                    metadata[key] = str(value)
        
        return metadata
    
    def _build_markdown_body(self, content: DocumentContent, base_name: str, 
                            ai_analysis: Dict = None) -> str:
        """Build markdown body content.
        
        Args:
            content: DocumentContent object
            base_name: Base name for attachments
            ai_analysis: AI analysis results
            
        Returns:
            Markdown body string
        """
        body_parts = []
        
        # Add AI summary as callout if available (now concise - max 100 words)
        if ai_analysis and ai_analysis.get('summary'):
            # Format summary for callout (preserve line breaks)
            summary_lines = ai_analysis['summary'].split('\n')
            formatted_summary = '\n> '.join(line for line in summary_lines if line.strip())
            body_parts.append(f"> [!summary] Summary\n> {formatted_summary}\n")
        
        # Add main content (clean up image placeholders from Docling)
        main_text = content.get_text()
        
        # Remove <!-- image --> placeholders left by Docling
        # These are typically decorative graphics (icons, borders, logos)
        # that we don't extract as actual images
        placeholder_count = main_text.count("<!-- image -->")
        if placeholder_count > 0:
            logger.debug(f"Removing {placeholder_count} image placeholders from main text")
            main_text = main_text.replace("<!-- image -->", "")
            # Clean up extra blank lines
            main_text = "\n".join(line for line in main_text.split("\n") if line.strip() or line == "")
        
        # Clean up broken/malformed tables from Docling
        main_text = self._clean_malformed_tables(main_text)

        # Unescape HTML entities left by Docling (e.g. &amp; &lt; &gt;)
        import html
        main_text = html.unescape(main_text)

        body_parts.append(main_text)
        
        # Add images section if there are any
        if content.images and self.config.get('embed_images', True):
            # Filter out decorative/blank images
            meaningful_images = []
            skipped_count = 0
            
            for image_info in content.images:
                if self._is_decorative_image(image_info):
                    skipped_count += 1
                    logger.debug(f"Skipping decorative image: {image_info.get('enhanced_description', '')[:50]}...")
                else:
                    meaningful_images.append(image_info)
            
            if skipped_count > 0:
                logger.info(f"Filtered out {skipped_count} decorative/blank images")
            
            if meaningful_images:
                body_parts.append("\n---\n\n## Images\n")
                
                for idx, image_info in enumerate(meaningful_images, 1):
                    # Save image
                    image_path = self._save_image(
                        image_info['image'], 
                        base_name, 
                        idx
                    )
                    
                    if image_path:
                        # Create relative path for Obsidian
                        rel_path = Path(image_path).relative_to(self.output_dir)
                        
                        # Add image with enhanced description
                        body_parts.append(f"\n### Image {idx}\n")
                        body_parts.append(f"![[{rel_path}]]\n")
                        
                        # Use enhanced description if available (OCR + AI vision)
                        enhanced_desc = image_info.get('enhanced_description', '')
                        if enhanced_desc and not enhanced_desc.startswith('[Image'):
                            body_parts.append(f"> {enhanced_desc}\n")
                        elif image_info.get('ocr_text'):
                            body_parts.append(f"> {image_info['ocr_text']}\n")
                        elif image_info.get('caption'):
                            body_parts.append(f"> {image_info['caption']}\n")
                    
                    # Add speaker notes if available
                    speaker_notes = image_info.get('speaker_notes', '')
                    if speaker_notes:
                        body_parts.append(f"\n**Speaker Notes:**\n> {speaker_notes}\n")
        
        return "\n".join(body_parts)
    
    def _save_image(self, image, base_name: str, index: int) -> str:
        """Save image to attachments folder.
        
        Args:
            image: PIL Image object
            base_name: Base name for file
            index: Image index
            
        Returns:
            Path to saved image
        """
        try:
            image_filename = f"{base_name}_img_{index:03d}.png"
            image_path = self.attachments_dir / image_filename
            image.save(image_path, "PNG")
            logger.debug(f"Saved image: {image_path}")
            return str(image_path)
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return ""
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Replace multiple underscores/spaces
        filename = ' '.join(filename.split())
        filename = '_'.join(filter(None, filename.split('_')))
        
        return filename.strip()
    
    def _clean_malformed_tables(self, text: str) -> str:
        """Clean up malformed table fragments from Docling.
        
        Args:
            text: Markdown text that may contain broken tables
            
        Returns:
            Cleaned text with malformed tables removed or fixed
        """
        import re
        
        lines = text.split('\n')
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Detect table row fragments (lines starting with |)
            if line.strip().startswith('|'):
                # Check if this is a standalone broken table row
                # (no header separator above, isolated from other table rows)
                
                # Look back for context
                has_table_above = False
                if i > 0:
                    prev_line = lines[i-1].strip()
                    # Check if previous line is part of a table
                    if prev_line.startswith('|') or re.match(r'^\|?[-:\s|]+\|?$', prev_line):
                        has_table_above = True
                
                # Look ahead for context
                has_table_below = False
                if i < len(lines) - 1:
                    next_line = lines[i+1].strip()
                    if next_line.startswith('|'):
                        has_table_below = True
                
                # If isolated (no table rows above or below), it's likely a fragment
                if not has_table_above and not has_table_below:
                    # Check if it's a valid complete table (has separator)
                    if i < len(lines) - 1:
                        next_line = lines[i+1].strip()
                        if not re.match(r'^\|?[-:\s|]+\|?$', next_line):
                            # Broken fragment - skip it
                            logger.debug(f"Removing broken table fragment: {line[:50]}...")
                            i += 1
                            continue
                
            cleaned_lines.append(line)
            i += 1
        
        return '\n'.join(cleaned_lines)
    
    def _is_decorative_image(self, image_info: Dict) -> bool:
        """Check if an image is decorative/blank and should be filtered out.
        
        Args:
            image_info: Image information dictionary
            
        Returns:
            True if image should be skipped, False otherwise
        """
        # Get AI description
        enhanced_desc = image_info.get('enhanced_description', '').lower()
        ocr_text = image_info.get('ocr_text', '').strip()
        
        # Patterns that indicate decorative/blank images
        decorative_patterns = [
            'white background',
            'plain white',
            'blank space',
            'empty placeholder',
            'no visible content',
            'no visible text or objects',
            'simple white square',
            'plain background',
            'no additional graphics',
            'minimalistic design with no',
            'no texts or other objects',
            'appears to be a blank',
            'no text present in the image',
            'simple, minimalist graphic with a plain white',
        ]
        
        # Check if description matches decorative patterns
        for pattern in decorative_patterns:
            if pattern in enhanced_desc:
                # Only filter if there's also no OCR text
                # (Sometimes "white background" images have important text overlays)
                if not ocr_text or len(ocr_text) < 10:
                    return True
        
        # Check for very short, generic descriptions
        if len(enhanced_desc) < 50 and any(word in enhanced_desc for word in ['white', 'blank', 'empty', 'plain']):
            if not ocr_text:
                return True
        
        return False

