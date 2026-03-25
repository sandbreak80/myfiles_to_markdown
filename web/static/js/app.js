const API_BASE = '/api';
const CHUNK_SIZE = 45 * 1024 * 1024;
const CHUNK_THRESHOLD = 45 * 1024 * 1024;
const MAX_FILE_SIZE = 500 * 1024 * 1024;

document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    uploadArea.addEventListener('click', () => {
        if (!uploadArea.classList.contains('uploading')) fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFiles(e.target.files);
        e.target.value = '';
    });

    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
});

function showStatus(msg, isError) {
    const area = document.getElementById('statusArea');
    const msgEl = document.getElementById('statusMessage');
    area.style.display = 'block';
    msgEl.textContent = msg;
    msgEl.className = 'status-message' + (isError ? ' error' : '');
}

function addDownloadLink(filename, jobId) {
    const links = document.getElementById('downloadLinks');
    const link = document.createElement('a');
    link.href = `${API_BASE}/download/${jobId}`;
    link.textContent = `Download ${filename}`;
    link.className = 'btn btn-secondary btn-small';
    link.style.margin = '4px';
    links.appendChild(link);
}

async function handleFiles(files) {
    const uploadArea = document.getElementById('uploadArea');
    document.getElementById('downloadLinks').innerHTML = '';

    for (let file of files) {
        if (file.size > MAX_FILE_SIZE) {
            showStatus(`${file.name} is too large (${(file.size/1024/1024).toFixed(0)}MB). Max 500MB.`, true);
            return;
        }
    }

    const aiEnhancement = document.getElementById('aiEnhancementToggle').checked;
    const aiImageProcessing = document.getElementById('aiImageToggle').checked;
    uploadArea.classList.add('uploading');

    try {
        for (let file of files) {
            showStatus(`Uploading ${file.name}...`);

            let jobId;
            if (file.size > CHUNK_THRESHOLD) {
                jobId = await uploadChunked(file, aiEnhancement, aiImageProcessing);
            } else {
                jobId = await uploadAndGetJob(file, aiEnhancement, aiImageProcessing);
            }

            showStatus(`Converting ${file.name}...`);
            await pollUntilDone(jobId, file.name);
            addDownloadLink(file.name.replace(/\.[^.]+$/, '.md'), jobId);
        }
        showStatus('All files converted successfully.');
    } catch (err) {
        showStatus(err.message, true);
    } finally {
        uploadArea.classList.remove('uploading');
    }
}

async function uploadAndGetJob(file, aiEnhancement, aiImageProcessing) {
    const form = new FormData();
    form.append('files[]', file);
    form.append('ai_enhancement', aiEnhancement);
    form.append('ai_image_processing', aiImageProcessing);

    const r = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form });
    if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        throw new Error(d.detail?.error || d.error || `Upload failed (${r.status})`);
    }
    const d = await r.json();
    if (!d.job_ids || d.job_ids.length === 0) {
        throw new Error(d.skipped ? `Unsupported format: ${d.skipped.join(', ')}` : 'Upload returned no jobs');
    }
    return d.job_ids[0];
}

async function uploadChunked(file, aiEnhancement, aiImageProcessing) {
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

    const initForm = new FormData();
    initForm.append('filename', file.name);
    initForm.append('total_size', file.size);
    initForm.append('total_chunks', totalChunks);
    initForm.append('ai_enhancement', aiEnhancement);
    initForm.append('ai_image_processing', aiImageProcessing);

    let r = await fetch(`${API_BASE}/upload/init`, { method: 'POST', body: initForm });
    if (!r.ok) throw new Error('Failed to start chunked upload');
    const { upload_id } = await r.json();

    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const blob = file.slice(start, Math.min(start + CHUNK_SIZE, file.size));
        const chunkForm = new FormData();
        chunkForm.append('chunk_index', i);
        chunkForm.append('chunk', blob, `chunk_${i}`);

        r = await fetch(`${API_BASE}/upload/chunk/${upload_id}`, { method: 'POST', body: chunkForm });
        if (!r.ok) throw new Error(`Chunk ${i+1}/${totalChunks} failed`);
        showStatus(`Uploading ${file.name}... chunk ${i+1}/${totalChunks}`);
    }

    r = await fetch(`${API_BASE}/upload/complete/${upload_id}`, { method: 'POST' });
    if (!r.ok) throw new Error('Failed to complete upload');
    return (await r.json()).job_id;
}

async function pollUntilDone(jobId, filename) {
    for (let i = 0; i < 300; i++) {
        const r = await fetch(`${API_BASE}/jobs/${jobId}`);
        const d = await r.json();
        if (d.status === 'completed') return;
        if (d.status === 'failed') throw new Error(d.error || `Conversion failed for ${filename}`);
        await new Promise(ok => setTimeout(ok, 2000));
    }
    throw new Error(`Conversion timed out for ${filename}`);
}
