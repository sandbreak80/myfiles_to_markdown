"""Extended AI enhancer tests covering Ollama integration paths."""

from unittest.mock import MagicMock, patch
from ai_enhancer import AIEnhancer
import tempfile
from pathlib import Path
from PIL import Image


def _mock_enhancer():
    e = AIEnhancer.__new__(AIEnhancer)
    e.host = 'http://test:11434'
    e.model = 'llama3.2:latest'
    e.timeout = 10
    e.temperature = 0.7
    e.client = MagicMock()
    return e


class TestCheckOllamaAvailable:
    def test_available_with_model(self):
        e = _mock_enhancer()
        e.client.list.return_value = {'models': [{'model': 'llama3.2:latest'}]}
        assert e.check_ollama_available() is True

    def test_available_models_as_objects(self):
        e = _mock_enhancer()
        model = MagicMock()
        model.model = 'llama3.2:latest'
        e.client.list.return_value = MagicMock(models=[model])
        assert e.check_ollama_available() is True

    def test_unavailable(self):
        e = _mock_enhancer()
        e.client.list.side_effect = Exception("connection refused")
        assert e.check_ollama_available() is False

    def test_model_missing_triggers_pull(self):
        e = _mock_enhancer()
        e.client.list.return_value = {'models': [{'model': 'other-model:latest'}]}
        e.client.pull.return_value = None
        result = e.check_ollama_available()
        assert result is True
        e.client.pull.assert_called_once_with('llama3.2:latest')

    def test_model_name_variant(self):
        e = _mock_enhancer()
        e.client.list.return_value = {'models': [{'name': 'llama3.2:latest'}]}
        assert e.check_ollama_available() is True


class TestPullModel:
    def test_pull_success(self):
        e = _mock_enhancer()
        e._pull_model()
        e.client.pull.assert_called_once()

    def test_pull_failure(self):
        e = _mock_enhancer()
        e.client.pull.side_effect = Exception("network error")
        import pytest
        with pytest.raises(Exception):
            e._pull_model()


class TestGenerateSummaryIntegration:
    def test_success(self):
        e = _mock_enhancer()
        e.client.generate.return_value = {'response': 'This is a summary of the document.'}
        result = e.generate_summary("A " * 100, max_length=50)
        assert result == 'This is a summary of the document.'
        e.client.generate.assert_called_once()

    def test_respects_max_length(self):
        e = _mock_enhancer()
        e.client.generate.return_value = {'response': 'short summary'}
        e.generate_summary("A " * 100, max_length=200)
        call_args = e.client.generate.call_args
        assert '200' in call_args[1]['prompt'] or '200' in str(call_args)


class TestGenerateTagsIntegration:
    def test_filters_short_tags(self):
        e = _mock_enhancer()
        e.client.generate.return_value = {'response': 'ai, ml, data-science, a, bb'}
        tags = e.generate_tags("A " * 100, max_tags=10)
        # Tags shorter than 3 chars filtered out
        assert 'a' not in tags
        assert 'bb' not in tags
        assert 'data-science' in tags

    def test_spaces_to_hyphens(self):
        e = _mock_enhancer()
        e.client.generate.return_value = {'response': 'machine learning, deep learning'}
        tags = e.generate_tags("A " * 100)
        for tag in tags:
            assert ' ' not in tag


class TestDescribeImage:
    def test_with_ocr_fallback(self, tmp_dir):
        e = _mock_enhancer()
        # All vision models fail
        e.client.generate.side_effect = Exception("model not found")
        img = Image.new('RGB', (10, 10))
        path = tmp_dir / 'test.png'
        img.save(path)
        result = e.describe_image(str(path), ocr_text="OCR extracted text", context="test doc")
        assert result == "OCR extracted text"

    def test_with_vision_success(self, tmp_dir):
        e = _mock_enhancer()
        e.client.generate.return_value = {'response': 'A chart showing quarterly revenue growth'}
        img = Image.new('RGB', (10, 10))
        path = tmp_dir / 'test.png'
        img.save(path)
        result = e.describe_image(str(path), context="business report")
        assert 'quarterly revenue' in result

    def test_no_ocr_no_vision(self, tmp_dir):
        e = _mock_enhancer()
        e.client.generate.side_effect = Exception("fail")
        img = Image.new('RGB', (10, 10))
        path = tmp_dir / 'test.png'
        img.save(path)
        result = e.describe_image(str(path), ocr_text="", context="doc")
        assert '[Image' in result

    def test_bad_file_path(self):
        e = _mock_enhancer()
        result = e.describe_image("/nonexistent/image.png", ocr_text="backup text")
        assert result == "backup text"


class TestAnalyzeDocumentIntegration:
    def test_full_analysis(self):
        e = _mock_enhancer()
        e.client.generate.return_value = {'response': 'test output'}
        result = e.analyze_document("A long document " * 50, max_tags=5)
        assert result['word_count'] > 0
        assert result['analysis_timestamp']
        # generate called 3 times: description, summary, tags
        assert e.client.generate.call_count == 3
