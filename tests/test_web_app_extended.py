"""Extended functional tests for web_app.py — async jobs, edge cases."""

import io
import os
import time
os.environ.setdefault('FLASK_PORT', '5111')
os.environ.setdefault('OLLAMA_HOST', 'http://localhost:11434')

from unittest.mock import patch, MagicMock
from web_app import app, jobs, jobs_lock, JobStatus, OUTPUT_FOLDER, process_file_job, API_UPLOAD_FOLDER
from pathlib import Path
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def _make_file_data(filename, content=b'test'):
    return (io.BytesIO(content), filename)


class TestConvertEdgeCases:
    def test_413_large_file(self, client):
        """Files over 500MB should return 413."""
        # We can't actually upload 500MB in a test, but the config is set
        assert app.config['MAX_CONTENT_LENGTH'] == 500 * 1024 * 1024

    @patch('web_app.DocumentProcessor')
    def test_processor_exception(self, mock_cls, client):
        mock_cls.side_effect = Exception("init failed")
        resp = client.post('/api/convert', data={
            'file': _make_file_data('test.pdf', b'%PDF-1'),
            'output_format': 'json',
        }, content_type='multipart/form-data')
        assert resp.status_code == 500
        assert 'init failed' in resp.get_json()['error']

    @patch('web_app.DocumentProcessor')
    def test_output_not_found(self, mock_cls, client):
        """process_file returns True but output file doesn't exist."""
        mock = MagicMock()
        mock.ai_enabled = True
        mock.process_file.return_value = True
        mock_cls.return_value = mock
        resp = client.post('/api/convert', data={
            'file': _make_file_data('ghost.pdf', b'%PDF-1'),
            'output_format': 'json',
        }, content_type='multipart/form-data')
        assert resp.status_code == 500
        assert 'not generated' in resp.get_json()['error']


class TestUploadExtended:
    @patch('web_app.process_file_job')
    def test_upload_creates_job(self, mock_job, client):
        resp = client.post('/api/upload', data={
            'files[]': _make_file_data('test.pdf', b'%PDF-1'),
            'ai_enhancement': 'true',
        }, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['job_ids']) == 1

    def test_upload_mixed_formats(self, client):
        """Upload both supported and unsupported files."""
        resp = client.post('/api/upload', data={
            'files[]': [
                _make_file_data('good.pdf', b'%PDF-1'),
                _make_file_data('bad.mp4', b'\x00\x00'),
            ],
            'ai_enhancement': 'false',
        }, content_type='multipart/form-data')
        data = resp.get_json()
        # mp4 should be skipped
        assert 'bad.mp4' in data.get('skipped', [])


class TestJobsExtended:
    def test_job_status_lifecycle(self):
        """Verify job status constants."""
        assert JobStatus.QUEUED == 'queued'
        assert JobStatus.PROCESSING == 'processing'
        assert JobStatus.COMPLETED == 'completed'
        assert JobStatus.FAILED == 'failed'

    def test_download_incomplete_job(self, client):
        job_id = 'test-incomplete-job'
        with jobs_lock:
            jobs[job_id] = {
                'id': job_id,
                'status': JobStatus.PROCESSING,
                'filename': 'test.pdf',
            }
        try:
            resp = client.get(f'/api/download/{job_id}')
            assert resp.status_code == 400
            assert 'not completed' in resp.get_json()['error']
        finally:
            with jobs_lock:
                jobs.pop(job_id, None)

    def test_get_specific_job(self, client):
        job_id = 'test-specific-job'
        with jobs_lock:
            jobs[job_id] = {
                'id': job_id,
                'status': JobStatus.COMPLETED,
                'filename': 'test.pdf',
            }
        try:
            resp = client.get(f'/api/jobs/{job_id}')
            assert resp.status_code == 200
            assert resp.get_json()['status'] == 'completed'
        finally:
            with jobs_lock:
                jobs.pop(job_id, None)


class TestProcessFileJob:
    @patch('web_app.DocumentProcessor')
    def test_job_success(self, mock_cls, tmp_dir):
        mock_proc = MagicMock()
        mock_proc.ai_enabled = True
        mock_proc.process_file.return_value = True
        mock_cls.return_value = mock_proc

        job_id = 'test-success'
        file_path = tmp_dir / 'test.pdf'
        file_path.write_bytes(b'%PDF-fake')

        out_file = OUTPUT_FOLDER / 'test.md'
        out_file.write_text('# Test\n')

        with jobs_lock:
            jobs[job_id] = {'id': job_id, 'status': JobStatus.QUEUED}

        try:
            process_file_job(job_id, file_path, ai_enhancement=True, ai_image_processing=False)
            assert jobs[job_id]['status'] == JobStatus.COMPLETED
        finally:
            with jobs_lock:
                jobs.pop(job_id, None)
            if out_file.exists():
                out_file.unlink()

    @patch('web_app.DocumentProcessor')
    def test_job_failure(self, mock_cls, tmp_dir):
        mock_proc = MagicMock()
        mock_proc.ai_enabled = True
        mock_proc.process_file.return_value = False
        mock_cls.return_value = mock_proc

        job_id = 'test-fail'
        file_path = tmp_dir / 'bad.pdf'
        file_path.write_bytes(b'bad')

        with jobs_lock:
            jobs[job_id] = {'id': job_id, 'status': JobStatus.QUEUED}

        try:
            process_file_job(job_id, file_path, ai_enhancement=False)
            assert jobs[job_id]['status'] == JobStatus.FAILED
        finally:
            with jobs_lock:
                jobs.pop(job_id, None)

    @patch('web_app.DocumentProcessor')
    def test_job_exception(self, mock_cls, tmp_dir):
        mock_cls.side_effect = Exception("crash")

        job_id = 'test-crash'
        file_path = tmp_dir / 'crash.pdf'
        file_path.write_bytes(b'x')

        with jobs_lock:
            jobs[job_id] = {'id': job_id, 'status': JobStatus.QUEUED}

        try:
            process_file_job(job_id, file_path)
            assert jobs[job_id]['status'] == JobStatus.FAILED
            assert 'crash' in jobs[job_id]['error']
        finally:
            with jobs_lock:
                jobs.pop(job_id, None)


class TestErrorHandler:
    def test_413_handler(self, client):
        """Verify the 413 error handler is registered."""
        # We can't easily trigger it in a test, but verify the handler exists
        handlers = app.error_handler_spec.get(None, {})
        assert 413 in handlers
