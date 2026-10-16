"""End-to-end browser tests for the web UI (Playwright, headless Chromium).

Drives the real page against the live running container: pick files,
wait for the status message, follow the download links.

Usage:
    BASE_URL=http://localhost:3143 pytest tests/test_e2e_browser.py
"""

import os
import re
import tempfile
import uuid
import csv
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3143")
CONVERT_TIMEOUT_MS = 180_000
AI_TIMEOUT_MS = 600_000


def _create_test_csv(path: Path, rows=5):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'name', 'value'])
        for i in range(rows):
            w.writerow([i, f'row_{i}', i * 2.5])


def _create_test_png(path: Path):
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (320, 120), 'white')
    ImageDraw.Draw(img).text((20, 50), 'Playwright test image', fill='black')
    img.save(path)


def _create_test_docx(path: Path):
    from docx import Document
    doc = Document()
    doc.add_heading('E2E Test Document', level=0)
    doc.add_paragraph('This document was created by the Playwright E2E test.')
    doc.add_heading('Section One', level=1)
    doc.add_paragraph('Automated testing validates the full pipeline.')
    doc.save(path)


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        pg = browser.new_page()
        pg.goto(BASE_URL)
        yield pg
        browser.close()


def _set_ai(page, enhancement: bool, images: bool):
    """Flip the toggles the way a user does: click the visible slider."""
    for toggle_id, want in (('aiEnhancementToggle', enhancement), ('aiImageToggle', images)):
        box = page.locator(f'#{toggle_id}')
        if box.is_checked() != want:
            page.locator(f'label.toggle-switch:has(#{toggle_id}) .toggle-slider').click()
        expect(box).to_be_checked(checked=want)


def _upload_and_wait(page, paths, timeout_ms=CONVERT_TIMEOUT_MS):
    page.locator('#fileInput').set_input_files([str(p) for p in paths])
    expect(page.locator('#statusMessage')).to_have_text(
        re.compile(r'All files converted successfully|failed|error|timed out', re.I),
        timeout=timeout_ms,
    )
    msg = page.locator('#statusMessage').text_content()
    assert 'All files converted successfully' in msg, msg


def _download_text(page, link_index=0):
    link = page.locator('#downloadLinks a').nth(link_index)
    resp = page.request.get(BASE_URL + link.get_attribute('href'))
    assert resp.ok, resp.status
    return resp.text()


def test_page_loads(page):
    assert page.title() != ""
    expect(page.locator('#uploadArea')).to_be_visible()
    expect(page.locator('#aiEnhancementToggle')).to_be_attached()
    expect(page.locator('#aiImageToggle')).to_be_attached()
    # Static assets must load (page is unusable without app.js)
    for asset in ('/static/js/app.js', '/static/css/styles.css'):
        assert page.request.get(BASE_URL + asset).ok, asset


def test_health_endpoint(page):
    resp = page.request.get(f"{BASE_URL}/health")
    assert resp.ok
    assert resp.json()['status'] == 'healthy'


def test_job_api_no_cache_headers(page):
    """Job polling must not be cached by a proxy (Cloudflare)."""
    resp = page.request.get(f"{BASE_URL}/api/jobs/{uuid.uuid4()}")
    assert resp.status == 404
    assert 'no-store' in resp.headers.get('cache-control', '')
    assert resp.headers.get('pragma') == 'no-cache'


def test_upload_csv_and_download(page):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'e2e_test.csv'
        _create_test_csv(p)
        _set_ai(page, False, False)
        _upload_and_wait(page, [p])
        expect(page.locator('#downloadLinks a')).to_have_count(1)
        expect(page.locator('#downloadLinks a').first).to_contain_text('e2e_test.md')
        md = _download_text(page)
        assert 'row_3' in md


def test_upload_docx_and_download(page):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'e2e_test.docx'
        _create_test_docx(p)
        _set_ai(page, False, False)
        _upload_and_wait(page, [p])
        md = _download_text(page)
        assert 'Section One' in md
        assert 'full pipeline' in md


def test_upload_image_without_ai(page):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / f'img_{uuid.uuid4().hex[:8]}.png'
        _create_test_png(p)
        _set_ai(page, False, False)
        _upload_and_wait(page, [p])
        expect(page.locator('#downloadLinks a')).to_have_count(1)


def test_multiple_file_upload(page):
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for i in range(3):
            p = Path(tmp) / f'multi_{i}.csv'
            _create_test_csv(p, rows=i + 2)
            paths.append(p)
        _set_ai(page, False, False)
        _upload_and_wait(page, paths)
        expect(page.locator('#downloadLinks a')).to_have_count(3)


def test_unsupported_format_shows_error(page):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'notes.xyz'
        p.write_text('not a supported format')
        page.locator('#fileInput').set_input_files(str(p))
        expect(page.locator('#statusMessage')).to_have_class(re.compile(r'\berror\b'), timeout=30_000)


@pytest.mark.skipif(os.environ.get("SKIP_AI_TESTS") == "1", reason="SKIP_AI_TESTS=1")
def test_upload_with_ai_enhancement(page):
    """Default UI settings (AI on): needs the configured Ollama to answer."""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'ai_test.docx'
        _create_test_docx(p)
        _set_ai(page, True, True)
        _upload_and_wait(page, [p], timeout_ms=AI_TIMEOUT_MS)
        md = _download_text(page)
        frontmatter = md.split('---')[1] if md.startswith('---') else ''
        assert 'summary:' in frontmatter or 'tags:' in frontmatter, md[:500]
