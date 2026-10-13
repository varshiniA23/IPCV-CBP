"""
Fingerprint Image Enhancement for Forensic Identification
==========================================================
A Flask-based forensic tool that enhances latent fingerprint images
using advanced digital image processing techniques.

Techniques Applied:
  - Grayscale conversion & preprocessing
  - Adaptive histogram equalization (CLAHE)
  - Gaussian & Median noise removal
  - Gabor filter ridge enhancement
  - Morphological operations
  - Binarization & Skeletonization

Metrics:
  - PSNR (Peak Signal-to-Noise Ratio)
  - SSIM (Structural Similarity Index)
  - Contrast Improvement Index
"""

import os
import io
import base64
import uuid
import numpy as np
from flask import Flask, render_template, request, jsonify
from PIL import Image
import cv2
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
from scipy.ndimage import rotate

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

UPLOAD_FOLDER = os.path.join('static', 'uploads')
RESULT_FOLDER = os.path.join('static', 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


# ────────────────────────────────────────────────────────────────────────────
# Core Enhancement Pipeline
# ────────────────────────────────────────────────────────────────────────────

def load_image_from_bytes(file_bytes):
    """Load image from bytes and convert to grayscale numpy array."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return img


def normalize_image(img):
    """Normalize image to 0-255 uint8."""
    img = img.astype(np.float64)
    img = (img - img.min()) / (img.max() - img.min() + 1e-8) * 255
    return img.astype(np.uint8)


def apply_clahe(img, clip_limit=3.0, tile_grid=8):
    """Apply Contrast Limited Adaptive Histogram Equalization."""
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(tile_grid, tile_grid)
    )
    return clahe.apply(img)


def apply_denoise(img):
    """Apply Gaussian blur followed by Median filter to remove noise."""
    gauss = cv2.GaussianBlur(img, (3, 3), sigmaX=0.8)
    median = cv2.medianBlur(gauss, 3)
    return median


def apply_gabor_filter(img):
    """
    Enhance fingerprint ridges using a bank of Gabor filters
    at multiple orientations (0 to 157.5 degrees).
    """
    accumulated = np.zeros_like(img, dtype=np.float64)
    orientations = np.linspace(0, np.pi, 8, endpoint=False)

    for theta in orientations:
        kernel = cv2.getGaborKernel(
            ksize=(21, 21),
            sigma=4.0,
            theta=theta,
            lambd=10.0,
            gamma=0.5,
            psi=0,
            ktype=cv2.CV_64F
        )
        filtered = cv2.filter2D(img.astype(np.float64), cv2.CV_64F, kernel)
        accumulated = np.maximum(accumulated, filtered)

    accumulated = normalize_image(accumulated)
    return accumulated


def apply_unsharp_mask(img, strength=1.5):
    """Sharpen ridges using unsharp masking."""
    blur = cv2.GaussianBlur(img.astype(np.float64), (9, 9), sigmaX=2.0)
    sharp = img.astype(np.float64) + strength * (img.astype(np.float64) - blur)
    return normalize_image(sharp)


def apply_morphology(img):
    """Apply morphological closing to fill ridge gaps."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    closed = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    return closed


def apply_binarization(img):
    """
    Adaptive thresholding to binarize the fingerprint ridge map.
    Uses Otsu's method for optimal threshold selection.
    """
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    binary = cv2.bitwise_not(binary)
    return binary


def compute_metrics(original, enhanced):
    """
    Compute image quality improvement metrics.
    """
    orig_f = original.astype(np.float64)
    enh_f = enhanced.astype(np.float64)

    try:
        psnr_val = psnr(original, enhanced, data_range=255)
    except Exception:
        psnr_val = 0.0

    try:
        ssim_val = ssim(original, enhanced, data_range=255)
    except Exception:
        ssim_val = 0.0

    orig_std = np.std(orig_f)
    enh_std = np.std(enh_f)
    cii = float(enh_std / (orig_std + 1e-8))

    orig_brightness = float(np.mean(orig_f))
    enh_brightness = float(np.mean(enh_f))

    quality = min(100.0, max(0.0, (
        (min(psnr_val, 50) / 50) * 40 +
        ssim_val * 40 +
        min(cii, 2.0) / 2.0 * 20
    )))

    return {
        "psnr": round(float(psnr_val), 2),
        "ssim": round(float(ssim_val), 4),
        "cii": round(cii, 3),
        "orig_brightness": round(orig_brightness, 1),
        "enh_brightness": round(enh_brightness, 1),
        "orig_std": round(orig_std, 2),
        "enh_std": round(enh_std, 2),
        "quality_score": round(quality, 1),
    }


def img_to_base64(img):
    """Convert numpy image array to base64-encoded PNG string."""
    success, encoded = cv2.imencode('.png', img)
    if not success:
        raise ValueError("Failed to encode image")
    return base64.b64encode(encoded.tobytes()).decode('utf-8')


def full_pipeline(img):
    """
    Run the complete enhancement pipeline.
    Returns (denoised, clahe_img, gabor_img, final_enhanced)
    """
    denoised = apply_denoise(img)
    clahe_img = apply_clahe(denoised)
    gabor_img = apply_gabor_filter(clahe_img)
    sharpened = apply_unsharp_mask(gabor_img)
    final = apply_morphology(sharpened)
    return denoised, clahe_img, gabor_img, final


# ────────────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/enhance', methods=['POST'])
def enhance():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    allowed = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'pgm'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        return jsonify({'error': f'Unsupported file type: .{ext}'}), 400

    try:
        file_bytes = file.read()
        original = load_image_from_bytes(file_bytes)

        if original is None:
            return jsonify({'error': 'Could not decode image'}), 400

        max_dim = 800
        h, w = original.shape
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            original = cv2.resize(original, (int(w * scale), int(h * scale)))

        denoised, clahe_img, gabor_img, enhanced = full_pipeline(original)
        binary = apply_binarization(enhanced.copy())
        metrics = compute_metrics(original, enhanced)

        result = {
            'original':  img_to_base64(original),
            'denoised':  img_to_base64(denoised),
            'clahe':     img_to_base64(clahe_img),
            'gabor':     img_to_base64(gabor_img),
            'enhanced':  img_to_base64(enhanced),
            'binary':    img_to_base64(binary),
            'metrics':   metrics,
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate_sample', methods=['POST'])
def generate_sample():
    """Generate a synthetic fingerprint-like test image."""
    try:
        size = 300
        img = np.zeros((size, size), dtype=np.uint8)

        cx, cy = size // 2, size // 2
        for r in range(10, size // 2, 10):
            cv2.ellipse(img, (cx, cy), (r, int(r * 0.7)), 15, 0, 360, 180, 1)

        for r in range(5, size // 2, 12):
            for angle in np.linspace(0, 2 * np.pi, max(6, int(r * 0.6))):
                x = int(cx + r * np.cos(angle))
                y = int(cy + r * np.sin(angle))
                if 0 <= x < size and 0 <= y < size:
                    cv2.circle(img, (x, y), 1, 200, -1)

        noise = np.random.normal(0, 25, img.shape).astype(np.float64)
        img = np.clip(img.astype(np.float64) + noise, 0, 255).astype(np.uint8)
        img = cv2.GaussianBlur(img, (7, 7), 2)

        original_b64 = img_to_base64(img)
        denoised, clahe_img, gabor_img, enhanced = full_pipeline(img)
        binary = apply_binarization(enhanced.copy())
        metrics = compute_metrics(img, enhanced)

        return jsonify({
            'original':  original_b64,
            'denoised':  img_to_base64(denoised),
            'clahe':     img_to_base64(clahe_img),
            'gabor':     img_to_base64(gabor_img),
            'enhanced':  img_to_base64(enhanced),
            'binary':    img_to_base64(binary),
            'metrics':   metrics,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("  Fingerprint Image Enhancement for Forensic Identification")
    print("  Running at: http://127.0.0.1:5001")
    print("=" * 80)
    app.run(debug=False, host='127.0.0.1', port=5001)
