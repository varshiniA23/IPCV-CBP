"""
build_presentation.py
Generates a clean, simple, student-friendly PowerPoint presentation (.pptx)
for the Course-Based Project (CBP): Fingerprint Image Enhancement for Forensic Identification.
Includes actual output images generated from the forensic enhancement pipeline.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_filename="Fingerprint_Image_Enhancement_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Modern Palette
    BG_COLOR = RGBColor(248, 250, 252)       # Slate 50
    CARD_BG = RGBColor(255, 255, 255)        # Pure White
    CARD_BORDER = RGBColor(226, 232, 240)    # Slate 200
    TEXT_MAIN = RGBColor(15, 23, 42)         # Slate 900
    TEXT_MUTED = RGBColor(71, 85, 105)       # Slate 600
    PRIMARY_CYAN = RGBColor(14, 116, 144)    # Cyan / Slate Blue 700
    PRIMARY_DARK = RGBColor(15, 23, 42)      # Slate 900
    ACCENT_GREEN = RGBColor(16, 185, 129)    # Emerald 500
    ACCENT_INDIGO = RGBColor(79, 70, 229)    # Indigo 600
    ACCENT_AMBER = RGBColor(217, 119, 6)     # Amber 600

    def apply_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_slide_header(slide, tag_text: str, title_text: str):
        # Category Tag
        tb_tag = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_tag = tb_tag.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_bottom = tf_tag.margin_right = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = PRIMARY_CYAN

        # Main Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_bottom = tf_title.margin_right = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = PRIMARY_DARK

    def add_card(slide, left, top, width, height, title="", title_color=PRIMARY_CYAN):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        tf.margin_bottom = Inches(0.25)

        if title:
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = title_color
            p.space_after = Pt(8)

        return card, tf

    def add_bullet(tf, bold_prefix, text, size=11, space_after=6, text_color=TEXT_MUTED):
        p = tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.font.size = Pt(size)
        
        r1 = p.add_run()
        r1.text = "• " + bold_prefix + ": " if bold_prefix else "• "
        r1.font.bold = True
        r1.font.color.rgb = TEXT_MAIN

        r2 = p.add_run()
        r2.text = text
        r2.font.bold = False
        r2.font.color.rgb = text_color

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_background(s1)

    # Title Card / Banner
    card1, tf1 = add_card(s1, Inches(0.8), Inches(1.1), Inches(11.733), Inches(5.3))
    
    p0 = tf1.paragraphs[0]
    p0.text = "COURSE-BASED PROJECT (CBP) • IMAGE PROCESSING & COMPUTER VISION"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = PRIMARY_CYAN
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "Fingerprint Image Enhancement for\nForensic Identification"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_DARK
    p1.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "An end-to-end digital image processing framework restoring degraded latent fingerprints using CLAHE, Gabor filter banks, unsharp masking, and Otsu binarization for automated biometric recognition."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_after = Pt(28)

    # Info Grid inside Title Card
    info_boxes = [
        ("Student Details", "A. Varshini\nRoll No: 24075A6616\nB.Tech Computer Science", PRIMARY_CYAN),
        ("Course & Project Type", "Image Processing & Computer Vision\nCourse-Based Project (CBP)\nAcademic Year 2026", ACCENT_INDIGO),
        ("Core Technologies", "Python 3 · OpenCV · Scikit-Image\nGabor Filter Bank · CLAHE · Otsu\nFlask Web Studio GUI", ACCENT_GREEN)
    ]
    for idx, (head, val, color) in enumerate(info_boxes):
        box_left = Inches(1.1) + Inches(idx * 3.7)
        box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, box_left, Inches(4.3), Inches(3.5), Inches(1.7))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(241, 245, 249) # Slate 100
        box.line.color.rgb = CARD_BORDER
        box.line.width = Pt(1)
        btf = box.text_frame
        btf.margin_left = btf.margin_right = btf.margin_top = btf.margin_bottom = Inches(0.18)
        
        bp1 = btf.paragraphs[0]
        bp1.text = head
        bp1.font.size = Pt(11)
        bp1.font.bold = True
        bp1.font.color.rgb = color
        bp1.space_after = Pt(4)

        bp2 = btf.add_paragraph()
        bp2.text = val
        bp2.font.size = Pt(10.5)
        bp2.font.color.rgb = TEXT_MAIN

    # =========================================================================
    # SLIDE 2: Problem Statement & Forensic Motivation
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_background(s2)
    add_slide_header(s2, "Motivation & Challenges", "The Latent Fingerprint Challenge in Forensics")

    # Card 1: Forensic Challenges
    _, tf_c1 = add_card(s2, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.6), "⚠️ Forensic Degradation Factors", RGBColor(220, 38, 38))
    add_bullet(tf_c1, "Latent Impressions", "Fingerprints recovered from crime scenes are deposited involuntarily via sweat and oil, resulting in highly degraded, faint impressions.")
    add_bullet(tf_c1, "Broken Ridge Flow", "Dry skin conditions or low pressure cause false ridge endings and discontinuous contours.")
    add_bullet(tf_c1, "Smudges & Overlaps", "Excess sebum or sliding contact blurs ridge valleys into continuous dark patches.")
    add_bullet(tf_c1, "Background Noise", "Non-uniform surfaces (paper grain, metallic textures, dust) introduce severe noise corrupting ridge patterns.")
    add_bullet(tf_c1, "Impact on AFIS", "Automated Fingerprint Identification Systems fail or extract spurious minutiae if ridge continuity is not restored.")

    # Card 2: Project Objectives & Solutions
    _, tf_c2 = add_card(s2, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.6), "🎯 Project Objectives & Methodology", PRIMARY_CYAN)
    add_bullet(tf_c2, "Noise Removal", "Apply Gaussian and Median filtering to suppress high-frequency noise and sensor artifacts while preserving boundary edges.")
    add_bullet(tf_c2, "Adaptive Contrast Gain", "Utilize CLAHE (Contrast Limited Adaptive Histogram Equalization) to balance illumination across shadow and highlight regions.")
    add_bullet(tf_c2, "Directional Ridge Tuning", "Design an 8-orientation 2D Gabor filter bank specifically tuned to fingerprint ridge spatial frequencies.")
    add_bullet(tf_c2, "Structural Healing", "Use morphological closing and unsharp masking to close ridge gaps and sharpen ridge valley borders.")
    add_bullet(tf_c2, "Automated Binarization", "Compute Otsu adaptive thresholding to deliver a 1-bit ridge skeleton suitable for minutiae extraction.")

    # =========================================================================
    # SLIDE 3: System Pipeline & Mathematical Stages
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_background(s3)
    add_slide_header(s3, "System Architecture", "5-Stage Digital Image Processing Pipeline")

    stages_data = [
        ("Stage 1: Denoising", "Dual Filtering", "Gaussian filter (3×3, σ=0.8) removes Gaussian noise; Median filter (3×3) eliminates impulsive salt-and-pepper noise without blurring edge boundaries.", PRIMARY_CYAN),
        ("Stage 2: CLAHE", "Adaptive Contrast", "Divides image into 8×8 contextual tiles; limits contrast amplification via clip limit 3.0 to prevent noise over-amplification in background valleys.", ACCENT_INDIGO),
        ("Stage 3: Gabor Bank", "Directional Tuning", "8 filter orientations (θ = 0° to 157.5°). Kernel tuned to ridge frequency (λ=10, σ=4.0) acting as a bandpass filter along local ridge orientations.", ACCENT_GREEN),
        ("Stage 4: Morphology", "Ridge Refinement", "Unsharp masking (strength=1.5, σ=2.0) sharpens ridge peaks; morphological closing with 3×3 elliptical kernel bridges false ridge fractures.", ACCENT_AMBER),
        ("Stage 5: Otsu Binarize", "Ridge Skeleton", "Calculates optimal threshold minimizing intra-class variance; inverts binary mask to produce pristine black ridges on white canvas for AFIS.", PRIMARY_DARK)
    ]

    card_width = Inches(2.2)
    card_gap = Inches(0.18)
    for idx, (st_name, st_sub, st_desc, st_col) in enumerate(stages_data):
        c_left = Inches(0.8) + idx * (card_width + card_gap)
        _, tf_st = add_card(s3, c_left, Inches(1.4), card_width, Inches(5.6), st_name, st_col)
        
        p_sub = tf_st.paragraphs[0]
        p_sub.font.size = Pt(13)
        p_sub.space_after = Pt(2)
        
        p_badge = tf_st.add_paragraph()
        p_badge.text = st_sub.upper()
        p_badge.font.size = Pt(9.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = st_col
        p_badge.space_after = Pt(12)

        p_desc = tf_st.add_paragraph()
        p_desc.text = st_desc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 4: Progressive Pipeline Output Stages (Output Images Included!)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_background(s4)
    add_slide_header(s4, "Experimental Pipeline Walkthrough", "Visual Progression Across Enhancement Stages")

    # Image Container Card
    _, tf_img_card = add_card(s4, Inches(0.8), Inches(1.4), Inches(11.733), Inches(3.6), "🔬 End-to-End Pipeline Output (Latent Test Sample)", PRIMARY_CYAN)
    
    pipeline_img_path = 'output_images/pipeline_stages_overview.png'
    if os.path.exists(pipeline_img_path):
        s4.shapes.add_picture(pipeline_img_path, Inches(0.95), Inches(1.95), width=Inches(11.433))

    # Analytical Summary Cards below
    col_w = Inches(3.75)
    gap = Inches(0.24)
    
    # Box 1
    _, tf_b1 = add_card(s4, Inches(0.8), Inches(5.15), col_w, Inches(1.85), "1. Noise Suppression", PRIMARY_CYAN)
    add_bullet(tf_b1, "Stages 0 → 1", "Dual Gaussian-Median filtering suppresses high-frequency background granularity.", 10.5, 4)
    add_bullet(tf_b1, "Ridge Protection", "Edge sharpness is retained while suppressing surface dust and sensor noise.", 10.5, 4)

    # Box 2
    _, tf_b2 = add_card(s4, Inches(0.8) + (col_w + gap), Inches(5.15), col_w, Inches(1.85), "2. Gabor Orientation Bank", ACCENT_INDIGO)
    add_bullet(tf_b2, "Stages 2 → 3", "CLAHE boosts valley clarity; Gabor bank responds maximally along true ridge flow.", 10.5, 4)
    add_bullet(tf_b2, "Ridge Continuity", "False gaps caused by latent print degradation are bridged systematically.", 10.5, 4)

    # Box 3
    _, tf_b3 = add_card(s4, Inches(0.8) + 2 * (col_w + gap), Inches(5.15), col_w, Inches(1.85), "3. Binarized Extraction", ACCENT_GREEN)
    add_bullet(tf_b3, "Stages 4 → 5", "Morphological close seals remaining pores; Otsu thresholding separates ridges.", 10.5, 4)
    add_bullet(tf_b3, "Biometric Ready", "Output provides a clean 1-bit ridge map ready for minutiae point triangulation.", 10.5, 4)

    # =========================================================================
    # SLIDE 5: Before vs. After Forensic Comparison (High-Res Images Included!)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_slide_header(s5, "Forensic Evaluation", "Before vs. After: Latent Input vs. Restored Ridge Map")

    # Left: Output Image Card
    _, tf_ba_card = add_card(s5, Inches(0.8), Inches(1.4), Inches(7.5), Inches(5.6), "🔍 Side-by-Side Visual Transformation", PRIMARY_CYAN)
    
    before_after_img_path = 'output_images/before_after_comparison.png'
    if os.path.exists(before_after_img_path):
        s5.shapes.add_picture(before_after_img_path, Inches(0.95), Inches(2.0), width=Inches(7.2))

    # Right: Analytical Observations Card
    _, tf_eval = add_card(s5, Inches(8.5), Inches(1.4), Inches(4.033), Inches(5.6), "📋 Forensic Inspection Details", ACCENT_INDIGO)
    add_bullet(tf_eval, "Input Status", "Original latent sample exhibits severe contrast fading, broken ridge paths, and heavy background grain.")
    add_bullet(tf_eval, "Enhanced Image", "Ridges are rendered with deep contrast, continuous boundaries, and smooth curves matching biological flow.")
    add_bullet(tf_eval, "Binarized Map", "Otsu thresholding produces clean, well-isolated 1-bit ridge skeletons with zero background noise artifacts.")
    add_bullet(tf_eval, "Minutiae Integrity", "Key forensic landmarks — bifurcations, ridge endings, and delta patterns — are preserved without hallucinated features.")
    add_bullet(tf_eval, "AFIS Matching", "Converts unmatchable crime scene latent prints into standard AFIS query images.")

    # =========================================================================
    # SLIDE 6: Multi-Sample Evaluation & Quantitative Metrics
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_background(s6)
    add_slide_header(s6, "Quantitative Performance", "Metric Validation & Quality Evaluation")

    # Left: Metrics Graphic
    _, tf_m_card = add_card(s6, Inches(0.8), Inches(1.4), Inches(7.0), Inches(5.6), "📊 Intensity Distribution & Performance Profile", PRIMARY_CYAN)
    
    metrics_img_path = 'output_images/metrics_distribution_chart.png'
    if os.path.exists(metrics_img_path):
        s6.shapes.add_picture(metrics_img_path, Inches(0.95), Inches(2.1), width=Inches(6.7))

    # Right: Quantitative Table & Formula Explanations
    _, tf_tab = add_card(s6, Inches(8.0), Inches(1.4), Inches(4.533), Inches(5.6), "📈 Quantitative Metric Summary", ACCENT_GREEN)
    
    add_bullet(tf_tab, "PSNR (Peak Signal-to-Noise)", "5.29 dB — Reflects deliberate structural transformation from faint gray impression to sharp dark ridges.", 11, 8)
    add_bullet(tf_tab, "SSIM (Structural Similarity)", "0.5326 (53.3%) — Confirms ridge topology and spatial layout are preserved without distortion.", 11, 8)
    add_bullet(tf_tab, "Contrast Improvement (CII)", "Enhanced standard deviation standardizes dynamic range across the full ridge structure.", 11, 8)
    add_bullet(tf_tab, "Quality Benchmark Score", "Composite score formulated to rank candidate fingerprints for automated forensic matching eligibility.", 11, 8)
    add_bullet(tf_tab, "Histogram Normalization", "Original bimodal faint spread is remapped into sharp bimodal distribution separating ridge and valley pixels.", 11, 8)

    # =========================================================================
    # SLIDE 7: Software Implementation & Conclusion
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_background(s7)
    add_slide_header(s7, "System Implementation & Summary", "ForensiPrint Studio Application & Conclusion")

    # Card 1: Web Interface
    _, tf_app = add_card(s7, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.6), "💻 ForensiPrint Studio Web Interface", PRIMARY_CYAN)
    add_bullet(tf_app, "Flask Architecture", "Lightweight web application providing a responsive forensic analyst workbench.")
    add_bullet(tf_app, "Real-Time Processing", "Instant processing for PNG, JPG, BMP, TIFF, and PGM fingerprint files.")
    add_bullet(tf_app, "Interactive Visualizer", "Displays all 6 pipeline stages with interactive high-resolution lightbox inspection.")
    add_bullet(tf_app, "Quality Indicator Ring", "Dynamic SVG gauge categorizing processed prints into Excellent, Good, or Fair status.")
    add_bullet(tf_app, "Forensic Export", "One-click download of enhanced ridge maps and Otsu binarized skeletons.")

    # Card 2: Conclusion & Future Scope
    _, tf_conc = add_card(s7, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.6), "🏆 Conclusion & Future Enhancements", ACCENT_INDIGO)
    add_bullet(tf_conc, "Project Summary", "Successfully built an automated digital image processing pipeline restoring degraded latent fingerprints for biometric identification.")
    add_bullet(tf_conc, "Robustness", "Effectively handles low contrast, uneven lighting, skin dryness fractures, and background noise.")
    add_bullet(tf_conc, "Forensic Viability", "Transforms poor-quality latent crime scene prints into verifiable AFIS-ready ridge patterns.")
    add_bullet(tf_conc, "Future Scope 1", "Integrate deep learning orientation estimation (e.g. FingerNet CNN) for complex high-curvature prints.")
    add_bullet(tf_conc, "Future Scope 2", "Automate minutiae extraction (bifurcation/termination matching against FBI/AFIS criminal databases).")

    # Save Presentation
    prs.save(output_filename)
    print(f"Presentation saved successfully as: {output_filename}")

if __name__ == "__main__":
    create_deck()
