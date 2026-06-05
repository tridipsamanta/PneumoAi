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
