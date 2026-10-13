/* =====================================================
   main.js – Fingerprint Forensic Studio
   ===================================================== */

'use strict';

// ── DOM refs ──────────────────────────────────────────
const fileInput       = document.getElementById('file-input');
const dropZone        = document.getElementById('drop-zone');
const processingBar   = document.getElementById('processing-bar');
const resultsSection  = document.getElementById('results-section');
const toastEl         = document.getElementById('toast');
const lightbox        = document.getElementById('lightbox');
const lightboxImg     = document.getElementById('lightbox-img');
const btnSample       = document.getElementById('btn-sample');
const btnNewAnalysis  = document.getElementById('btn-new-analysis');

// ── State ──────────────────────────────────────────────
let currentResults = null;

// ── Toast ──────────────────────────────────────────────
function showToast(msg, type = 'error') {
  toastEl.textContent = msg;
  toastEl.className   = `toast ${type}`;
  toastEl.style.display = 'block';
  setTimeout(() => { toastEl.style.display = 'none'; }, 4000);
}

// ── Lightbox ───────────────────────────────────────────
function openLightbox(src) {
  lightboxImg.src = src;
  lightbox.classList.add('open');
}
document.getElementById('lightbox-close').addEventListener('click', () => {
  lightbox.classList.remove('open');
});
lightbox.addEventListener('click', e => {
  if (e.target === lightbox) lightbox.classList.remove('open');
});

// ── Drag & Drop ────────────────────────────────────────
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) processFile(file);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) processFile(fileInput.files[0]);
});

// ── Upload button is a <label for="file-input"> — handled natively ──────────

// ── Sample button ──────────────────────────────────────
btnSample.addEventListener('click', async (e) => {
  e.stopPropagation();
  showProcessing('Generating synthetic fingerprint…');
  try {
    const res  = await fetch('/generate_sample', { method: 'POST' });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    currentResults = data;
    renderResults(data);
    showToast('Sample fingerprint generated!', 'success');
  } catch (err) {
    showToast('Error: ' + err.message);
  } finally {
    hideProcessing();
  }
});

// ── New analysis ───────────────────────────────────────
btnNewAnalysis.addEventListener('click', () => {
  resultsSection.classList.remove('visible');
  dropZone.scrollIntoView({ behavior: 'smooth' });
  fileInput.value = '';
  currentResults = null;
});

// ── Process uploaded file ─────────────────────────────
async function processFile(file) {
  const allowed = ['image/png','image/jpeg','image/bmp','image/tiff'];
  if (!allowed.includes(file.type) && !file.name.match(/\.(pgm|tif)$/i)) {
    showToast('Please upload PNG, JPG, BMP, TIF, or PGM images only.');
    return;
  }
  if (file.size > 16 * 1024 * 1024) {
    showToast('File too large. Maximum size is 16 MB.');
    return;
  }

  showProcessing(`Processing "${file.name}"…`);
  const formData = new FormData();
  formData.append('image', file);

  try {
    const res  = await fetch('/enhance', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    currentResults = data;
    renderResults(data);
    showToast('Enhancement complete!', 'success');
  } catch (err) {
    showToast('Error: ' + err.message);
  } finally {
    hideProcessing();
  }
}

// ── Processing UI ──────────────────────────────────────
function showProcessing(label) {
  document.getElementById('proc-label').textContent = label;
  processingBar.classList.add('visible');
  resultsSection.classList.remove('visible');
}
function hideProcessing() {
  processingBar.classList.remove('visible');
}

// ── Render Results ────────────────────────────────────
function renderResults(data) {
  const { original, denoised, clahe, gabor, enhanced, binary, metrics } = data;

  // Pipeline stages
  const stages = [
    { key: 'original',  step: 'Step 0', name: 'Original Input',      desc: 'Raw grayscale fingerprint image',         src: original },
    { key: 'denoised',  step: 'Step 1', name: 'Noise Removal',        desc: 'Gaussian + Median filter applied',        src: denoised },
    { key: 'clahe',     step: 'Step 2', name: 'CLAHE Enhancement',    desc: 'Adaptive histogram equalization',         src: clahe    },
    { key: 'gabor',     step: 'Step 3', name: 'Gabor Ridge Filter',   desc: '8-orientation Gabor bank applied',        src: gabor    },
    { key: 'enhanced',  step: 'Step 4', name: 'Final Enhanced',       desc: 'Unsharp mask + morphological closing',    src: enhanced },
    { key: 'binary',    step: 'Step 5', name: 'Binarized (Otsu)',     desc: 'Ridge map ready for matching',            src: binary   },
  ];

  const pipelineGrid = document.getElementById('pipeline-grid');
  pipelineGrid.innerHTML = stages.map(s => `
    <div class="pipeline-card" onclick="openLightbox('data:image/png;base64,${s.src}')">
      <img src="data:image/png;base64,${s.src}" alt="${s.name}" />
      <div class="pipeline-label">
        <div class="pipeline-step">${s.step}</div>
        <div class="pipeline-name">${s.name}</div>
        <div class="pipeline-desc">${s.desc}</div>
      </div>
    </div>
  `).join('');

  // Comparison
  document.getElementById('cmp-original').src = `data:image/png;base64,${original}`;
  document.getElementById('cmp-enhanced').src = `data:image/png;base64,${enhanced}`;

  // Metrics
  document.getElementById('m-psnr').textContent   = metrics.psnr + ' dB';
  document.getElementById('m-ssim').textContent   = (metrics.ssim * 100).toFixed(1) + '%';
  document.getElementById('m-cii').textContent    = metrics.cii.toFixed(2) + '×';
  document.getElementById('m-std-orig').textContent = metrics.orig_std;
  document.getElementById('m-std-enh').textContent  = metrics.enh_std;

  // Quality ring
  const qs   = metrics.quality_score;
  const circ = 2 * Math.PI * 30; // r=30
  const fill = (qs / 100) * circ;
  const ring  = document.getElementById('quality-ring-fill');
  ring.style.strokeDasharray  = circ;
  ring.style.strokeDashoffset = circ - fill;
  ring.style.stroke = qs >= 70 ? '#10d88a' : qs >= 45 ? '#f59e0b' : '#ef4444';
  document.getElementById('quality-score-text').textContent = qs;
  document.getElementById('m-quality-label').textContent =
    qs >= 70 ? 'Excellent' : qs >= 45 ? 'Good' : 'Fair';

  // Detail rows
  document.getElementById('d-brightness-orig').textContent = metrics.orig_brightness;
  document.getElementById('d-brightness-enh').textContent  = metrics.enh_brightness;

  // Download buttons
  document.getElementById('dl-enhanced').onclick = () => downloadBase64(enhanced, 'enhanced_fingerprint.png');
  document.getElementById('dl-binary').onclick   = () => downloadBase64(binary,   'binary_fingerprint.png');

  resultsSection.classList.add('visible');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Download helper ────────────────────────────────────
function downloadBase64(b64, filename) {
  const a = document.createElement('a');
  a.href     = `data:image/png;base64,${b64}`;
  a.download = filename;
  a.click();
}
