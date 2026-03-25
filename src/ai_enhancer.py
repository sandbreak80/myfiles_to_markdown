"""AI enhancement using local Ollama."""

import time
from typing import List, Dict, Optional
from loguru import logger
import ollama
from PIL import Image
import io
import base64


class AIEnhancer:
    """Handles AI enhancement of documents using Ollama."""
    
    def __init__(self, config: Dict):
        """Initialize AI enhancer.
        
        Args:
            config: Ollama configuration dictionary
        """
        self.host = config.get('host', 'http://ollama:11434')
        self.model = config.get('model', 'llama3.2:latest')
        self.timeout = config.get('timeout', 300)
        self.temperature = config.get('temperature', 0.7)
        
        # Configure ollama client
        self.client = ollama.Client(host=self.host)
        logger.info(f"AI Enhancer initialized with model: {self.model}")
        
    def check_ollama_available(self) -> bool:
        """Check if Ollama is available and model is pulled.
        
        Returns:
            True if Ollama is ready, False otherwise
        """
        try:
            # Check if Ollama is running
            models = self.client.list()
            if hasattr(models, 'models'):
                model_list = models.models
            elif isinstance(models, dict) and 'models' in models:
                model_list = models['models']
            else:
                model_list = []
            
            logger.info(f"Ollama is available. Found {len(model_list)} models")
            
            # Check if our model is available
            model_names = []
            for m in model_list:
                if hasattr(m, 'model'):
                    model_names.append(m.model)
                elif isinstance(m, dict) and 'model' in m:
                    model_names.append(m['model'])
                elif isinstance(m, dict) and 'name' in m:
                    model_names.append(m['name'])
            
            if model_names and self.model not in model_names and not any(self.model.split(':')[0] in m for m in model_names):
                logger.warning(f"Model {self.model} not found. Available models: {model_names}")
                logger.info(f"Attempting to pull {self.model}...")
                self._pull_model()
            
            return True
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False
    
    def _pull_model(self):
        """Pull the required model from Ollama."""
        try:
            logger.info(f"Pulling model {self.model}...")
            self.client.pull(self.model)
            logger.info(f"Model {self.model} pulled successfully")
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            raise
    
    def generate_summary(self, text: str, max_length: int = 100) -> str:
        """Generate a summary of the document.
        
        Args:
            text: Document text to summarize
            max_length: Maximum summary length in words (default: 100)
            
        Returns:
            Generated summary
        """
        if not text or len(text.strip()) < 50:
            return "Document too short for summary generation."
        
        prompt = f"""Create a concise summary of the following document in MAXIMUM {max_length} words. 
Focus on the main topic and key purpose. Be brief and clear.

Document:
{text[:10000]}

Summary (max {max_length} words):"""
        
        try:
            logger.info("Generating document summary...")
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'num_predict': max_length * 2  # Rough token estimate
                }
            )
            summary = response['response'].strip()
            logger.info("Summary generated successfully")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def generate_description(self, text: str) -> str:
        """Generate a short one-sentence description of the document.
        
        Args:
            text: Document text to analyze
            
        Returns:
            Short description (1-2 sentences)
        """
        if not text or len(text.strip()) < 20:
            return "No description available."
        
        prompt = f"""Write a single-sentence description of this document's main purpose or topic.

Document:
{text[:3000]}

One-sentence description:"""
        
        try:
            logger.info("Generating document description...")
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.5,
                    'num_predict': 50
                }
            )
            description = response['response'].strip()
            logger.info("Description generated successfully")
            return description
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return "Document content summary."
    
    def generate_tags(self, text: str, max_tags: int = 10) -> List[str]:
        """Generate relevant tags for the document.
        
        Args:
            text: Document text to analyze
            max_tags: Maximum number of tags to generate
            
        Returns:
            List of generated tags (hyphenated, no spaces)
        """
        if not text or len(text.strip()) < 20:
            return []
        
        prompt = f"""Analyze the following document and generate up to {max_tags} relevant tags/keywords.
Return ONLY the tags as a comma-separated list, no explanations.
Tags must be lowercase with hyphens instead of spaces (e.g., "ai-prompting", "sales-enablement").
Use single words or hyphenated phrases only.

Document:
{text[:5000]}

Tags:"""
        
        try:
            logger.info("Generating document tags...")
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.5,  # Lower temperature for more focused tags
                    'num_predict': 100
                }
            )
            
            tags_text = response['response'].strip()
            # Parse comma-separated tags
            tags = [tag.strip().lower() for tag in tags_text.split(',')]
            # Replace spaces with hyphens for Obsidian compatibility
            tags = [tag.replace(' ', '-') for tag in tags if tag]
            # Clean up multiple hyphens and ensure valid format
            tags = ['-'.join(filter(None, tag.split('-'))) for tag in tags]
            tags = [tag for tag in tags if tag and len(tag) > 2][:max_tags]
            
            logger.info(f"Generated {len(tags)} tags")
            return tags
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return []
    
    def describe_image(self, image_path: str, ocr_text: str = "", context: str = "") -> str:
        """Generate a description of an image using AI vision + OCR fallback.
        
        Strategy for presentations (PRIORITY: Vision AI):
        1. Always try AI vision first for best quality
        2. Fall back to OCR only if vision fails
        3. Use contextual placeholder as last resort
        
        Args:
            image_path: Path to the image file
            ocr_text: Pre-extracted OCR text (fallback only)
            context: Optional context about the document
            
        Returns:
            Image description
        """
        try:
            # For presentations, ALWAYS try vision AI first
            # OCR often fails on styled text, graphics, and layouts
            
            # Strategy 2: Try AI vision models
            logger.info(f"Attempting AI vision for: {image_path}")
            
            import base64
            with open(image_path, 'rb') as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            prompt = "Describe this image in detail. If there's text, transcribe it exactly. Then describe visual elements."
            if context:
                prompt = f"Context: {context}\n\n{prompt}"
            
            # Try vision models in order of preference
            vision_models = ['llava:7b', 'llava', 'llama3.2-vision', 'llava:13b', 'bakllava']
            
            for model in vision_models:
                try:
                    logger.debug(f"Trying vision model: {model}")
                    response = self.client.generate(
                        model=model,
                        prompt=prompt,
                        images=[image_data],
                        options={
                            'temperature': 0.3,
                            'num_predict': 300
                        }
                    )
                    description = response['response'].strip()
                    if description and len(description) > 10:
                        logger.info(f"✓ AI vision ({model}): {len(description)} chars")
                        return description
                except Exception as model_err:
                    logger.debug(f"  {model} not available: {model_err}")
                    continue
            
            # Strategy 3: Use any OCR text
            if ocr_text and ocr_text.strip():
                logger.info("Using short OCR text (vision unavailable)")
                return ocr_text.strip()
            
            # Strategy 4: Contextual placeholder
            logger.warning("No OCR or vision available")
            msg = "[Image"
            if context:
                msg += f" - {context}"
            msg += " - install llama3.2-vision: ollama pull llama3.2-vision]"
            return msg
                
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return ocr_text.strip() if ocr_text else "[Image]"
    
    def analyze_document(self, text: str, max_tags: int = 10) -> Dict[str, any]:
        """Perform complete AI analysis on document.
        
        Args:
            text: Document text to analyze
            max_tags: Maximum number of tags
            
        Returns:
            Dictionary with description, summary, tags, and metadata
        """
        logger.info("Starting comprehensive document analysis...")
        
        result = {
            'description': '',
            'summary': '',
            'tags': [],
            'word_count': len(text.split()),
            'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Generate short description
        result['description'] = self.generate_description(text)
        
        # Generate summary (max 100 words)
        result['summary'] = self.generate_summary(text, max_length=100)
        
        # Generate tags (Obsidian-compatible with hyphens)
        result['tags'] = self.generate_tags(text, max_tags)
        
        logger.info("Document analysis complete")
        return result

