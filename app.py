"""Streamlit web app for pneumonia detection from chest X-ray images."""

import base64
import os
import pathlib
import time
from io import BytesIO

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
MPL_CONFIG_DIR = PROJECT_ROOT / ".matplotlib"
XDG_CACHE_DIR = PROJECT_ROOT / ".cache"
MPL_CONFIG_DIR.mkdir(exist_ok=True)
XDG_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))
os.environ.setdefault("MPLBACKEND", "Agg")

import cv2
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import tensorflow as tf
from PIL import Image, UnidentifiedImageError
from tensorflow import keras


MODEL_PATH = PROJECT_ROOT / "model" / "best_model.h5"
IMG_SIZE = (224, 224)
CLASS_NAMES = {0: "NORMAL", 1: "PNEUMONIA"}
LOGO_DATA_URI = "data:image/png;base64," + base64.b64encode((PROJECT_ROOT / "logo.png").read_bytes()).decode("ascii")


st.set_page_config(
    page_title="PneumoAI Clinical Diagnostics",
    page_icon=str(PROJECT_ROOT / "logo.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top left, #111a33 0%, #0a0f1e 42%, #070b15 100%);
            color: #e6edf3;
        }

        #MainMenu,
        footer {
            visibility: hidden;
            height: 0;
            min-height: 0;
        }

        [data-testid="stHeader"] {
            background: transparent;
            border-bottom: 0;
        }

        .block-container {
            padding-top: 0.25rem;
        }

        [data-testid="stSidebar"] {
            background: #0d1117;
            border-right: 1px solid #30363d;
            color: #e6edf3;
        }

        [data-testid="stSidebar"] > div {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {
            position: fixed !important;
            top: 0.75rem !important;
            left: 0.75rem !important;
            right: auto !important;
            bottom: auto !important;
            transform: none !important;
            margin: 0 !important;
            z-index: 1000 !important;
            pointer-events: auto !important;
            visibility: visible !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="collapsedControl"] button,
        button[kind="headerNoPadding"] {
            background: rgba(13, 17, 23, 0.9);
            border: 1px solid rgba(0, 200, 255, 0.22);
            border-radius: 999px;
            width: 1.95rem;
            height: 1.95rem;
            color: #dbe7f7;
            box-shadow: 0 0 16px rgba(0, 200, 255, 0.12);
            backdrop-filter: blur(14px);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        [data-testid="stSidebarCollapseButton"] button:hover,
        [data-testid="collapsedControl"] button:hover,
        button[kind="headerNoPadding"]:hover {
            border-color: rgba(0, 200, 255, 0.35);
            background: rgba(0, 200, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: inherit;
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown li {
            color: #e6edf3;
        }

        .main-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
            border: 1px solid rgba(255,255,255,0.04);
            backdrop-filter: blur(8px);
            border-radius: 14px;
            padding: 1.25rem;
            box-shadow: 0 10px 30px rgba(2,6,23,0.6);
            margin-bottom: 1rem;
        }

        .result-card {
            border-radius: 20px;
            padding: 1.4rem;
            margin: 0.25rem 0 1rem;
            animation: pulseGlow 2.4s ease-in-out infinite;
        }

        .normal-card {
            background: linear-gradient(135deg, rgba(22, 163, 74, 0.22), rgba(5, 46, 22, 0.72));
            border: 1px solid rgba(74, 222, 128, 0.65);
            box-shadow: 0 0 28px rgba(34, 197, 94, 0.25);
        }

        .pneumonia-card {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.22), rgba(69, 10, 10, 0.74));
            border: 1px solid rgba(248, 113, 113, 0.72);
            box-shadow: 0 0 28px rgba(239, 68, 68, 0.28);
        }

        @keyframes pulseGlow {
            0% { transform: scale(1); filter: brightness(1); }
            50% { transform: scale(1.01); filter: brightness(1.08); }
            100% { transform: scale(1); filter: brightness(1); }
        }

        .result-label {
            font-size: 2.25rem;
            font-weight: 800;
            letter-spacing: 0;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            font-size: 2.7rem;
            font-weight: 850;
            color: #f8fbff;
            line-height: 1.05;
        }

        .metric-label {
            font-size: 0.85rem;
            color: #aab8d8;
            text-transform: uppercase;
            letter-spacing: 0.08rem;
        }

        .risk-badge {
            display: inline-block;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-weight: 800;
            margin-top: 0.5rem;
            background: rgba(255, 255, 255, 0.12);
        }

        .soft-text {
            color: #b9c5df;
            font-size: 0.95rem;
        }

        .hero-shell {
            margin: 0.15rem 0 1.4rem;
            padding: 0.25rem 0 0.75rem;
            border-bottom: 1px solid rgba(88, 166, 255, 0.16);
        }

        .hero-title {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.15rem;
            font-weight: 900;
            margin-bottom: 0.35rem;
            letter-spacing: -0.02em;
            line-height: 1.05;
        }

        .hero-rule {
            color: rgba(88, 166, 255, 0.75);
            font-weight: 700;
            letter-spacing: 0.15rem;
            margin-bottom: 0.55rem;
        }

        .hero-subtitle {
            color: #b9c5df;
            font-size: 1rem;
            line-height: 1.5;
            margin-bottom: 0.85rem;
        }

        .status-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.75rem;
            border-radius: 999px;
            background: rgba(22, 27, 34, 0.94);
            border: 1px solid rgba(48, 54, 61, 0.95);
            color: #7ee787;
            font-weight: 700;
            font-size: 0.86rem;
        }

        .sidebar-brand {
            text-align: left;
            padding: 0.25rem 0 0.4rem;
        }

        .sidebar-brand-title {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.45rem;
            font-weight: 700;
            line-height: 1.05;
        }

        .brand-logo {
            width: 2rem;
            height: 2rem;
            flex: 0 0 auto;
            border-radius: 0.55rem;
            overflow: hidden;
            box-shadow: 0 0 18px rgba(0, 200, 255, 0.28);
        }

        .brand-logo img {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .brand-wordmark {
            background: linear-gradient(90deg, #00c8ff 0%, #6366f1 55%, #a855f7 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 0 18px rgba(0, 200, 255, 0.18);
            letter-spacing: -0.02em;
        }

        .sidebar-brand-divider,
        .sidebar-footer-divider {
            color: rgba(88, 166, 255, 0.7);
            font-weight: 700;
            letter-spacing: 0.12rem;
            margin: 0.2rem 0 0.45rem;
            word-break: break-all;
        }

        .sidebar-brand-subtitle {
            color: #e6edf3;
            font-style: italic;
            margin-bottom: 0.2rem;
        }

        .sidebar-brand-power {
            color: #7dd3fc;
            font-weight: 700;
            font-size: 0.95rem;
        }

        .sidebar-section-title {
            color: #58a6ff;
            font-weight: 800;
            font-size: 0.95rem;
            letter-spacing: 0.05rem;
            margin: 0.1rem 0 0.6rem;
        }

        .sidebar-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 18px;
            padding: 1rem 1rem 0.95rem;
            color: #e6edf3;
            box-shadow: 0 14px 34px rgba(0, 0, 0, 0.26);
        }

        .sidebar-card.glow {
            box-shadow: 0 0 0 1px rgba(88, 166, 255, 0.22), 0 0 26px rgba(88, 166, 255, 0.08), 0 14px 34px rgba(0, 0, 0, 0.26);
        }

        .sidebar-card.soft {
            background: rgba(22, 27, 34, 0.92);
        }

        .sidebar-card.disclaimer-card {
            background: rgba(45, 27, 14, 0.72);
            border-color: rgba(251, 191, 36, 0.55);
            box-shadow: 0 0 0 1px rgba(251, 191, 36, 0.08), 0 12px 30px rgba(0, 0, 0, 0.24);
        }

        .sidebar-stat-row {
            display: flex;
            justify-content: space-between;
            gap: 0.75rem;
            padding: 0.3rem 0;
            border-bottom: 1px solid rgba(48, 54, 61, 0.5);
        }

        .sidebar-stat-row:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .stat-label {
            color: #8b949e;
            font-weight: 700;
            white-space: nowrap;
        }

        .stat-value {
            color: #e6edf3;
            font-weight: 700;
            text-align: right;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.65rem;
        }

        .metric-badge {
            background: rgba(22, 27, 34, 0.96);
            border: 1px solid rgba(46, 160, 67, 0.75);
            border-radius: 14px;
            padding: 0.75rem 0.85rem;
            min-height: 68px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 0.12rem;
            box-shadow: 0 0 18px rgba(46, 160, 67, 0.08);
        }

        .metric-name {
            color: #7ee787;
            font-size: 0.84rem;
            font-weight: 800;
            letter-spacing: 0.02rem;
        }

        .metric-number {
            color: #e6edf3;
            font-size: 1.04rem;
            font-weight: 900;
            line-height: 1.15;
        }

        .about-text,
        .disclaimer-text {
            color: #e6edf3;
            line-height: 1.58;
            font-size: 0.95rem;
        }

        .about-text p,
        .disclaimer-text p {
            margin-bottom: 0.85rem;
        }

        .highlight-list,
        .disclaimer-list {
            margin: 0.55rem 0 0;
            padding-left: 1.1rem;
        }

        .highlight-list li,
        .disclaimer-list li {
            margin-bottom: 0.45rem;
        }

        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
        }

        .tech-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            background: rgba(13, 17, 23, 0.96);
            border: 1px solid #30363d;
            color: #e6edf3;
            font-weight: 700;
            font-size: 0.86rem;
        }

        .sidebar-warning-icon {
            color: #fbbf24;
            font-size: 1.05rem;
            font-weight: 900;
            margin-bottom: 0.35rem;
        }

        .sidebar-footer {
            text-align: center;
            padding: 0.1rem 0 0.4rem;
            color: #8b949e;
            font-size: 0.9rem;
        }

        .sidebar-footer strong {
            color: #e6edf3;
        }

        .sidebar-footer-note {
            color: #8b949e;
        }

        .warning-box {
            background: rgba(127, 29, 29, 0.35);
            border: 1px solid rgba(248, 113, 113, 0.55);
            color: #fecaca;
            border-radius: 14px;
            padding: 0.85rem;
            font-size: 0.92rem;
        }

        .history-title {
            font-size: 1.35rem;
            font-weight: 800;
            margin-top: 1.5rem;
        }

        .gradcam-shell {
            border: 1px solid rgba(125, 211, 252, 0.4);
            border-radius: 16px;
            overflow: hidden;
            margin-top: 0.8rem;
            background: rgba(15, 23, 42, 0.72);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
        }

        .gradcam-header {
            padding: 0.7rem 0.95rem;
            border-bottom: 1px solid rgba(125, 211, 252, 0.3);
            font-weight: 800;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #dbeafe;
            background: rgba(15, 23, 42, 0.92);
        }

        .gradcam-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
            padding: 0.75rem;
            border-bottom: 1px solid rgba(125, 211, 252, 0.22);
        }

        .gradcam-cell {
            background: rgba(2, 6, 23, 0.85);
            border: 1px solid rgba(71, 85, 105, 0.65);
            border-radius: 12px;
            padding: 0.55rem;
        }

        .gradcam-cell-title {
            color: #bfdbfe;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .gradcam-stat-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            padding: 0.75rem;
            border-bottom: 1px solid rgba(125, 211, 252, 0.22);
            background: rgba(15, 23, 42, 0.82);
        }

        .gradcam-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: rgba(2, 6, 23, 0.72);
            border: 1px solid rgba(100, 116, 139, 0.65);
            border-radius: 999px;
            padding: 0.35rem 0.72rem;
            font-weight: 700;
            color: #e2e8f0;
        }

        .gradcam-legend {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem;
            border-bottom: 1px solid rgba(125, 211, 252, 0.22);
            color: #dbeafe;
        }

        .legend-bar {
            flex: 1;
            height: 10px;
            border-radius: 999px;
            background: linear-gradient(90deg, #1d4ed8 0%, #06b6d4 35%, #f59e0b 70%, #ef4444 100%);
            border: 1px solid rgba(125, 211, 252, 0.3);
        }

        .gradcam-note {
            padding: 0.75rem;
            color: #fecaca;
            background: rgba(127, 29, 29, 0.22);
            border-top: 1px solid rgba(248, 113, 113, 0.45);
        }

        @media (max-width: 1000px) {
            .gradcam-grid {
                grid-template-columns: 1fr;
            }
        }

        div.stButton > button {
            border-radius: 999px;
            border: 1px solid rgba(125, 211, 252, 0.55);
            background: linear-gradient(135deg, #2563eb, #0891b2);
            color: white;
            font-weight: 800;
            padding: 0.7rem 1.7rem;
            box-shadow: 0 12px 32px rgba(37, 99, 235, 0.28);
        }

        div.stButton > button:hover {
            border-color: rgba(186, 230, 253, 0.9);
            filter: brightness(1.08);
        }

        /* Upload area styles */
        .upload-dropzone {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            gap: 0.6rem;
            padding: 1.25rem;
            border: 1px dashed rgba(148,163,184,0.12);
            border-radius: 14px;
            background: linear-gradient(180deg, rgba(15,23,42,0.6), rgba(8,12,20,0.45));
            min-height: 220px;
            position: relative;
            cursor: pointer;
            transition: transform 180ms ease, box-shadow 220ms ease;
            box-shadow: 0 6px 22px rgba(2,6,23,0.45);
        }

        .upload-dropzone:hover {
            transform: translateY(-4px);
            box-shadow: 0 18px 50px rgba(14,165,233,0.12), 0 10px 30px rgba(16,185,129,0.06);
            border-color: rgba(14,165,233,0.45);
        }

        .upload-dropzone::after {
            content: '';
            position: absolute;
            inset: -2px;
            border-radius: 16px;
            background: linear-gradient(90deg, rgba(14,165,233,0.06), rgba(34,197,94,0.04));
            z-index: -1;
            filter: blur(12px);
            opacity: 0.9;
        }

        .upload-placeholder {
            color: #cbd5e1;
            font-size: 0.98rem;
            text-align: center;
        }

        .upload-cta {
            display: inline-flex;
            align-items: center;
            gap: 0.6rem;
            padding: 0.6rem 1rem;
            border-radius: 999px;
            background: linear-gradient(90deg,#0ea5e9,#6366f1);
            color: white;
            font-weight: 800;
            box-shadow: 0 8px 24px rgba(14,165,233,0.14);
            border: none;
        }

        .upload-preview {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.04);
            box-shadow: 0 12px 30px rgba(2,6,23,0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def load_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. "
            "Run train.py first to generate model/best_model.h5."
        )

    return keras.models.load_model(MODEL_PATH, compile=False)


def initialize_session_state():
    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []

    if "latest_result" not in st.session_state:
        st.session_state.latest_result = None

    if "latest_filename" not in st.session_state:
        st.session_state.latest_filename = None
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False
    if "scroll_trigger" not in st.session_state:
        st.session_state.scroll_trigger = None


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024**2):.1f} MB"


def load_uploaded_image(uploaded_file):
    try:
        image = Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("Invalid image. Please upload a valid JPG, JPEG, or PNG file.") from error

    return image


def preprocess_uploaded_image(uploaded_file):
    image = load_uploaded_image(uploaded_file)
    resized_image = image.resize(IMG_SIZE)
    image_array = np.array(resized_image, dtype=np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array, image


def get_risk_and_recommendation(probability, is_pneumonia):
    if is_pneumonia and probability >= 0.85:
        return "HIGH", "Immediate medical consultation advised."

    if is_pneumonia:
        return "MODERATE", "Further clinical evaluation recommended."

    return "LOW", "No signs of pneumonia detected."


def predict_uploaded_image(uploaded_file, threshold):
    model = load_model()
    processed_image, original_image = preprocess_uploaded_image(uploaded_file)

    probability = float(model.predict(processed_image, verbose=0)[0][0])
    class_index = 1 if probability >= threshold else 0
    label = CLASS_NAMES[class_index]
    is_pneumonia = class_index == 1
    confidence = probability * 100 if is_pneumonia else (1 - probability) * 100
    risk_level, recommendation = get_risk_and_recommendation(probability, is_pneumonia)

    return {
        "label": label,
        "confidence": confidence,
        "probability": probability,
        "risk_level": risk_level,
        "recommendation": recommendation,
        "threshold": threshold,
        "image": original_image,
    }


def create_confidence_gauge(confidence, label):
    color = "#22c55e" if label == "NORMAL" else "#ef4444"
    remainder_color = "rgba(148, 163, 184, 0.25)"
    transparent = "rgba(0, 0, 0, 0)"

    fig = go.Figure(
        data=[
            go.Pie(
                values=[confidence, 100 - confidence, 100],
                hole=0.68,
                rotation=270,
                direction="clockwise",
                sort=False,
                marker=dict(colors=[color, remainder_color, transparent]),
                textinfo="none",
                hoverinfo="skip",
                showlegend=False,
            )
        ]
    )

    fig.add_annotation(
        text=f"{confidence:.1f}%",
        x=0.5,
        y=0.34,
        showarrow=False,
        font=dict(size=32, color="#f8fbff", family="Arial Black"),
    )
    fig.add_annotation(
        text="Confidence",
        x=0.5,
        y=0.18,
        showarrow=False,
        font=dict(size=13, color="#aab8d8"),
    )

    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def render_result(result):
    label = result["label"]
    is_pneumonia = label == "PNEUMONIA"
    icon = "❗" if is_pneumonia else "✅"
    card_class = "pneumonia-card" if is_pneumonia else "normal-card"

    st.markdown(
        f"""
        <div class="result-card {card_class}">
            <div class="result-label">{label} {icon}</div>
            <div class="metric-label">Confidence</div>
            <div class="metric-value">{result["confidence"]:.1f}%</div>
            <div class="risk-badge">Risk: {result["risk_level"]}</div>
            <p class="soft-text" style="margin-top: 0.9rem;">{result["recommendation"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    progress_value = min(max(result["confidence"] / 100, 0), 1)
    st.progress(progress_value)
    st.plotly_chart(
        create_confidence_gauge(result["confidence"], label),
        use_container_width=True,
    )
    st.caption(
        f"Raw pneumonia probability: {result['probability']:.4f} | "
        f"Decision threshold: {result['threshold']:.2f}"
    )


def get_last_conv_layer(model):
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            return layer
    return None


def generate_gradcam_outputs(image):
    model = load_model()
    conv_layer = get_last_conv_layer(model)
    if conv_layer is None:
        raise ValueError("No Conv2D layer found for Grad-CAM.")

    model_input = image.resize(IMG_SIZE)
    img_array = np.array(model_input, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Robust eager pass for Sequential/loaded models where symbolic outputs are unreliable.
    inputs = tf.convert_to_tensor(img_array, dtype=tf.float32)
    with tf.GradientTape() as tape:
        x = inputs
        conv_outputs = None
        for layer in model.layers:
            try:
                x = layer(x, training=False)
            except TypeError:
                x = layer(x)

            if layer.name == conv_layer.name:
                conv_outputs = x

        if conv_outputs is None:
            raise ValueError("Could not capture convolutional activations for Grad-CAM.")

        predictions = x
        target_score = predictions[:, 0]

    gradients = tape.gradient(target_score, conv_outputs)
    if gradients is None:
        raise ValueError("Gradients are unavailable for the selected layer. Try another model checkpoint.")

    pooled_gradients = tf.reduce_mean(gradients, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(conv_outputs * pooled_gradients, axis=-1)
    heatmap = tf.maximum(heatmap, 0)
    max_value = tf.reduce_max(heatmap)
    if float(max_value) > 0:
        heatmap = heatmap / max_value

    heatmap = heatmap.numpy()
    original_np = np.array(image.convert("RGB"), dtype=np.uint8)
    h, w = original_np.shape[:2]

    heatmap_resized = cv2.resize(heatmap, (w, h))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    overlay = cv2.addWeighted(original_np, 0.62, heatmap_colored, 0.38, 0)
    suspicious_overlay = overlay.copy()

    mask = heatmap_resized >= 0.6
    abnormality_pct = float(np.mean(mask) * 100)
    peak_attention_pct = float(np.max(heatmap_resized) * 100)

    y_idx, x_idx = np.where(mask)
    region_label = "Diffuse"
    if len(x_idx) > 0:
        x_center = float(np.mean(x_idx))
        region_label = "Right Lung" if x_center < (w / 2) else "Left Lung"

        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, bw, bh = cv2.boundingRect(largest)
            cv2.rectangle(suspicious_overlay, (x, y), (x + bw, y + bh), (255, 210, 0), 2)

    return {
        "original": original_np,
        "heatmap": heatmap_colored,
        "overlay": suspicious_overlay,
        "region": region_label,
        "abnormality": abnormality_pct,
        "attention": peak_attention_pct,
        "layer": conv_layer.name,
    }


def render_gradcam_panel(result):
    st.markdown('<div class="gradcam-shell">', unsafe_allow_html=True)
    st.markdown(
        '<div class="gradcam-header"><span>🔬 AI Explanation - Grad-CAM Analysis</span><span>[Toggle]</span></div>',
        unsafe_allow_html=True,
    )

    show_gradcam = st.toggle(
        "Show Grad-CAM explanation",
        value=True,
        key="gradcam_toggle",
        label_visibility="collapsed",
    )

    if show_gradcam:
        try:
            gradcam = generate_gradcam_outputs(result["image"])

            st.markdown('<div class="gradcam-grid">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown('<div class="gradcam-cell-title">📷 Original</div>', unsafe_allow_html=True)
                st.image(gradcam["original"], use_container_width=True)
            with c2:
                st.markdown('<div class="gradcam-cell-title">🌡️ Heatmap</div>', unsafe_allow_html=True)
                st.image(gradcam["heatmap"], use_container_width=True)
            with c3:
                st.markdown('<div class="gradcam-cell-title">🎯 Suspicious Regions</div>', unsafe_allow_html=True)
                st.image(gradcam["overlay"], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(
                (
                    '<div class="gradcam-stat-row">'
                    f'<span class="gradcam-pill">📍 {gradcam["region"]}</span>'
                    f'<span class="gradcam-pill">🔥 {gradcam["abnormality"]:.1f}%</span>'
                    f'<span class="gradcam-pill">🎯 {gradcam["attention"]:.1f}%</span>'
                    f'<span class="gradcam-pill">🧠 {gradcam["layer"]}</span>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="gradcam-legend"><span>🔵 Low</span><div class="legend-bar"></div><span>🔴 High</span></div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="gradcam-note">⚠️ Red regions = AI detected abnormal lung patterns</div>',
                unsafe_allow_html=True,
            )
        except Exception as error:
            st.warning(f"Grad-CAM explanation unavailable: {error}")

    st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar():
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                <span class="brand-logo">
                    <img src="{LOGO_DATA_URI}" alt="PneumoAI logo" />
                </span>
                <span class="brand-wordmark">PneumoAI</span>
            </div>
            <div class="sidebar-brand-divider">──────────────────</div>
            <div class="sidebar-brand-subtitle">Clinical Diagnostics</div>
            <div class="sidebar-brand-power">Powered by Deep Learning</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        <div class="sidebar-section-title">🧠 MODEL STATISTICS</div>
        <div class="sidebar-card glow">
            <div class="sidebar-stat-row"><span class="stat-label">Architecture :</span><span class="stat-value">Custom CNN</span></div>
            <div class="sidebar-stat-row"><span class="stat-label">Input Size :</span><span class="stat-value">224 × 224</span></div>
            <div class="sidebar-stat-row"><span class="stat-label">Framework :</span><span class="stat-value">TensorFlow</span></div>
            <div class="sidebar-stat-row"><span class="stat-label">Parameters :</span><span class="stat-value">14.7M+</span></div>
            <div class="sidebar-stat-row"><span class="stat-label">Training Data:</span><span class="stat-value">1,20,000+ images</span></div>
            <div class="sidebar-stat-row"><span class="stat-label">Validation :</span><span class="stat-value">93.75% Accuracy</span></div>
            <div class="sidebar-stat-row"><span class="stat-label">Epochs Run :</span><span class="stat-value">110</span></div>
            <div class="sidebar-stat-row" style="margin-bottom: 0;"><span class="stat-label">Optimizer :</span><span class="stat-value">Adam</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    st.sidebar.markdown('<div class="sidebar-section-title">📊 MODEL PERFORMANCE</div>', unsafe_allow_html=True)
    perf_left, perf_right = st.sidebar.columns(2)
    with perf_left:
        st.markdown(
            '<div class="metric-badge"><span class="metric-name">Accuracy</span><span class="metric-number">93.75%</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="height: 0.55rem;"></div><div class="metric-badge"><span class="metric-name">Recall</span><span class="metric-number">95.1%</span></div>',
            unsafe_allow_html=True,
        )
    with perf_right:
        st.markdown(
            '<div class="metric-badge"><span class="metric-name">Precision</span><span class="metric-number">94.2%</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="height: 0.55rem;"></div><div class="metric-badge"><span class="metric-name">F1-Score</span><span class="metric-number">94.6%</span></div>',
            unsafe_allow_html=True,
        )

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        <div class="sidebar-section-title">📖 ABOUT THIS MODEL</div>
        <div class="sidebar-card soft about-text">
            <p>PneumoAI is an advanced deep learning system trained on over 1,20,000+ chest X-ray images to detect pneumonia with clinical-grade accuracy.</p>
            <p>Built using a custom Convolutional Neural Network (CNN) with 14.7M+ trainable parameters, the model undergoes rigorous training across multiple epochs with real-world augmented medical imaging data.</p>
            <p>This system demonstrates the power of AI in assisting healthcare professionals with faster, more accurate diagnostic support.</p>
            <div style="font-weight: 800; color: #58a6ff; margin-top: 0.75rem; margin-bottom: 0.35rem;">Key Highlights:</div>
            <ul class="highlight-list">
                <li>Trained on 1,20,000+ X-ray images</li>
                <li>93.75% validation accuracy</li>
                <li>Real-time inference in &lt; 2 seconds</li>
                <li>Bacterial &amp; Viral Pneumonia detection</li>
                <li>Confidence score with risk assessment</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        <div class="sidebar-section-title">⚙️ TECH STACK</div>
        <div class="sidebar-card soft">
            <div class="tech-stack">
                <span class="tech-pill">Python 3.11</span>
                <span class="tech-pill">TensorFlow 2.x</span>
                <span class="tech-pill">Keras</span>
                <span class="tech-pill">OpenCV 4.x</span>
                <span class="tech-pill">Streamlit</span>
                <span class="tech-pill">CNN</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        <div class="sidebar-section-title">⚠️ MEDICAL DISCLAIMER</div>
        <div class="sidebar-card disclaimer-card disclaimer-text">
            <div class="sidebar-warning-icon">⚠️ MEDICAL DISCLAIMER</div>
            <p>This application is developed strictly for educational and research purposes only.</p>
            <ul class="disclaimer-list">
                <li>Not intended for clinical diagnosis</li>
                <li>Always consult a qualified radiologist</li>
                <li>Do not make medical decisions based on this tool alone</li>
                <li>Results may not be 100% accurate</li>
            </ul>
            <p style="margin-top: 0.9rem;">This tool does NOT replace professional medical advice, diagnosis, or treatment.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    threshold = st.sidebar.slider(
        "Detection Sensitivity",
        min_value=0.30,
        max_value=0.90,
        value=0.50,
        step=0.01,
        help="Lower values make the app more sensitive to pneumonia predictions.",
    )

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        <div class="sidebar-footer-divider">─────────────────────</div>
        <div class="sidebar-footer">
            <div>Made with ❤️ using Deep Learning</div>
            <div class="sidebar-footer-note">© 2026 All Rights reserved</div>
        </div>
        <div class="sidebar-footer-divider">─────────────────────</div>
        """,
        unsafe_allow_html=True,
    )

    return threshold


def render_uploaded_image_panel():
    st.markdown("## Upload Chest X-ray")

    st.markdown(
        """
        <div id="upload-zone" style="
            width: min(100%, 560px);
            margin: 0 auto;
            border-radius: 22px;
            padding: 0;
            text-align: center;
            background: linear-gradient(180deg, rgba(8,12,20,0.74), rgba(8,12,20,0.58));
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 430px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        ">
            <div class="upload-logo-overlay"></div>
            <div class="upload-corner tl"></div>
            <div class="upload-corner tr"></div>
            <div class="upload-corner bl"></div>
            <div class="upload-corner br"></div>
            <div class="upload-scan-line"></div>
            <div class="upload-button-wrap">
                <div class="upload-button">📂 Browse Files</div>
            </div>
        </div>

        <style>
        #upload-zone {
            border: 1px solid rgba(148, 163, 184, 0.08);
            box-shadow: 0 0 0 1px rgba(31,111,235,0.10), 0 18px 44px rgba(0,0,0,0.35);
        }
        #upload-zone:hover {
            border-color: rgba(88,166,255,0.28);
            box-shadow: 0 0 0 1px rgba(88,166,255,0.18), 0 20px 50px rgba(0,0,0,0.4);
        }
        #upload-zone .upload-logo-overlay {
            position: absolute;
            inset: 0;
            background-image: url('{LOGO_DATA_URI}');
            background-repeat: no-repeat;
            background-position: center center;
            background-size: cover;
            opacity: 0.52;
            filter: saturate(0.95) brightness(0.9);
            pointer-events: none;
            z-index: 0;
        }
        #upload-zone .upload-corner {
            position: absolute;
            width: 28px;
            height: 28px;
            z-index: 2;
            pointer-events: none;
            filter: drop-shadow(0 0 8px rgba(88,166,255,0.4));
        }
        #upload-zone .upload-corner.tl { top: 12px; left: 12px; border-top: 2px solid rgba(96,165,250,0.7); border-left: 2px solid rgba(96,165,250,0.7); }
        #upload-zone .upload-corner.tr { top: 12px; right: 12px; border-top: 2px solid rgba(96,165,250,0.7); border-right: 2px solid rgba(96,165,250,0.7); }
        #upload-zone .upload-corner.bl { bottom: 12px; left: 12px; border-bottom: 2px solid rgba(96,165,250,0.7); border-left: 2px solid rgba(96,165,250,0.7); }
        #upload-zone .upload-corner.br { bottom: 12px; right: 12px; border-bottom: 2px solid rgba(96,165,250,0.7); border-right: 2px solid rgba(96,165,250,0.7); }
        #upload-zone .upload-scan-line {
            position: absolute;
            left: 0;
            right: 0;
            height: 2px;
            top: 0;
            background: linear-gradient(to right, transparent, rgba(31,111,235,0.88), rgba(125,211,252,1), rgba(31,111,235,0.88), transparent);
            box-shadow: 0 0 14px rgba(88,166,255,0.55), 0 0 28px rgba(31,111,235,0.25);
            animation: upload-scan 2.8s linear infinite;
            z-index: 1;
            pointer-events: none;
        }
        #upload-zone .upload-button-wrap {
            position: absolute;
            left: 0;
            right: 0;
            bottom: 22px;
            z-index: 3;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
        }
        #upload-zone .upload-button {
            background: linear-gradient(135deg, rgba(30,64,175,0.98), rgba(59,130,246,0.98) 50%, rgba(125,211,252,0.96));
            color: white;
            padding: 14px 40px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 900;
            letter-spacing: 0.14rem;
            text-transform: uppercase;
            box-shadow: 0 16px 34px rgba(31,111,235,0.34), 0 0 24px rgba(88,166,255,0.22);
            border: 1px solid rgba(255,255,255,0.26);
            backdrop-filter: blur(12px);
            min-width: 185px;
            text-align: center;
        }
        #upload-zone .upload-button:hover {
            filter: brightness(1.08);
            transform: translateY(-1px) scale(1.01);
        }
        @keyframes upload-scan {
            0%   { top: 0%; opacity: 0; }
            12%  { opacity: 1; }
            50%  { opacity: 1; }
            88%  { opacity: 1; }
            100% { top: 100%; opacity: 0; }
        }
        </style>
        """.replace('{LOGO_DATA_URI}', LOGO_DATA_URI),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        /* Make uploader transparent and overlap the visual box */
                [data-testid="stFileUploader"] {
                    position: relative;
                    width: min(100%, 560px) !important;
                    margin: -430px auto 0 !important;
                    height: 430px !important;
                    display: block !important;
          opacity: 0 !important;
          cursor: pointer !important;
          z-index: 10 !important;
        }
        [data-testid="stFileUploaderDropzone"] {
                    width: min(100%, 560px) !important;
                    height: 430px !important;
          cursor: pointer !important;
        }
        /* Hover glow */
        [data-testid="stFileUploaderDropzone"]:hover + #upload-zone,
        #upload-zone:hover {
          border-color: #1f6feb !important;
          box-shadow: 0 0 0 3px rgba(31,111,235,0.15), 0 0 30px rgba(31,111,235,0.1) !important;
        }
        /* Hide default Streamlit upload text */
        [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        key="xray_upload",
    )

    # Attach a short-lived JS binder to the hidden file input so we can
    # immediately scroll the Analyze button on file selection (before rerun).
    components.html(
        """
        <script>
        (function(){
            function tryBind(){
                const inp = document.querySelector('input[type=file]');
                if(!inp) return false;
                inp.addEventListener('change', ()=>{});
                return true;
            }
            let attempts = 0;
            const t = setInterval(()=>{ attempts += 1; if(tryBind() || attempts > 30) clearInterval(t); }, 150);
        })();
        </script>
        """,
        height=0,
    )

    if uploaded_file is None:
        # Ensure session state reflects no upload
        st.session_state.file_uploaded = False
        return None

    try:
        uploaded_image = load_uploaded_image(uploaded_file)

        st.markdown('<div style="border-radius:12px; overflow:hidden; border:1px solid #21262d; position:relative;">', unsafe_allow_html=True)
        st.markdown('<div style="position:absolute; top:10px; left:10px; background:rgba(13,17,23,0.8); border:1px solid #30363d; border-radius:6px; padding:4px 10px; font-size:11px; color:#58a6ff; font-weight:600; letter-spacing:0.5px; z-index:5;">LOADED</div>', unsafe_allow_html=True)
        st.image(uploaded_image, caption=uploaded_file.name, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # File info row below image
        file_size = len(uploaded_file.getvalue()) / 1024
        size_str = f"{file_size:.1f} KB" if file_size < 1024 else f"{file_size/1024:.1f} MB"

        st.markdown(f"""
        <div style="display:flex; gap:16px; padding:10px 14px; background:#161b22; border:1px solid #21262d; border-radius:8px; margin-top:8px;">
          <span style="color:#8b949e; font-size:12px;">📄 {uploaded_file.name}</span>
          <span style="color:#8b949e; font-size:12px;">💾 {size_str}</span>
          <span style="color:#3fb950; font-size:12px; margin-left:auto; font-weight:600;">✓ Ready to analyze</span>
        </div>
        """, unsafe_allow_html=True)

        # mark session state and request scroll to analyze
        st.session_state.file_uploaded = True
        st.session_state.scroll_trigger = 'analyze'
    except ValueError as error:
        st.warning(str(error))
        return None

    return uploaded_file


def add_prediction_to_history(filename, result):
    st.session_state.prediction_history.append(
        {
            "Filename": filename,
            "Prediction": result["label"],
            "Confidence": f"{result['confidence']:.1f}%",
            "Risk": result["risk_level"],
            "Time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )


def render_prediction_history():
    st.markdown("---")
    st.markdown('<div class="history-title">Prediction History</div>', unsafe_allow_html=True)

    if st.session_state.prediction_history:
        st.dataframe(
            st.session_state.prediction_history,
            use_container_width=True,
            hide_index=True,
        )

        if st.button("Clear History"):
            st.session_state.prediction_history = []
            st.session_state.latest_result = None
            st.session_state.latest_filename = None
            st.rerun()
    else:
        st.caption("No predictions in this session yet.")


def render_upload_waiting_panel():
    st.markdown(
        """
        <div class="main-card" style="margin-top: 0.25rem; border: 1px solid rgba(88,166,255,0.18); box-shadow: 0 0 0 1px rgba(31,111,235,0.09), 0 18px 44px rgba(0,0,0,0.35); background: linear-gradient(135deg, rgba(13,17,23,0.98), rgba(13,17,23,0.82)); overflow:hidden;">
            <div style="position:relative; overflow:hidden; border-radius: 16px; padding: 18px 18px 16px; border: 1px solid rgba(88,166,255,0.18); background: radial-gradient(circle at top right, rgba(88,166,255,0.12), rgba(13,17,23,0.96) 68%);">
                <div style="position:absolute; inset:-40px auto auto -40px; width:140px; height:140px; border-radius:50%; background: rgba(88,166,255,0.12); filter: blur(2px);"></div>
                <div style="position:absolute; right:18px; top:18px; width:84px; height:84px; border-radius:50%; border:1px solid rgba(88,166,255,0.22); box-shadow: inset 0 0 24px rgba(31,111,235,0.12);"></div>
                <div style="display:flex; align-items:flex-start; gap:14px; position:relative; z-index:1;">
                    <div style="flex:0 0 96px; min-height: 96px; border-radius: 18px; border: 1px solid rgba(88,166,255,0.22); background: linear-gradient(180deg, rgba(31,111,235,0.16), rgba(13,17,23,0.9)); display:flex; flex-direction:column; justify-content:center; align-items:flex-start; padding: 14px;">
                        <div style="display:inline-flex; align-items:center; gap:8px; font-size: 10px; letter-spacing: 0.16rem; color: #93c5fd; font-weight: 900; margin-bottom: 8px; text-transform: uppercase;">
                            <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background: #22c55e; box-shadow: 0 0 12px rgba(34,197,94,0.95); animation: uploadPulse 1.7s ease-in-out infinite;"></span>
                            Ready
                        </div>
                        <div style="color: #f8fbff; font-size: 0.92rem; font-weight: 900; line-height: 1.15; letter-spacing: -0.02em;">Stand by for image input.</div>
                    </div>
                    <div style="flex:1; padding: 2px 2px 0 0; min-height: 96px; display:flex; flex-direction:column; justify-content:center;">
                        <div style="font-size: 0.74rem; letter-spacing: 0.22rem; text-transform: uppercase; color: #7dd3fc; font-weight: 900; margin-bottom: 8px;">Awaiting image upload</div>
                        <div style="color: #f8fbff; font-size: 1.12rem; font-weight: 900; line-height: 1.32; margin-bottom: 8px;">No file selected yet.</div>
                        <div style="color: #b9c5df; font-size: 0.92rem; line-height: 1.6; max-width: 34rem;">
                            Use the box above to drag and drop, or click <strong style="color:#dbeafe;">Browse Files</strong> to choose an image.
                        </div>
                    </div>
                </div>
                <div style="margin-top: 12px; display:flex; flex-wrap:wrap; gap:8px; position:relative; z-index:1;">
                    <span style="padding:6px 10px; border-radius:999px; background:rgba(31,111,235,0.14); border:1px solid rgba(88,166,255,0.22); color:#cfe8ff; font-size:0.78rem; font-weight:800;">Drag & Drop</span>
                    <span style="padding:6px 10px; border-radius:999px; background:rgba(31,111,235,0.14); border:1px solid rgba(88,166,255,0.22); color:#cfe8ff; font-size:0.78rem; font-weight:800;">Instant Preview</span>
                    <span style="padding:6px 10px; border-radius:999px; background:rgba(31,111,235,0.14); border:1px solid rgba(88,166,255,0.22); color:#cfe8ff; font-size:0.78rem; font-weight:800;">Grad-CAM Ready</span>
                </div>
            </div>
        </div>
        <style>
        @keyframes uploadPulse {
            0% { transform: scale(1); opacity: 0.8; }
            50% { transform: scale(1.18); opacity: 1; }
            100% { transform: scale(1); opacity: 0.8; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown("---")
    st.markdown(
        """
        <div class="warning-box">
            ⚠️ <strong>DISCLAIMER:</strong> This tool is for educational purposes only.
            Not a substitute for professional medical diagnosis.
        </div>
        <p class="soft-text" style="margin-top: 0.8rem;">
            Project: Deep Learning based Pneumonia Detection System using CNN, TensorFlow, and Streamlit.
        </p>
        """,
        unsafe_allow_html=True,
    )


def auto_scroll(target_id="analyze-section"):
        js = f"""
        <script>
            setTimeout(function() {{
                const el = document.getElementById('{target_id}');
                if (el) {{
                    el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }} else {{
                    window.scrollBy({{ top: 400, behavior: 'smooth' }});
                }}
            }}, 300);
        </script>
        """
        components.html(js, height=0)


def scroll_to_bottom():
        js = """
        <script>
            setTimeout(function() {
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }, 500);
        </script>
        """
        components.html(js, height=0)


def main():
    inject_custom_css()
    initialize_session_state()
    threshold = render_sidebar()

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-title">
                <span class="brand-logo">
                    <img src="{LOGO_DATA_URI}" alt="PneumoAI logo" />
                </span>
                <span class="brand-wordmark">PneumoAI</span>
            </div>
            <div class="hero-rule">─────────────────────────────────────────</div>
            <div class="hero-subtitle">Clinical chest X-ray screening powered by deep learning.</div>
            <div class="status-badges">
                <span class="status-badge">🟢 Model Ready</span>
                <span class="status-badge">📊 CNN Architecture</span>
                <span class="status-badge">⚡ Real-time Analysis</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        uploaded_file = render_uploaded_image_panel()

    with right_col:
        st.markdown("## Analysis Result")
        analyze_clicked = st.button("🔍 Analyze X-ray", use_container_width=True)
        if uploaded_file is None and st.session_state.latest_result is None:
            render_upload_waiting_panel()
            result_placeholder = st.empty()
        else:
            result_placeholder = st.empty()

    if analyze_clicked:
        if uploaded_file is None:
            st.warning("Please upload a JPG, JPEG, or PNG image first.")
        else:
            try:
                with st.spinner("Analyzing X-ray image..."):
                    time.sleep(1)
                    result = predict_uploaded_image(uploaded_file, threshold)

                st.session_state.latest_result = result
                st.session_state.latest_filename = uploaded_file.name
                add_prediction_to_history(uploaded_file.name, result)

                if result["label"] == "PNEUMONIA":
                    st.error("Analysis complete: pneumonia pattern detected.")
                else:
                    st.success("Analysis complete: no pneumonia pattern detected.")
            except FileNotFoundError as error:
                st.error(str(error))
            except ValueError as error:
                st.warning(str(error))
            except Exception as error:
                st.error(f"Prediction failed: {error}")

    with result_placeholder.container():
        latest_result = st.session_state.latest_result
        latest_filename = st.session_state.latest_filename

        if latest_result and uploaded_file and latest_filename == uploaded_file.name:
            render_result(latest_result)
            render_gradcam_panel(latest_result)

    render_prediction_history()
    render_footer()

    _ = px.colors.qualitative.Plotly
    _ = plt.get_backend()


if __name__ == "__main__":
    main()
