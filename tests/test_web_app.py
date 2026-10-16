"""Functional tests for web_app.py API endpoints (FastAPI TestClient, processor mocked)."""

import io
import pytest
from unittest.mock import patch, MagicMock

# Must set env before importing app
import os
os.environ['OLLAMA_HOST'] = 'http://localhost:11434'

from fastapi.testclient import TestClient
from web_app import app, SUPPORTED_FORMATS, _validate_ext, OUTPUT_FOLDER


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _file(filename, content=b'test content'):
    return (filename, io.BytesIO(content))


def _error(resp):
    """HTTPException(detail={...}) arrives as {"detail": {...}}."""
    body = resp.json()
    return body.get('detail', body)


def _mock_processor(mock_proc_cls, success=True, markdown=None):
    """Mock DocumentProcessor; on success write the .md where the endpoint looks for it."""
    mock_proc = MagicMock()
    mock_proc.ai_enabled = True

    def process_file(file_path, *args, **kwargs):
        if success and markdown is not None:
            (OUTPUT_FOLDER / f"{file_path.stem}.md").write_text(markdown)
        return success

    mock_proc.process_file.side_effect = process_file
    mock_proc_cls.return_value = mock_proc
    return mock_proc


class TestValidateExt:
    def test_supported(self):
        assert _validate_ext('test.pdf') == 'pdf'
        assert _validate_ext('test.PPTX') == 'pptx'
        assert _validate_ext('test.CSV') == 'csv'

    def test_unsupported(self):
        assert _validate_ext('test.mp4') == ''
        assert _validate_ext('test.mp3') == ''
        assert _validate_ext('test.exe') == ''

    def test_no_extension(self):
        assert _validate_ext('noext') == ''

    def test_all_formats_covered(self):
        for fmt in SUPPORTED_FORMATS:
            assert _validate_ext(f'test.{fmt}') == fmt


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'myfiles-to-markdown'
        assert data['version'] == app.version


class TestConvertEndpoint:
    def test_no_file(self, client):
        resp = client.post('/api/convert')
        assert resp.status_code == 422

    def test_unsupported_format_mp4(self, client):
        resp = client.post('/api/convert', files={'file': _file('video.mp4')})
        assert resp.status_code == 415
        err = _error(resp)
        assert 'Unsupported' in err['error']
        assert 'supported_formats' in err

    def test_unsupported_format_mp3(self, client):
        resp = client.post('/api/convert', files={'file': _file('audio.mp3')})
        assert resp.status_code == 415

    def test_unsupported_format_exe(self, client):
        resp = client.post('/api/convert', files={'file': _file('malware.exe')})
        assert resp.status_code == 415

    @patch('web_app.DocumentProcessor')
    def test_successful_conversion_json(self, mock_proc_cls, client):
        _mock_processor(mock_proc_cls, markdown='---\ntitle: Test\n---\n\n# Hello World\n')
        resp = client.post('/api/convert', files={'file': _file('testdoc.pdf', b'%PDF-fake')},
                           data={'output_format': 'json', 'ai_enhancement': 'false'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'completed'
        assert '# Hello World' in data['markdown']
        assert data['filename'] == 'testdoc.pdf'
        assert data['output_filename'] == 'testdoc.md'

    @patch('web_app.DocumentProcessor')
    def test_successful_conversion_markdown(self, mock_proc_cls, client):
        _mock_processor(mock_proc_cls, markdown='---\ntitle: MD Test\n---\n\nContent here\n')
        resp = client.post('/api/convert', files={'file': _file('mdtest.pdf', b'%PDF-fake')},
                           data={'output_format': 'markdown'})
        assert resp.status_code == 200
        assert resp.headers['content-type'].startswith('text/markdown')
        assert b'Content here' in resp.content

    @patch('web_app.DocumentProcessor')
    def test_output_cleaned_up(self, mock_proc_cls, client):
        _mock_processor(mock_proc_cls, markdown='# temp\n')
        before = set(OUTPUT_FOLDER.glob('*_cleanme.md'))
        resp = client.post('/api/convert', files={'file': _file('cleanme.pdf', b'%PDF-fake')},
                           data={'output_format': 'json'})
        assert resp.status_code == 200
        assert set(OUTPUT_FOLDER.glob('*_cleanme.md')) == before

    @patch('web_app.DocumentProcessor')
    def test_conversion_failure(self, mock_proc_cls, client):
        _mock_processor(mock_proc_cls, success=False)
        resp = client.post('/api/convert', files={'file': _file('fail.pdf', b'%PDF-fake')},
                           data={'output_format': 'json'})
        assert resp.status_code == 500
        assert 'failed' in _error(resp)['error'].lower()

    @patch('web_app.DocumentProcessor')
    def test_ai_enhancement_flag(self, mock_proc_cls, client):
        """ai_enhancement=false disables AI on the processor."""
        mock_proc = _mock_processor(mock_proc_cls, markdown='---\ntitle: t\n---\ncontent\n')
        resp = client.post('/api/convert', files={'file': _file('aitest.pdf', b'%PDF-fake')},
                           data={'output_format': 'json', 'ai_enhancement': 'false'})
        assert resp.status_code == 200
        assert mock_proc.ai_enabled is False


class TestUploadEndpoint:
    def test_no_files(self, client):
        resp = client.post('/api/upload')
        assert resp.status_code in (400, 422)

    def test_unsupported_files_skipped(self, client):
        resp = client.post('/api/upload', files={'files[]': _file('video.mp4')})
        data = resp.json()
        assert data['job_ids'] == []
        assert 'video.mp4' in data.get('skipped', [])


class TestJobsEndpoint:
    def test_get_nonexistent_job(self, client):
        resp = client.get('/api/jobs/nonexistent-uuid')
        assert resp.status_code == 404

    def test_download_nonexistent_job(self, client):
        resp = client.get('/api/download/nonexistent-uuid')
        assert resp.status_code == 404
