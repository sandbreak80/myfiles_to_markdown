"""Extended functional tests for web_app.py — async jobs, edge cases."""

import io
import os
os.environ.setdefault('OLLAMA_HOST', 'http://localhost:11434')

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from web_app import app, jobs, jobs_lock, JobStatus, OUTPUT_FOLDER, MAX_FILE_SIZE, process_file_job
import pytest


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _file(filename, content=b'test'):
    return (filename, io.BytesIO(content))


def _error(resp):
    body = resp.json()
    return body.get('detail', body)


class TestConvertEdgeCases:
    def test_max_file_size(self):
        """Files over 500MB are rejected with 413 (can't upload that much in a test)."""
        assert MAX_FILE_SIZE == 500 * 1024 * 1024

    @patch('web_app.DocumentProcessor')
    def test_processor_exception(self, mock_cls, client):
        mock_cls.side_effect = Exception("init failed")
        resp = client.post('/api/convert', files={'file': _file('test.pdf', b'%PDF-1')},
                           data={'output_format': 'json'})
        assert resp.status_code == 500
        assert 'init failed' in _error(resp)['error']

    @patch('web_app.DocumentProcessor')
    def test_output_not_found(self, mock_cls, client):
        """process_file returns True but output file doesn't exist."""
        mock = MagicMock()
        mock.ai_enabled = True
        mock.process_file.return_value = True
        mock_cls.return_value = mock
        resp = client.post('/api/convert', files={'file': _file('ghost.pdf', b'%PDF-1')},
                           data={'output_format': 'json'})
        assert resp.status_code == 500
        assert 'not generated' in _error(resp)['error']


class TestUploadExtended:
    @patch('web_app.process_file_job')
    def test_upload_creates_job(self, mock_job, client):
        resp = client.post('/api/upload', files={'files[]': _file('test.pdf', b'%PDF-1')},
                           data={'ai_enhancement': 'true'})
        assert resp.status_code == 200
        assert len(resp.json()['job_ids']) == 1

    @patch('web_app.process_file_job')
    def test_upload_mixed_formats(self, mock_job, client):
        """Upload both supported and unsupported files; mp4 is skipped."""
        resp = client.post('/api/upload', files=[
            ('files[]', _file('good.pdf', b'%PDF-1')),
            ('files[]', _file('bad.mp4', b'\x00\x00')),
        ], data={'ai_enhancement': 'false'})
        data = resp.json()
        assert len(data['job_ids']) == 1
        assert 'bad.mp4' in data.get('skipped', [])


class TestJobsExtended:
    def test_job_status_lifecycle(self):
        assert JobStatus.QUEUED == 'queued'
        assert JobStatus.PROCESSING == 'processing'
        assert JobStatus.COMPLETED == 'completed'
        assert JobStatus.FAILED == 'failed'

    def test_download_incomplete_job(self, client):
        job_id = 'test-incomplete-job'
        with jobs_lock:
            jobs[job_id] = {'id': job_id, 'status': JobStatus.PROCESSING, 'filename': 'test.pdf'}
        try:
            resp = client.get(f'/api/download/{job_id}')
            assert resp.status_code == 400
            assert 'not completed' in _error(resp)['error']
        finally:
            with jobs_lock:
                jobs.pop(job_id, None)

    def test_get_specific_job(self, client):
        job_id = 'test-specific-job'
        with jobs_lock:
            jobs[job_id] = {'id': job_id, 'status': JobStatus.COMPLETED, 'filename': 'test.pdf'}
        try:
            resp = client.get(f'/api/jobs/{job_id}')
            assert resp.status_code == 200
            assert resp.json()['status'] == 'completed'
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
            assert jobs[job_id]['output_file'] == str(out_file)
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
    def test_413_handler_registered(self):
        assert 413 in app.exception_handlers
