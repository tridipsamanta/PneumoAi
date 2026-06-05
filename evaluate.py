"""Evaluate the trained pneumonia detection CNN on the test set."""

import os
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
MPL_CONFIG_DIR = PROJECT_ROOT / ".matplotlib"
XDG_CACHE_DIR = PROJECT_ROOT / ".cache"
MPL_CONFIG_DIR.mkdir(exist_ok=True)
XDG_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(XDG_CACHE_DIR))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator


TEST_DIR = "dataset/chest_xray/test"
MODEL_PATH = "model/best_model.h5"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
LOGS_DIR = PROJECT_ROOT / "logs"
CLASS_NAMES = ["NORMAL", "PNEUMONIA"]


def resolve_path(relative_path):
    return PROJECT_ROOT / relative_path


def validate_paths():
    model_path = resolve_path(MODEL_PATH)
    test_dir = resolve_path(TEST_DIR)

    if not model_path.is_file():
        raise FileNotFoundError(
            f"Model file not found: {model_path}\n"
            "Run training first and confirm model/best_model.h5 exists."
        )

    required_dirs = [test_dir / "NORMAL", test_dir / "PNEUMONIA"]
    missing_dirs = [path for path in required_dirs if not path.is_dir()]
    if missing_dirs:
        missing_list = "\n".join(f"  - {path}" for path in missing_dirs)
        raise FileNotFoundError(
            "Test dataset folders were not found:\n"
            f"{missing_list}\n\n"
            "Expected structure:\n"
            "  pneumonia_detection/dataset/chest_xray/test/NORMAL\n"
            "  pneumonia_detection/dataset/chest_xray/test/PNEUMONIA"
        )


def load_best_model():
    model = keras.models.load_model(resolve_path(MODEL_PATH), compile=False)
    print("✅ Model loaded successfully")
    model.summary()
    return model


def create_test_generator():
    test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    test_generator = test_datagen.flow_from_directory(
        resolve_path(TEST_DIR),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary",
        shuffle=False,
    )

    print("\nClass indices:")
    for class_name, class_index in test_generator.class_indices.items():
        print(f"  {class_name}: {class_index}")

    return test_generator


def run_predictions(model, test_generator):
    test_generator.reset()
    prediction_probs = model.predict(test_generator, verbose=1).flatten()
    predicted_labels = (prediction_probs > 0.5).astype(int)
    true_labels = test_generator.classes

    print("\nSanity check: first 10 true vs predicted labels")
    print("-" * 50)
    for index, (true_label, predicted_label) in enumerate(
        zip(true_labels[:10], predicted_labels[:10]), start=1
    ):
        print(
            f"{index:02d}. True: {CLASS_NAMES[int(true_label)]} | "
            f"Predicted: {CLASS_NAMES[int(predicted_label)]} | "
            f"Probability: {prediction_probs[index - 1]:.4f}"
        )

    return prediction_probs, predicted_labels, true_labels


def calculate_metrics(true_labels, predicted_labels, prediction_probs):
    accuracy = accuracy_score(true_labels, predicted_labels)
    precision = precision_score(true_labels, predicted_labels, zero_division=0)
    recall = recall_score(true_labels, predicted_labels, zero_division=0)
    f1 = f1_score(true_labels, predicted_labels, zero_division=0)
    auc_roc = roc_auc_score(true_labels, prediction_probs)

    cm = confusion_matrix(true_labels, predicted_labels, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) else 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "specificity": specificity,
        "auc_roc": auc_roc,
        "confusion_matrix": cm,
    }


def print_metrics(metrics):
    print("\n================================")
    print("MODEL EVALUATION RESULTS")
    print("================================")
    print(f"Accuracy   : {metrics['accuracy'] * 100:.2f}%")
    print(f"Precision  : {metrics['precision'] * 100:.2f}%")
    print(f"Recall     : {metrics['recall'] * 100:.2f}%")
    print(f"F1-Score   : {metrics['f1'] * 100:.2f}%")
    print(f"Specificity: {metrics['specificity'] * 100:.2f}%")
    print(f"AUC-ROC    : {metrics['auc_roc']:.4f}")
    print("================================")


def plot_confusion_matrix(cm):
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
    )
    plt.title("Confusion Matrix — Pneumonia Detection")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()

    output_path = LOGS_DIR / "confusion_matrix.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved confusion matrix to: {output_path}")


def print_classification_report(true_labels, predicted_labels):
    print("\nClassification Report")
    print("-" * 50)
    print(
        classification_report(
            true_labels,
            predicted_labels,
            labels=[0, 1],
            target_names=CLASS_NAMES,
            zero_division=0,
        )
    )


def plot_roc_curve(true_labels, prediction_probs, auc_roc):
    fpr, tpr, _ = roc_curve(true_labels, prediction_probs)

    plt.figure(figsize=(7, 6))
    plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {auc_roc:.4f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random Guess")
    plt.title("ROC Curve — Pneumonia Detection")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    output_path = LOGS_DIR / "roc_curve.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved ROC curve to: {output_path}")


def plot_sample_predictions(test_generator, true_labels, predicted_labels):
    sample_size = min(9, len(test_generator.filepaths))
    sample_indices = np.random.choice(
        len(test_generator.filepaths),
        size=sample_size,
        replace=False,
    )

    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    axes = axes.flat

    for axis, sample_index in zip(axes, sample_indices):
        image_path = test_generator.filepaths[sample_index]
        image = keras.utils.load_img(image_path, target_size=IMG_SIZE)

        true_label = int(true_labels[sample_index])
        predicted_label = int(predicted_labels[sample_index])
        is_correct = true_label == predicted_label
        mark = "✅" if is_correct else "❌"
        title_color = "green" if is_correct else "red"

        axis.imshow(image, cmap="gray")
        axis.set_title(
            f"True: {CLASS_NAMES[true_label]} | "
            f"Pred: {CLASS_NAMES[predicted_label]} {mark}",
            color=title_color,
            fontsize=10,
        )
        axis.axis("off")

    for axis in axes[sample_size:]:
        axis.axis("off")

    plt.tight_layout()
    output_path = LOGS_DIR / "sample_predictions.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved sample predictions to: {output_path}")


def main():
    print(f"TensorFlow version: {tf.__version__}")
    print(f"Keras version: {keras.__version__}")
    print(f"Project root: {PROJECT_ROOT}")

    LOGS_DIR.mkdir(exist_ok=True)
    validate_paths()

    model = load_best_model()
    test_generator = create_test_generator()
    prediction_probs, predicted_labels, true_labels = run_predictions(
        model,
        test_generator,
    )

    metrics = calculate_metrics(true_labels, predicted_labels, prediction_probs)
    print_metrics(metrics)
    plot_confusion_matrix(metrics["confusion_matrix"])
    print_classification_report(true_labels, predicted_labels)
    plot_roc_curve(true_labels, prediction_probs, metrics["auc_roc"])
    plot_sample_predictions(test_generator, true_labels, predicted_labels)

    print("\nStep 5 evaluation complete.")


if __name__ == "__main__":
    main()
