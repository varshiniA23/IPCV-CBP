"""
prepare_ppt_assets.py
Generates presentation-ready figures and output images for the Fingerprint Forensics project.
"""

import os
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import app

os.makedirs('output_images', exist_ok=True)

# 1. Process Sample 1 (images.jpg)
img1_path = 'C:/Users/A Varshini/Downloads/images.jpg'
orig1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
if orig1 is None:
    raise FileNotFoundError(f"Could not load {img1_path}")

denoised1, clahe1, gabor1, enh1 = app.full_pipeline(orig1)
bin1 = app.apply_binarization(enh1.copy())
metrics1 = app.compute_metrics(orig1, enh1)

# 2. Process Sample 2 (img.jpg)
img2_path = 'C:/Users/A Varshini/Downloads/img.jpg'
orig2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
if orig2 is not None:
    # Resize if too large
    if max(orig2.shape) > 800:
        scale = 800 / max(orig2.shape)
        orig2 = cv2.resize(orig2, (int(orig2.shape[1] * scale), int(orig2.shape[0] * scale)))
    denoised2, clahe2, gabor2, enh2 = app.full_pipeline(orig2)
    bin2 = app.apply_binarization(enh2.copy())
    metrics2 = app.compute_metrics(orig2, enh2)
else:
    metrics2 = None

# Save individual clean stage images for Sample 1
cv2.imwrite('output_images/s1_0_raw.png', orig1)
cv2.imwrite('output_images/s1_1_denoised.png', denoised1)
cv2.imwrite('output_images/s1_2_clahe.png', clahe1)
cv2.imwrite('output_images/s1_3_gabor.png', gabor1)
cv2.imwrite('output_images/s1_4_enhanced.png', enh1)
cv2.imwrite('output_images/s1_5_binarized.png', bin1)

if orig2 is not None:
    cv2.imwrite('output_images/s2_0_raw.png', orig2)
    cv2.imwrite('output_images/s2_4_enhanced.png', enh2)
    cv2.imwrite('output_images/s2_5_binarized.png', bin2)

# 3. Create Multi-Panel Pipeline Progression Graphic (6 stages)
plt.style.use('default')
fig, axes = plt.subplots(1, 6, figsize=(18, 3.8), dpi=300)
fig.patch.set_facecolor('#0f172a') # Slate 900 background

stages = [
    (orig1, "Stage 0: Input", "Degraded / Latent", '#94a3b8'),
    (denoised1, "Stage 1: Denoise", "Gaussian + Median", '#38bdf8'),
    (clahe1, "Stage 2: CLAHE", "Local Equalization", '#818cf8'),
    (gabor1, "Stage 3: Gabor", "8 Orientations (21x21)", '#c084fc'),
    (enh1, "Stage 4: Enhanced", "Unsharp + Morphology", '#34d399'),
    (bin1, "Stage 5: Binarized", "Otsu Ridge Skeleton", '#22d3ee')
]

for idx, (img_data, title, sub, color) in enumerate(stages):
    ax = axes[idx]
    ax.imshow(img_data, cmap='gray')
    ax.set_title(title, fontsize=12, fontweight='bold', color=color, pad=8)
    ax.set_xlabel(sub, fontsize=9.5, color='#cbd5e1', labelpad=6)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(color)
        spine.set_linewidth(1.8)

plt.subplots_adjust(wspace=0.12, left=0.03, right=0.97, top=0.85, bottom=0.15)
pipeline_chart_path = 'output_images/pipeline_stages_overview.png'
plt.savefig(pipeline_chart_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()
print("Saved:", pipeline_chart_path)

# 4. Create High-Impact Before vs After Comparison Graphic
fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), dpi=300)
fig.patch.set_facecolor('#ffffff')

comparisons = [
    (orig1, "1. Latent Input Fingerprint", "Low contrast, broken ridges, background noise", '#dc2626'),
    (enh1, "2. Gabor & Morphologically Enhanced", "Sharp continuous ridges, high contrast", '#0284c7'),
    (bin1, "3. Binarized Ridge Skeleton (Otsu)", "Ideal representation for AFIS minutiae matching", '#059669')
]

for idx, (im, t, d, c) in enumerate(comparisons):
    ax = axes[idx]
    ax.imshow(im, cmap='gray')
    ax.set_title(t, fontsize=13, fontweight='bold', color='#0f172a', pad=10)
    ax.set_xlabel(d, fontsize=10, color='#475569', labelpad=8)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(c)
        spine.set_linewidth(2.5)

plt.subplots_adjust(wspace=0.15, left=0.04, right=0.96, top=0.88, bottom=0.12)
before_after_path = 'output_images/before_after_comparison.png'
plt.savefig(before_after_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()
print("Saved:", before_after_path)

# 5. Create Multi-Sample Comparison Graphic (Sample 1 & Sample 2)
if orig2 is not None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor('#ffffff')

    sample_rows = [
        (orig1, enh1, bin1, "Sample 1 (Latent Impression)"),
        (orig2, enh2, bin2, "Sample 2 (Plain Impression)")
    ]

    for row_idx, (r_orig, r_enh, r_bin, row_title) in enumerate(sample_rows):
        for col_idx, (im, col_title, border_col) in enumerate([
            (r_orig, "Raw Input", '#64748b'),
            (r_enh, "Enhanced Ridges", '#0284c7'),
            (r_bin, "Binarized Skeleton", '#10b981')
        ]):
            ax = axes[row_idx, col_idx]
            ax.imshow(im, cmap='gray')
            ax.set_title(f"{row_title} - {col_title}", fontsize=11, fontweight='bold', color='#1e293b', pad=8)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_color(border_col)
                spine.set_linewidth(2.0)

    plt.subplots_adjust(wspace=0.15, hspace=0.25, left=0.04, right=0.96, top=0.92, bottom=0.08)
    multi_sample_path = 'output_images/multi_sample_comparison.png'
    plt.savefig(multi_sample_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print("Saved:", multi_sample_path)

# 6. Create Metrics & Histogram Analysis Graphic
fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), dpi=300)
fig.patch.set_facecolor('#ffffff')

# Subplot 1: Pixel Intensity Histogram (Original vs Enhanced)
ax1 = axes[0]
ax1.hist(orig1.ravel(), bins=60, color='#94a3b8', alpha=0.65, label='Original (Faint & Skewed)', density=True)
ax1.hist(enh1.ravel(), bins=60, color='#0284c7', alpha=0.65, label='Enhanced (Distinct Ridges)', density=True)
ax1.set_title("Pixel Intensity Distribution (Histogram)", fontsize=12, fontweight='bold', color='#0f172a', pad=10)
ax1.set_xlabel("Pixel Intensity (0 - 255)", fontsize=10, color='#334155')
ax1.set_ylabel("Normalized Density", fontsize=10, color='#334155')
ax1.legend(loc='upper right', frameon=True, fontsize=9.5)
ax1.grid(True, linestyle='--', alpha=0.3)
for spine in ax1.spines.values():
    spine.set_color('#cbd5e1')

# Subplot 2: Quality & Metric Score Bar Chart
ax2 = axes[1]
metric_labels = ['PSNR (dB)', 'SSIM (x100)', 'CII (Contrast)', 'Quality Score']
metric_values = [
    metrics1['psnr'],
    metrics1['ssim'] * 100,
    metrics1['cii'] * 20,
    metrics1['quality_score']
]
colors = ['#38bdf8', '#818cf8', '#f59e0b', '#10b981']
bars = ax2.bar(metric_labels, metric_values, color=colors, width=0.55, edgecolor='#334155', linewidth=1.2)
ax2.set_title("Quantitative Metric Profile (Sample 1)", fontsize=12, fontweight='bold', color='#0f172a', pad=10)
ax2.set_ylabel("Metric Value / Scale", fontsize=10, color='#334155')
ax2.grid(axis='y', linestyle='--', alpha=0.3)
for spine in ax2.spines.values():
    spine.set_color('#cbd5e1')

# Add values above bars
for bar in bars:
    height = bar.get_height()
    ax2.annotate(f'{height:.1f}',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 4), textcoords="offset points",
                 ha='center', va='bottom', fontsize=10, fontweight='bold', color='#0f172a')

plt.subplots_adjust(wspace=0.25, left=0.06, right=0.96, top=0.88, bottom=0.15)
metrics_chart_path = 'output_images/metrics_distribution_chart.png'
plt.savefig(metrics_chart_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()
print("Saved:", metrics_chart_path)

print("All assets prepared successfully!")
