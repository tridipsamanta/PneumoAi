"""Single-image prediction script for pneumonia detection."""

import argparse
import os
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
MPL_CONFIG_DIR = PROJECT_ROOT / ".matplotlib"
XDG_CACHE_DIR = PROJECT_ROOT / ".cache"
MPL_CONFIG_DIR.mkdir(exist_ok=True)
XDG_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError
from tensorflow import keras


MODEL_PATH = "model/best_model.h5"
IMG_SIZE = (224, 224)
CLASS_NAMES = {0: "NORMAL", 1: "PNEUMONIA"}
THRESHOLD = 0.5
ACCEPTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def resolve_project_path(relative_path):
    return PROJECT_ROOT / relative_path


def resolve_image_path(image_path):
    path = pathlib.Path(image_path).expanduser()

    if path.is_absolute():
        return path

    current_dir_path = pathlib.Path.cwd() / path
    if current_dir_path.exists():
        return current_dir_path

    project_root_path = PROJECT_ROOT / path
    if project_root_path.exists():
        return project_root_path

    return current_dir_path


def load_model():
    model_path = resolve_project_path(MODEL_PATH)
    if not model_path.is_file():
        raise FileNotFoundError(
            f"Model not found: {model_path}\n"
            "Run train.py first to generate the model."
        )

    model = keras.models.load_model(model_path, compile=False)
    print("✅ Model loaded")
    return model


def preprocess_image(image_path):
    image_path = resolve_image_path(image_path)

    if not image_path.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if image_path.suffix.lower() not in ACCEPTED_EXTENSIONS:
        accepted = ", ".join(sorted(ACCEPTED_EXTENSIONS))
        raise ValueError(f"Unsupported image format. Accepted formats: {accepted}")

    try:
        image = Image.open(image_path).convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("Could not read image, please try another file.") from error

    image = image.resize(IMG_SIZE)
    image_array = np.array(image, dtype=np.float32)
    image_array = image_array / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    return image_array


def get_risk_level(probability):
    if probability >= 0.85:
        return "HIGH", "Immediate medical consultation advised."

    if probability >= 0.5:
        return "MODERATE", "Further clinical evaluation recommended."

    return "LOW", "No signs of pneumonia detected."


def predict(image_path, model):
    processed_image = preprocess_image(image_path)
    probability = float(model.predict(processed_image, verbose=0)[0][0])
    class_index = 1 if probability >= THRESHOLD else 0
    label = CLASS_NAMES[class_index]

    if class_index == 1:
        confidence = probability * 100
    else:
        confidence = (1 - probability) * 100

    risk_level, recommendation = get_risk_level(probability)

    return {
        "label": label,
        "confidence": confidence,
        "probability": probability,
        "risk_level": risk_level,
        "recommendation": recommendation,
    }


def display_result(image_path, result):
    image_path = resolve_image_path(image_path)

    try:
        image = Image.open(image_path).convert("RGB")
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("Could not read image, please try another file.") from error

    is_pneumonia = result["label"] == "PNEUMONIA"
    status_icon = "❗" if is_pneumonia else "✅"
    title_color = "red" if is_pneumonia else "green"

    title = (
        f"{result['label']} {status_icon} | "
        f"Confidence: {result['confidence']:.1f}% | "
        f"Risk: {result['risk_level']}"
    )

    plt.figure(figsize=(7, 7))
    plt.imshow(image, cmap="gray")
    plt.title(title, color=title_color, fontsize=12)
    plt.axis("off")
    plt.tight_layout()

    output_path = PROJECT_ROOT / "prediction_output.png"
    plt.savefig(output_path, dpi=150)
    print(f"\nSaved prediction output image to: {output_path}")
    plt.show()
    plt.close()


def print_result(image_path, result):
    image_path = resolve_image_path(image_path)
    is_pneumonia = result["label"] == "PNEUMONIA"
    status_icon = "❗" if is_pneumonia else "✅"

    print("\n=========================================")
    print("PNEUMONIA DETECTION RESULT")
    print("=========================================")
    print(f"Image          : {image_path.name}")
    print(f"Prediction     : {result['label']} {status_icon}")
    print(f"Confidence     : {result['confidence']:.1f}%")
    print(f"Risk Level     : {result['risk_level']}")
    print(f"Probability    : {result['probability']:.4f}")
    print(f"Recommendation : {result['recommendation']}")
    print("=========================================")
    print("⚠️  DISCLAIMER: For educational purposes only.")
    print("    Not a substitute for professional diagnosis.")
    print("=========================================")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Predict pneumonia from a single chest X-ray image.",
        usage="python predict.py --image path/to/xray.jpg",
    )
    parser.add_argument(
        "positional_image",
        nargs="?",
        help="Path to a JPEG or PNG chest X-ray image.",
    )
    parser.add_argument(
        "--image",
        dest="image",
        help="Path to a JPEG or PNG chest X-ray image.",
    )

    args = parser.parse_args()
    image_path = args.image or args.positional_image

    if not image_path:
        parser.print_help()
        print("\nExample:")
        print("  python predict.py --image dataset/chest_xray/test/PNEUMONIA/person1.jpeg")
        sys.exit(1)

    return image_path


def main():
    image_path = parse_args()

    try:
        print(f"TensorFlow version: {tf.__version__}")
        print(f"Keras version: {keras.__version__}")
        print(f"OpenCV version: {cv2.__version__}")

        model = load_model()
        result = predict(image_path, model)
        print_result(image_path, result)
        display_result(image_path, result)
    except FileNotFoundError as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
    except ValueError as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
    except Exception as error:
        print(f"\nUnexpected error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
