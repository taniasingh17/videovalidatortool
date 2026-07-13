import streamlit as st
import threading
import http.server
import os
import socket
import tempfile
import time

st.set_page_config(page_title="Video Validator Tool", layout="wide")
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; }
        header { visibility: hidden; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/mediainfo.js@0.3.7/dist/umd/index.min.js" integrity="sha384-3Oz6Jpgi4ju60E2vE6C1Fb3rpTfrKKKhC4VbQwnfkewpiPhP49uWVAJNml2p8JYC" crossorigin="anonymous"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Manrope', sans-serif; font-weight: 400; }
        body { background-color: #FAFAFA; color: #0F172A; padding-bottom: 250px; }
        .container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

        header {
            background-color: #111827;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 3rem;
            border-bottom: 4px solid #0F172A;
        }
        header h1 {
            color: #FFFFFF;
            font-size: 36px;
            font-weight: 400;
            letter-spacing: 2px;
        }

        /* KPI Cards */
        .summary-dashboard {
            display: none;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 2rem;
        }
        .summary-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .summary-value { font-size: 28px; font-weight: 400; line-height: 1; }
        .summary-label {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            font-size: 11px;
            color: #64748B;
            text-transform: uppercase;
            font-weight: 400;
            letter-spacing: 0.5px;
            margin-top: 10px;
        }

        /* Dropzone */
        .upload-section {
            background-color: #FFFFFF;
            border: 1.5px dashed #CBD5E1;
            padding: 50px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-bottom: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }
        .upload-section:hover, .upload-section.dragover {
            border-color: #0F172A;
            background-color: #F8FAFC;
        }
        .upload-icon { width: 42px; height: 42px; color: #64748B; margin-bottom: 12px; transition: color 0.2s ease; }
        .upload-section:hover .upload-icon { color: #0F172A; }
        .upload-text { color: #0F172A; font-size: 15px; font-weight: 400; letter-spacing: 0.3px; }
        .upload-subtext { color: #64748B; font-size: 13px; margin-top: 6px; font-weight: 400; }
        #file-input { display: none; }

        /* Tables */
        .table-wrapper { background: transparent; margin-bottom: 3rem; display: none; }
        .table-header-title {
            padding: 0 0 12px 0;
            font-size: 18px;
            font-weight: 400;
            color: #334155;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .table-container {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            overflow: visible;
        }
        table { width: 100%; border-collapse: collapse; table-layout: fixed; }
        th {
            background-color: #2C0A38;
            color: #FFFFFF;
            padding: 10px 16px;
            font-size: 11px;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            text-align: center;
            white-space: nowrap;
        }
        th:nth-child(1) { text-align: left; }
        .th-content { display: flex; align-items: center; gap: 8px; }
        th:not(:nth-child(1)) .th-content { justify-content: center; }
        .th-content svg { width: 14px; height: 14px; fill: #FFFFFF; }
        td {
            padding: 14px 16px;
            font-size: 13px;
            color: #0F172A;
            text-align: center;
            border-bottom: 1px solid #E2E8F0;
            vertical-align: middle;
            word-break: break-word;
            overflow-wrap: anywhere;
            font-weight: 400;
        }
        td:nth-child(1) { text-align: left; }
        tr:last-child td { border-bottom: none; }
        tr.data-row:hover td { background-color: #F8FAFC !important; }

        th:nth-child(1), td:nth-child(1) { width: 28%; }
        th:nth-child(2), td:nth-child(2) { width: 12%; }
        th:nth-child(3), td:nth-child(3) { width: 13%; }
        th:nth-child(4), td:nth-child(4) { width: 13%; }
        th:nth-child(5), td:nth-child(5) { width: 16%; }
        th:nth-child(6), td:nth-child(6) { width: 18%; }

        .status-container { display: flex; flex-direction: column; gap: 4px; }
        .status-main { display: flex; align-items: center; justify-content: center; gap: 8px; font-weight: 400; font-size: 13px; }
        .status-text-pass { color: #22C55E; }
        .status-text-fail { color: #DC2626; }
        .text-error-detail { color: #DC2626; font-weight: 400; }

        /* Clear button */
        .action-bar-container { display: none; justify-content: center; margin-top: 2rem; margin-bottom: 2rem; }
        .clear-btn {
            background-color: #111827;
            color: #FFFFFF;
            border: none;
            padding: 12px 24px;
            font-size: 13px;
            font-weight: 400;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: background-color 0.2s, transform 0.1s;
        }
        .clear-btn:hover { background-color: #334155; }
        .clear-btn:active { transform: scale(0.98); }

        /* Error banner */
        .mediainfo-error {
            display: none;
            background: #FEF2F2;
            border: 1px solid #FECACA;
            color: #DC2626;
            font-size: 13px;
            padding: 10px 16px;
            margin-bottom: 1rem;
            text-align: center;
        }

        /* Footer */
        .app-footer {
            margin-top: 5rem;
            padding-top: 24px;
            border-top: 1px solid #E2E8F0;
            text-align: center;
            font-size: 12px;
            color: #64748B;
            line-height: 1.6;
            letter-spacing: 0.5px;
        }
        .app-footer strong { color: #0F172A; font-weight: 600; }
        .app-footer-team { font-size: 11px; text-transform: uppercase; color: #94A3B8; font-weight: 500; margin-top: 2px; letter-spacing: 1px; }
    </style>
</head>
<body>
    <header><h1>Video Validator Tool</h1></header>
    <div class="container">

        <div class="mediainfo-error" id="mediainfo-error">
            Codec checker unavailable — check your internet connection and reload.
        </div>

        <div class="summary-dashboard" id="summary-dashboard">
            <div class="summary-card">
                <div class="summary-value" style="color:#22C55E;" id="count-pass">0</div>
                <div class="summary-label">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Compliant
                </div>
            </div>
            <div class="summary-card">
                <div class="summary-value" style="color:#DC2626;" id="count-fail">0</div>
                <div class="summary-label">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Non-Compliant
                </div>
            </div>
        </div>

        <div class="upload-section" id="dropzone" onclick="document.getElementById('file-input').click();">
            <svg class="upload-icon" id="upload-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
            </svg>
            <span class="upload-text" id="upload-main-text">Drag &amp; drop your video files here</span>
            <span class="upload-subtext" id="upload-sub-text">or click to browse files</span>
            <input type="file" id="file-input" multiple>
        </div>

        <div class="table-wrapper" id="wrapper-fail">
            <div class="table-header-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                Non-Compliant
            </div>
            <div class="table-container">
                <table>
                    <thead id="thead-fail"></thead>
                    <tbody id="tbody-fail"></tbody>
                </table>
            </div>
        </div>

        <div class="table-wrapper" id="wrapper-pass">
            <div class="table-header-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 11.08V12a10 10 0 11-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Compliant
            </div>
            <div class="table-container">
                <table>
                    <thead id="thead-pass"></thead>
                    <tbody id="tbody-pass"></tbody>
                </table>
            </div>
        </div>

        <div class="action-bar-container" id="action-bar">
            <button class="clear-btn" onclick="clearResults()">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                Clear All Results
            </button>
        </div>

        <footer class="app-footer">
            <div>Made by <strong>TANIA SINGH</strong></div>
            <div class="app-footer-team">MiQ Ad Ops Team</div>
        </footer>
    </div>

    <script>
        const thRowHTML = `
            <tr>
                <th><div class="th-content"><svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg> FILE NAME</div></th>
                <th><div class="th-content"><svg viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z"/></svg> FILE TYPE</div></th>
                <th><div class="th-content"><svg viewBox="0 0 24 24"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14zM5 15h14v3H5z"/></svg> SIZE</div></th>
                <th><div class="th-content"><svg viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"/></svg> DURATION</div></th>
                <th><div class="th-content"><svg viewBox="0 0 24 24"><path d="M12 3v9.28a4.39 4.39 0 00-1.5-.28C8.01 12 6 14.01 6 16.5S8.01 21 10.5 21c2.31 0 4.2-1.75 4.45-4H15V6h4V3h-6.5z"/></svg> AUDIO CODEC</div></th>
                <th><div class="th-content"><svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg> STATUS</div></th>
            </tr>
        `;
        document.getElementById('thead-fail').innerHTML = thRowHTML;
        document.getElementById('thead-pass').innerHTML = thRowHTML;

        // State
        let processedFiles = new Set();
        let compliantCount = 0;
        let nonCompliantCount = 0;
        let passRows = [];
        let failRows = [];

        // Initialise MediaInfo.js once; reuse the same instance for all files
        // The UMD bundle exposes the factory on .default in some environments
        const mediaInfoPromise = (async () => {
            const factory = (typeof MediaInfo === 'function')
                ? MediaInfo
                : (MediaInfo && typeof MediaInfo.default === 'function' ? MediaInfo.default : null);
            if (!factory) {
                document.getElementById('mediainfo-error').style.display = 'block';
                throw new Error('MediaInfo not loaded');
            }
            try {
                return await factory({
                    format: 'object',
                    locateFile: () => 'https://cdn.jsdelivr.net/npm/mediainfo.js@0.3.7/dist/MediaInfoModule.wasm'
                });
            } catch (err) {
                document.getElementById('mediainfo-error').style.display = 'block';
                throw err;
            }
        })();

        function formatDuration(ms) {
            if (ms == null || isNaN(ms)) return '-';
            const totalSec = Math.round(ms / 1000);
            const m = Math.floor(totalSec / 60);
            const s = totalSec % 60;
            return m + ':' + String(s).padStart(2, '0');
        }

        function esc(s) {
            return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
        }

        const iconPass = `<svg width="18" height="18" viewBox="0 0 24 24" fill="#22C55E"><circle cx="12" cy="12" r="11"/><path d="M8 12.5L10.5 15L16 9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
        const iconFail = `<svg width="18" height="18" viewBox="0 0 24 24" fill="#DC2626"><circle cx="12" cy="12" r="11"/><path d="M15 9L9 15M9 9L15 15" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

        function appendRow(name, displayExt, sizeStr, durationStr, codecStr, status, errors) {
            const isPass = status === 'Pass';

            // Size cell — red if over limit
            const sizeCell = (sizeStr !== '-' && sizeStr.includes('MB') && parseFloat(sizeStr) > 250)
                ? `<span class="text-error-detail">${esc(sizeStr)}</span>`
                : esc(sizeStr);

            // Codec cell — red if not AAC and not placeholder
            const codecCell = (codecStr !== '-' && codecStr !== 'None' && codecStr.toUpperCase() !== 'AAC')
                ? `<span class="text-error-detail">${esc(codecStr)}</span>`
                : esc(codecStr);

            // Ext cell — red if not mp4
            const extCell = (displayExt !== '-' && displayExt !== '.mp4')
                ? `<span class="text-error-detail">${esc(displayExt)}</span>`
                : esc(displayExt);

            // Error bullets
            const msgHtml = errors
                .map(e => `<div class="text-error-detail" style="font-size:12px;line-height:1.25;">• ${esc(e)}</div>`)
                .join('');

            const statusBlock = isPass
                ? `<div class="status-container"><div class="status-main status-text-pass">${iconPass} Pass</div></div>`
                : `<div class="status-container"><div class="status-main status-text-fail">${iconFail} Fail</div>${msgHtml}</div>`;

            const tr = `<tr class="data-row">
        <td>${esc(name)}</td>
        <td>${extCell}</td>
        <td>${sizeCell}</td>
        <td>${esc(durationStr)}</td>
        <td>${codecCell}</td>
        <td>${statusBlock}</td>
    </tr>`;

            if (isPass) {
                compliantCount++;
                passRows.push(tr);
            } else {
                nonCompliantCount++;
                failRows.push(tr);
            }
        }

        async function handleFiles(files) {
            document.getElementById('upload-main-text').innerText = 'Processing files…';
            document.getElementById('upload-icon-svg').style.color = '#3B82F6';
            await new Promise(r => setTimeout(r, 50)); // let UI paint

            let mi;
            try {
                mi = await mediaInfoPromise;
            } catch (_) {
                document.getElementById('upload-main-text').innerText = 'Drag & drop your video files here';
                document.getElementById('upload-icon-svg').style.color = '#64748B';
                return;
            }

            for (const file of files) {
                const fileId = file.name + '_' + file.size;
                if (processedFiles.has(fileId)) continue;
                processedFiles.add(fileId);

                const sizeKB = file.size / 1024;
                const sizeMB = file.size / (1024 * 1024);
                const sizeStr = sizeMB >= 1
                    ? sizeMB.toFixed(1) + ' MB'
                    : sizeKB.toFixed(1) + ' KB';

                const rawExt = file.name.split('.').pop();
                const logicExt = rawExt.toLowerCase();
                const displayExt = '.' + logicExt;

                const errors = [];
                let status = 'Pass';
                let durationStr = '-';
                let codecStr = '-';

                // 1. File type check
                if (logicExt !== 'mp4') {
                    status = 'Fail';
                    errors.push('Invalid format: ' + displayExt);
                    appendRow(file.name, displayExt, '-', '-', '-', status, errors);
                    continue;
                }

                // 2. Size check
                if (sizeMB > 250) {
                    status = 'Fail';
                    errors.push('File exceeds 250 MB limit');
                }

                // 3. Audio codec check via MediaInfo.js
                try {
                    const getSize = () => file.size;
                    const readChunk = (chunkSize, offset) =>
                        new Promise((resolve, reject) => {
                            const reader = new FileReader();
                            reader.onload = (e) => {
                                if (e.target.error) reject(e.target.error);
                                else resolve(new Uint8Array(e.target.result));
                            };
                            reader.onerror = () => reject(reader.error);
                            reader.readAsArrayBuffer(file.slice(offset, offset + chunkSize));
                        });

                    const result = await mi.analyzeData(getSize, readChunk);
                    const tracks = result.media ? result.media.track : [];
                    const audioTrack = tracks.find(t => t['@type'] === 'Audio');
                    const generalTrack = tracks.find(t => t['@type'] === 'General');

                    if (generalTrack && generalTrack.Duration) {
                        durationStr = formatDuration(parseFloat(generalTrack.Duration) * 1000);
                    }

                    if (!audioTrack) {
                        codecStr = 'None';
                        status = 'Fail';
                        errors.push('No audio track detected');
                    } else {
                        const fmt = (audioTrack.Format || '').toUpperCase();
                        codecStr = audioTrack.Format || 'Unknown';
                        if (fmt !== 'AAC') {
                            status = 'Fail';
                            errors.push('Audio codec is ' + (audioTrack.Format || 'unknown') + ', must be AAC');
                        }
                    }
                } catch (_) {
                    codecStr = 'Unreadable';
                    status = 'Fail';
                    errors.push('Could not read audio metadata');
                }

                appendRow(file.name, displayExt, sizeStr, durationStr, codecStr, status, errors);
            }

            // Flush rows to DOM
            document.getElementById('tbody-pass').innerHTML = passRows.join('');
            document.getElementById('tbody-fail').innerHTML = failRows.join('');

            document.getElementById('upload-main-text').innerText = 'Drag & drop your video files here';
            document.getElementById('upload-icon-svg').style.color = '#64748B';
            updateSummary();
        }

        function updateSummary() {
            document.getElementById('count-pass').innerText = compliantCount;
            document.getElementById('count-fail').innerText = nonCompliantCount;
            const total = compliantCount + nonCompliantCount;
            document.getElementById('summary-dashboard').style.display = total > 0 ? 'grid' : 'none';
            document.getElementById('action-bar').style.display = total > 0 ? 'flex' : 'none';
            document.getElementById('wrapper-fail').style.display = nonCompliantCount > 0 ? 'block' : 'none';
            document.getElementById('wrapper-pass').style.display = compliantCount > 0 ? 'block' : 'none';
        }

        // Dropzone events
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('file-input');

        function clearResults() {
            processedFiles.clear();
            compliantCount = 0;
            nonCompliantCount = 0;
            passRows = [];
            failRows = [];
            document.getElementById('tbody-pass').innerHTML = '';
            document.getElementById('tbody-fail').innerHTML = '';
            fileInput.value = '';
            updateSummary();
            window.scrollTo({ top: 0, behavior: 'smooth' });
            try { window.parent.scrollTo({ top: 0, behavior: 'smooth' }); } catch(_) {}
        }

        dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
        dropzone.addEventListener('drop', (e) => { e.preventDefault(); dropzone.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
        fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
    </script>
</body>
</html>
"""

HTML_PORT = 8700

def _find_free_port(preferred):
    for port in range(preferred, preferred + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return preferred

def _write_html_file():
    path = os.path.join(tempfile.gettempdir(), "_video_validator.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_code)
    return path

# Always write the latest HTML (outside cache so edits take effect on reload)
_write_html_file()

@st.cache_resource
def _start_server():
    html_path = os.path.join(tempfile.gettempdir(), "_video_validator.html")
    html_dir = os.path.dirname(html_path)
    html_filename = os.path.basename(html_path)
    port = _find_free_port(HTML_PORT)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=html_dir, **kwargs)
        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.3)
    return port, html_filename

port, filename = _start_server()
st.markdown(
    f'<iframe src="http://localhost:{port}/{filename}" '
    f'width="100%" height="1400" frameborder="0" style="border:none;display:block;"></iframe>',
    unsafe_allow_html=True,
)
