"""Configuration management for the document converter."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: str = "/app/config/config.yaml"):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._apply_env_overrides()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        if os.getenv('OLLAMA_HOST'):
            self.config['ollama']['host'] = os.getenv('OLLAMA_HOST')
            logger.info(f"Ollama host overridden from environment: {self.config['ollama']['host']}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'ollama': {
                'host': 'http://ollama:11434',
                'model': 'llama3.2:latest',
                'timeout': 300,
                'temperature': 0.7
            },
            'paths': {
                'input_dir': '/app/input',
                'output_dir': '/app/output',
                'log_dir': '/app/logs'
            },
            'processing': {
                'supported_formats': ['pdf', 'docx', 'pptx', 'xlsx'],
                'ocr': {
                    'enabled': True,
                    'language': 'eng',
                    'min_confidence': 60
                },
                'images': {
                    'extract': True,
                    'max_size_mb': 10,
                    'describe_failed_ocr': True
                },
                'ai': {
                    'generate_summary': True,
                    'generate_tags': True,
                    'max_tags': 10,
                    'describe_images': True
                }
            },
            'obsidian': {
                'frontmatter': {
                    'add_source_file': True,
                    'add_created_date': True,
                    'add_processed_date': True,
                    'add_ai_summary': True,
                    'add_ai_tags': True
                },
                'preserve_filename': True,
                'sanitize_filenames': True,
                'attachments_folder': 'attachments',
                'embed_images': True
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'ollama.host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration.
        
        Returns:
            Ollama configuration dictionary
        """
        return self.config.get('ollama', {})
    
    def get_paths(self) -> Dict[str, str]:
        """Get path configuration.
        
        Returns:
            Path configuration dictionary
        """
        return self.config.get('paths', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration.
        
        Returns:
            Processing configuration dictionary
        """
        return self.config.get('processing', {})
    
    def get_obsidian_config(self) -> Dict[str, Any]:
        """Get Obsidian configuration.
        
        Returns:
            Obsidian configuration dictionary
        """
        return self.config.get('obsidian', {})

