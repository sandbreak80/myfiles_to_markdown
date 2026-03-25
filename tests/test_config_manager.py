"""Tests for config_manager.py."""

import os
import yaml
from pathlib import Path
from config_manager import ConfigManager


class TestConfigManager:
    def test_load_from_file(self, tmp_dir, monkeypatch):
        monkeypatch.delenv('OLLAMA_HOST', raising=False)
        cfg_path = tmp_dir / 'config.yaml'
        cfg_path.write_text(yaml.dump({
            'ollama': {'host': 'http://test:11434', 'model': 'test-model'},
            'paths': {'input_dir': '/in', 'output_dir': '/out', 'log_dir': '/log'},
            'processing': {'supported_formats': ['pdf']},
            'obsidian': {'preserve_filename': True},
        }))
        cm = ConfigManager(str(cfg_path))
        assert cm.get_ollama_config()['host'] == 'http://test:11434'
        assert cm.get_paths()['input_dir'] == '/in'

    def test_defaults_when_missing(self, tmp_dir):
        cm = ConfigManager(str(tmp_dir / 'nonexistent.yaml'))
        cfg = cm.get_ollama_config()
        assert 'host' in cfg
        assert 'model' in cfg

    def test_dot_notation_get(self, tmp_dir, monkeypatch):
        monkeypatch.delenv('OLLAMA_HOST', raising=False)
        cfg_path = tmp_dir / 'config.yaml'
        cfg_path.write_text(yaml.dump({
            'ollama': {'host': 'http://x:11434', 'model': 'm'},
            'paths': {'input_dir': '/i', 'output_dir': '/o', 'log_dir': '/l'},
            'processing': {},
            'obsidian': {},
        }))
        cm = ConfigManager(str(cfg_path))
        assert cm.get('ollama.host') == 'http://x:11434'
        assert cm.get('nonexistent.key', 'default') == 'default'

    def test_env_override(self, tmp_dir, monkeypatch):
        cfg_path = tmp_dir / 'config.yaml'
        cfg_path.write_text(yaml.dump({
            'ollama': {'host': 'http://original:11434', 'model': 'm'},
            'paths': {'input_dir': '/i', 'output_dir': '/o', 'log_dir': '/l'},
            'processing': {},
            'obsidian': {},
        }))
        monkeypatch.setenv('OLLAMA_HOST', 'http://override:11434')
        cm = ConfigManager(str(cfg_path))
        assert cm.get_ollama_config()['host'] == 'http://override:11434'

    def test_get_processing_config(self, tmp_dir):
        cfg_path = tmp_dir / 'config.yaml'
        cfg_path.write_text(yaml.dump({
            'ollama': {'host': 'h', 'model': 'm'},
            'paths': {'input_dir': '/i', 'output_dir': '/o', 'log_dir': '/l'},
            'processing': {'ocr': {'enabled': True}},
            'obsidian': {},
        }))
        cm = ConfigManager(str(cfg_path))
        assert cm.get_processing_config()['ocr']['enabled'] is True

    def test_get_obsidian_config(self, tmp_dir):
        cfg_path = tmp_dir / 'config.yaml'
        cfg_path.write_text(yaml.dump({
            'ollama': {'host': 'h', 'model': 'm'},
            'paths': {'input_dir': '/i', 'output_dir': '/o', 'log_dir': '/l'},
            'processing': {},
            'obsidian': {'preserve_filename': False},
        }))
        cm = ConfigManager(str(cfg_path))
        assert cm.get_obsidian_config()['preserve_filename'] is False
