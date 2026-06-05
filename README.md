<!--
PneumoAI Project Report

The full project report PDF is included in this repository as
`PneumoAI_Project_Report.pdf` and can be opened directly on GitHub.

If your browser supports embedding, the PDF will appear below. If embedding
is not allowed by the viewer, click the link to open the PDF in a new tab.

-->

# PneumoAI — Project Report

**View the full PDF report (opens below if supported):**

<p>
<a href="https://github.com/tridipsamanta/PneumoAi/blob/main/PneumoAI_Project_Report.pdf">Open PDF on GitHub</a>
</p>

<!-- Attempt to embed via raw GitHub content. Note: GitHub sanitizes some HTML
         so inline embedding may be blocked; if so, use the link above. -->

<iframe src="https://raw.githubusercontent.com/tridipsamanta/PneumoAi/main/PneumoAI_Project_Report.pdf" width="100%" height="800px">
    Your browser does not support iframes — open the PDF directly: <a href="https://github.com/tridipsamanta/PneumoAi/blob/main/PneumoAI_Project_Report.pdf">PneumoAI_Project_Report.pdf</a>
</iframe>

---

# PneumoAI — Deep Learning Based Pneumonia Detection

A complete research-and-deployment project that detects pneumonia from chest X-ray images using a custom Convolutional Neural Network (CNN). This repository contains the model, training and evaluation scripts, a Streamlit web application for inference, and a professional project report PDF.

Preview the full project report (PDF):

[PneumoAI Project Report](PneumoAI_Project_Report.pdf)

If your browser supports it, GitHub will open the PDF inline. Otherwise click the link above to download or view.

## Table of Contents
- Overview
- Key Features
- Results Summary
- Repository Structure
- Setup & Installation
- Usage
- Model Details
- Dataset
- Evaluation
- Contributing
- License & Contact

## Overview

PneumoAI is an academic project (BCA Final Year) that demonstrates a production-like pipeline for automated pneumonia screening from chest X-ray images. The repository includes training, evaluation, Grad-CAM explainability, automated PDF report generation, and a Streamlit web UI for real-time inference.

## Key Features

- Custom CNN trained from scratch (~14.7M parameters)
- Data augmentation and a complete training pipeline with checkpoints and early stopping
- Grad-CAM visual explanations for each prediction
- Streamlit-based web application with animated scanning UI
- Downloadable, printable PDF diagnostic reports (ReportLab)
- Batch processing with CSV export

## Results Summary

- Validation Accuracy: 93.75%
- Recall (Sensitivity): 95.1%
- AUC-ROC: 0.962
- Model parameters: ~14.7M

These metrics were obtained on the Kaggle Chest X-ray dataset (Kermany et al., 2018). See the full PDF report for detailed tables, plots, and analysis.

## Repository Structure

See Appendix A in the report for the complete file listing. Key files and directories:

- `app.py` — Streamlit web application for inference and reporting
- `train.py` — Training pipeline (data generators, augmentation, callbacks)
- `evaluate.py` — Evaluation scripts and metric computation
- `predict.py` — CLI helper for single-image prediction
- `model/` — Saved models (`best_model.h5`, `final_model.h5`)
- `dataset/` — Expected location for Chest X-ray data (not included)
- `logs/` — Training logs and plots
- `PneumoAI_Project_Report.pdf` — Full project report (formal documentation)
- `requirements.txt` — Python dependencies

## Setup & Installation

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Place the Kaggle Chest X-ray dataset under `dataset/chest_xray/` following the structure used in the project. Do NOT commit large dataset files to the repo.

## Usage

Train the model:

```bash
python train.py
```

Evaluate on the test set:

```bash
python evaluate.py
```

Run a single prediction (CLI):

```bash
python predict.py --image dataset/chest_xray/test/PNEUMONIA/person1_virus_6.jpeg
```

Launch the Streamlit app (web UI):

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser to use the app locally.

## Model Details

- Architecture: 4 convolutional blocks (32 → 256 filters), BatchNorm, MaxPool, Dense(512), Dropout(0.5), Dense(1, sigmoid)
- Input size: 224×224 RGB
- Loss: Binary Cross-Entropy
- Optimizer: Adam (lr=1e-4)
- Best model saved as `model/best_model.h5` (Epoch 6)

## Dataset

This project uses the Kaggle Chest X-ray Images (Pneumonia) dataset (Kermany et al., 2018). Expected split in this repo:

- `dataset/chest_xray/train/` — training images
- `dataset/chest_xray/val/` — validation images
- `dataset/chest_xray/test/` — test images

Do not include the dataset in the repository. Add it locally at the path above or configure `train.py` accordingly.

## Evaluation & Metrics

Evaluation scripts compute Accuracy, Precision, Recall, F1-Score, Specificity, and AUC-ROC. Confusion matrix and ROC plots are saved under `logs/` by default.

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository
2. Create a feature branch
3. Open a pull request with a clear description and tests where applicable

Please do not commit large binary datasets or model checkpoints to this repository. Use Git LFS or external storage when sharing large files.

## License & Contact

This project is provided for educational and research purposes. If you wish to reuse or redistribute, please include appropriate citations to the original authors and the dataset (Kermany et al., 2018).

For questions contact the project authors (see `project_report.py` cover page for team and supervisor details).

---

<!-- Original report generator script follows below (kept for traceability). -->

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Flowable
)
import datetime

W4, H4 = A4
LM = RM = 25*mm
TM = BM = 20*mm
CW = W4 - LM - RM   # content width

# ── Palette ────────────────────────────────────────────────────
WHITE   = colors.white
BLACK   = colors.HexColor("#0d0d0d")
INK     = colors.HexColor("#1a1a2e")
GRAY    = colors.HexColor("#4a4a4a")
LGRAY   = colors.HexColor("#888888")
BORDER  = colors.HexColor("#d0d0d0")
NAVY    = colors.HexColor("#1a3a6b")
BLUE    = colors.HexColor("#1e5ba8")
LBLUE   = colors.HexColor("#e8f0fb")
CYAN    = colors.HexColor("#0077b6")
GREEN   = colors.HexColor("#1a7a4a")
LGREEN  = colors.HexColor("#e8f5ee")
RED     = colors.HexColor("#b91c1c")
LRED    = colors.HexColor("#fef2f2")
GOLD    = colors.HexColor("#b45309")
LGOLD   = colors.HexColor("#fffbeb")
ACCENT  = colors.HexColor("#e8f0fb")
DARK    = colors.HexColor("#0f172a")

# ── Custom Flowables ────────────────────────────────────────────
class VRule(Flowable):
    def __init__(self, w, h, c=BORDER):
        self.w, self.h, self.c = w, h, c
    def draw(self):
        self.canv.setFillColor(self.c)
        self.canv.rect(0, 0, self.w, self.h, fill=1, stroke=0)
    def wrap(self, *a): return self.w, self.h

class HRule(Flowable):
    def __init__(self, w, h=1, c=BORDER):
        self.w, self.h, self.c = w, h, c
    def draw(self):
        self.canv.setFillColor(self.c)
        self.canv.rect(0, 0, self.w, self.h, fill=1, stroke=0)
    def wrap(self, *a): return self.w, self.h

# ── Page Events ─────────────────────────────────────────────────
class PageEvents:
    def __init__(self):
        self.chapter = ""

    def on_cover(self, canvas, doc):
        W, H = W4, H4
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        # Deep navy top band
        canvas.setFillColor(NAVY)
        canvas.rect(0, H - 82, W, 82, fill=1, stroke=0)
        # Thin gold rule under navy
        canvas.setFillColor(GOLD)
        canvas.rect(0, H - 84, W, 2, fill=1, stroke=0)
        # Bottom band
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, W, 50, fill=1, stroke=0)
        canvas.setFillColor(GOLD)
        canvas.rect(0, 50, W, 2, fill=1, stroke=0)
        # Left accent bar
        canvas.setFillColor(BLUE)
        canvas.rect(0, 52, 6, H - 136, fill=1, stroke=0)

    def on_page(self, canvas, doc):
        W, H = W4, H4
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        # Top rule
        canvas.setFillColor(NAVY)
        canvas.rect(LM, H - 16*mm, CW, 0.8, fill=1, stroke=0)
        # Header text
        canvas.setFillColor(LGRAY)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(LM, H - 14*mm,
            "PneumoAI — Deep Learning Based Pneumonia Detection")
        canvas.drawRightString(LM + CW, H - 14*mm,
            f"Page {doc.page}")
        # Bottom rule
        canvas.setFillColor(NAVY)
        canvas.rect(LM, 14*mm, CW, 0.8, fill=1, stroke=0)
        canvas.setFillColor(LGRAY)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(LM, 10*mm,
            "BCA Final Year Project  ·  Midnapore College, Dept. of Computer Application  ·  2025–26")
        canvas.drawRightString(LM + CW, 10*mm, "EduMath")

PE = PageEvents()

# ── Style Factory ───────────────────────────────────────────────
def S(name, **kw): return ParagraphStyle(name, **kw)

ss = {
# Cover
"cov_tag":   S("ct", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#aac4ff"),
               alignment=TA_CENTER, letterSpacing=2, spaceAfter=6),
"cov_title": S("cv", fontName="Helvetica-Bold", fontSize=26, textColor=WHITE,
               alignment=TA_CENTER, leading=32, spaceAfter=4),
"cov_sub":   S("cs", fontName="Helvetica", fontSize=12, textColor=colors.HexColor("#c0d4ff"),
               alignment=TA_CENTER, leading=18, spaceAfter=4),
"cov_meta":  S("cm", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#8899cc"),
               alignment=TA_CENTER, spaceAfter=3),
"cov_body":  S("cb", fontName="Helvetica", fontSize=10, textColor=GRAY,
               alignment=TA_JUSTIFY, leading=16, spaceAfter=6),
# Additional cover styles
"cov_college": S("cov_college", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY,
                  alignment=TA_CENTER, spaceAfter=2),
"cov_aff":     S("cov_aff", fontName="Helvetica", fontSize=9, textColor=GRAY,
                  alignment=TA_CENTER, spaceAfter=2),
"cov_dept":    S("cov_dept", fontName="Helvetica", fontSize=10, textColor=BLUE,
                  alignment=TA_CENTER, spaceAfter=6),
"cov_report":  S("cov_report", fontName="Helvetica-Bold", fontSize=11, textColor=GOLD,
                  alignment=TA_CENTER, spaceAfter=4),
"cov_subtitle":S("cov_subtitle", fontName="Helvetica", fontSize=12, textColor=WHITE,
                  alignment=TA_CENTER, leading=16, spaceAfter=6),
"cov_footer":  S("cov_footer", fontName="Helvetica", fontSize=10, textColor=GRAY,
                  alignment=TA_CENTER, leading=14, spaceAfter=6),
"cov_year":    S("cov_year", fontName="Helvetica-Bold", fontSize=10, textColor=NAVY,
                  alignment=TA_CENTER, spaceAfter=2),
# Certificates
"cert_h":    S("ch2", fontName="Helvetica-Bold", fontSize=16, textColor=NAVY,
               alignment=TA_CENTER, spaceAfter=10, leading=22),
"cert_b":    S("cb2", fontName="Helvetica", fontSize=10.5, textColor=GRAY,
               alignment=TA_CENTER, leading=17, spaceAfter=8),
"sig_name":  S("sn", fontName="Helvetica-Bold", fontSize=10.5, textColor=BLACK),
"sig_role":  S("sr", fontName="Helvetica", fontSize=9, textColor=LGRAY),
# Chapter headers
"ch_num":    S("cn", fontName="Helvetica-Bold", fontSize=9, textColor=BLUE,
               letterSpacing=1.5, spaceAfter=2),
"ch_title":  S("cth", fontName="Helvetica-Bold", fontSize=20, textColor=NAVY,
               leading=26, spaceAfter=4),
"ch_rule":   S("cr", fontName="Helvetica", fontSize=1, spaceAfter=2),
# Section
"sec_h":     S("sh", fontName="Helvetica-Bold", fontSize=13, textColor=NAVY,
               spaceBefore=10, spaceAfter=4, leading=17),
"sec_h2":    S("sh2", fontName="Helvetica-Bold", fontSize=11, textColor=BLUE,
               spaceBefore=6, spaceAfter=3, leading=15),
# Body
"body":      S("bd", fontName="Helvetica", fontSize=10, textColor=GRAY,
               leading=16, spaceAfter=6, alignment=TA_JUSTIFY),
"body_b":    S("bdb", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK,
               leading=16, spaceAfter=4),
"bullet":    S("bl", fontName="Helvetica", fontSize=10, textColor=GRAY,
               leading=15, spaceAfter=3, leftIndent=14, bulletIndent=0),
"bullet2":   S("bl2", fontName="Helvetica`,
}