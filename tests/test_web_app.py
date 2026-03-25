"""Functional tests for web_app.py API endpoints."""

import io
import json
import csv
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Must set env before importing app
import os
os.environ['FLASK_PORT'] = '5111'
os.environ['OLLAMA_HOST'] = 'http://localhost:11434'

from web_app import app, SUPPORTED_FORMATS, _validate_file_ext, API_UPLOAD_FOLDER, OUTPUT_FOLDER


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def _make_file_data(filename, content=b'test content'):
    return (io.BytesIO(content), filename)


class TestValidateFileExt:
    def test_supported(self):
        assert _validate_file_ext('test.pdf') == 'pdf'
        assert _validate_file_ext('test.PPTX') == 'pptx'
        assert _validate_file_ext('test.CSV') == 'csv'

    def test_unsupported(self):
        assert _validate_file_ext('test.mp4') == ''
        assert _validate_file_ext('test.mp3') == ''
        assert _validate_file_ext('test.exe') == ''

    def test_no_extension(self):
        assert _validate_file_ext('noext') == ''

    def test_all_formats_covered(self):
        for fmt in SUPPORTED_FORMATS:
            assert _validate_file_ext(f'test.{fmt}') == fmt


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'myfiles-to-markdown'


class TestStatsEndpoint:
    def test_stats(self, client):
        resp = client.get('/api/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total' in data
        assert 'completed' in data
        assert 'failed' in data


class TestConvertEndpoint:
    def test_no_file(self, client):
        resp = client.post('/api/convert')
        assert resp.status_code == 400
        assert 'No file provided' in resp.get_json()['error']

    def test_empty_filename(self, client):
        resp = client.post('/api/convert', data={
            'file': _make_file_data(''),
        }, content_type='multipart/form-data')
        assert resp.status_code == 400

    def test_unsupported_format_mp4(self, client):
        resp = client.post('/api/convert', data={
            'file': _make_file_data('video.mp4'),
        }, content_type='multipart/form-data')
        assert resp.status_code == 415
        data = resp.get_json()
        assert 'Unsupported' in data['error']
        assert 'supported_formats' in data

    def test_unsupported_format_mp3(self, client):
        resp = client.post('/api/convert', data={
            'file': _make_file_data('audio.mp3'),
        }, content_type='multipart/form-data')
        assert resp.status_code == 415

    def test_unsupported_format_exe(self, client):
        resp = client.post('/api/convert', data={
            'file': _make_file_data('malware.exe'),
        }, content_type='multipart/form-data')
        assert resp.status_code == 415

    @patch('web_app.DocumentProcessor')
    def test_successful_conversion_json(self, mock_proc_cls, client, tmp_dir):
        """Test successful conversion returns JSON with markdown."""
        # Setup mock
        mock_proc = MagicMock()
        mock_proc.ai_enabled = True
        mock_proc.process_file.return_value = True
        mock_proc_cls.return_value = mock_proc

        # Create fake output file
        stem = 'testdoc'
        out_file = OUTPUT_FOLDER / f'{stem}.md'
        out_file.write_text('---\ntitle: Test\n---\n\n# Hello World\n')

        try:
            resp = client.post('/api/convert', data={
                'file': _make_file_data(f'{stem}.pdf', b'%PDF-fake'),
                'output_format': 'json',
                'ai_enhancement': 'false',
            }, content_type='multipart/form-data')

            assert resp.status_code == 200
            data = resp.get_json()
            assert data['status'] == 'completed'
            assert '# Hello World' in data['markdown']
            assert data['filename'] == f'{stem}.pdf'
        finally:
            if out_file.exists():
                out_file.unlink()

    @patch('web_app.DocumentProcessor')
    def test_successful_conversion_markdown(self, mock_proc_cls, client):
        """Test markdown output format."""
        mock_proc = MagicMock()
        mock_proc.ai_enabled = True
        mock_proc.process_file.return_value = True
        mock_proc_cls.return_value = mock_proc

        stem = 'mdtest'
        out_file = OUTPUT_FOLDER / f'{stem}.md'
        out_file.write_text('---\ntitle: MD Test\n---\n\nContent here\n')

        try:
            resp = client.post('/api/convert', data={
                'file': _make_file_data(f'{stem}.pdf', b'%PDF-fake'),
                'output_format': 'markdown',
            }, content_type='multipart/form-data')

            assert resp.status_code == 200
            assert resp.content_type == 'text/markdown; charset=utf-8'
            assert b'Content here' in resp.data
        finally:
            if out_file.exists():
                out_file.unlink()

    @patch('web_app.DocumentProcessor')
    def test_conversion_failure(self, mock_proc_cls, client):
        mock_proc = MagicMock()
        mock_proc.ai_enabled = True
        mock_proc.process_file.return_value = False
        mock_proc_cls.return_value = mock_proc

        resp = client.post('/api/convert', data={
            'file': _make_file_data('fail.pdf', b'%PDF-fake'),
            'output_format': 'json',
        }, content_type='multipart/form-data')

        assert resp.status_code == 500
        assert 'failed' in resp.get_json()['error'].lower()

    @patch('web_app.DocumentProcessor')
    def test_ai_enhancement_flag(self, mock_proc_cls, client):
        """Test that ai_enhancement=false disables AI."""
        mock_proc = MagicMock()
        mock_proc.ai_enabled = True
        mock_proc.process_file.return_value = True
        mock_proc_cls.return_value = mock_proc

        stem = 'aitest'
        out_file = OUTPUT_FOLDER / f'{stem}.md'
        out_file.write_text('---\ntitle: t\n---\ncontent\n')

        try:
            resp = client.post('/api/convert', data={
                'file': _make_file_data(f'{stem}.pdf', b'%PDF-fake'),
                'output_format': 'json',
                'ai_enhancement': 'false',
            }, content_type='multipart/form-data')

            assert resp.status_code == 200
            # Verify AI was disabled on the processor
            assert mock_proc.ai_enabled is False
        finally:
            if out_file.exists():
                out_file.unlink()


class TestUploadEndpoint:
    def test_no_files(self, client):
        resp = client.post('/api/upload')
        assert resp.status_code == 400

    def test_unsupported_files_skipped(self, client):
        resp = client.post('/api/upload', data={
            'files[]': _make_file_data('video.mp4'),
        }, content_type='multipart/form-data')
        data = resp.get_json()
        assert data['job_ids'] == []
        assert 'video.mp4' in data.get('skipped', [])


class TestJobsEndpoint:
    def test_list_jobs(self, client):
        resp = client.get('/api/jobs')
        assert resp.status_code == 200
        assert 'jobs' in resp.get_json()

    def test_get_nonexistent_job(self, client):
        resp = client.get('/api/jobs/nonexistent-uuid')
        assert resp.status_code == 404

    def test_download_nonexistent_job(self, client):
        resp = client.get('/api/download/nonexistent-uuid')
        assert resp.status_code == 404
