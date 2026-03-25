"""Tests for ai_enhancer.py."""

from unittest.mock import MagicMock, patch
from ai_enhancer import AIEnhancer


def _make_enhancer(host='http://localhost:11434'):
    config = {'host': host, 'model': 'llama3.2:latest', 'timeout': 10, 'temperature': 0.7}
    return AIEnhancer(config)


class TestAIEnhancerInit:
    def test_init(self):
        e = _make_enhancer()
        assert e.model == 'llama3.2:latest'
        assert e.temperature == 0.7

    def test_custom_host(self):
        e = _make_enhancer('http://custom:9999')
        assert e.host == 'http://custom:9999'


class TestGenerateSummary:
    def test_short_text_returns_default(self):
        e = _make_enhancer()
        result = e.generate_summary("Too short")
        assert "too short" in result.lower()

    def test_empty_text(self):
        e = _make_enhancer()
        result = e.generate_summary("")
        assert "too short" in result.lower()

    @patch.object(AIEnhancer, '__init__', lambda self, cfg: None)
    def test_ollama_error_returns_error_string(self):
        e = AIEnhancer.__new__(AIEnhancer)
        e.model = 'test'
        e.temperature = 0.7
        e.client = MagicMock()
        e.client.generate.side_effect = Exception("connection refused")
        result = e.generate_summary("A " * 100)
        assert "Error" in result


class TestGenerateTags:
    def test_short_text_returns_empty(self):
        e = _make_enhancer()
        assert e.generate_tags("Hi") == []

    @patch.object(AIEnhancer, '__init__', lambda self, cfg: None)
    def test_parses_comma_separated(self):
        e = AIEnhancer.__new__(AIEnhancer)
        e.model = 'test'
        e.temperature = 0.7
        e.client = MagicMock()
        e.client.generate.return_value = {'response': 'ai-tools, machine-learning, data-science'}
        tags = e.generate_tags("A " * 100, max_tags=5)
        assert 'ai-tools' in tags
        assert 'machine-learning' in tags
        assert len(tags) <= 5

    @patch.object(AIEnhancer, '__init__', lambda self, cfg: None)
    def test_tags_hyphenated(self):
        e = AIEnhancer.__new__(AIEnhancer)
        e.model = 'test'
        e.temperature = 0.7
        e.client = MagicMock()
        e.client.generate.return_value = {'response': 'natural language processing, deep learning'}
        tags = e.generate_tags("A " * 100)
        assert all('-' in t or len(t.split()) == 1 for t in tags)

    @patch.object(AIEnhancer, '__init__', lambda self, cfg: None)
    def test_max_tags_limit(self):
        e = AIEnhancer.__new__(AIEnhancer)
        e.model = 'test'
        e.temperature = 0.7
        e.client = MagicMock()
        e.client.generate.return_value = {'response': ', '.join(f'tag-{i}' for i in range(20))}
        tags = e.generate_tags("A " * 100, max_tags=3)
        assert len(tags) <= 3


class TestGenerateDescription:
    def test_short_text(self):
        e = _make_enhancer()
        result = e.generate_description("Hi")
        assert "No description" in result

    @patch.object(AIEnhancer, '__init__', lambda self, cfg: None)
    def test_ollama_error(self):
        e = AIEnhancer.__new__(AIEnhancer)
        e.model = 'test'
        e.client = MagicMock()
        e.client.generate.side_effect = Exception("fail")
        result = e.generate_description("A " * 100)
        assert result == "Document content summary."


class TestAnalyzeDocument:
    @patch.object(AIEnhancer, '__init__', lambda self, cfg: None)
    def test_returns_all_fields(self):
        e = AIEnhancer.__new__(AIEnhancer)
        e.model = 'test'
        e.temperature = 0.7
        e.client = MagicMock()
        e.client.generate.return_value = {'response': 'test output'}
        result = e.analyze_document("A " * 100)
        assert 'description' in result
        assert 'summary' in result
        assert 'tags' in result
        assert 'word_count' in result
        assert 'analysis_timestamp' in result
