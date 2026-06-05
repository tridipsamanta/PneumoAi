"""Data preprocessing and CNN architecture for pneumonia detection.

Step 2:
- Load train, validation, and test image folders.
- Apply data augmentation to the training set.
- Normalize validation and test images.
- Print dataset information and class distribution.
- Save a 3x3 preview grid of training images.

Step 3:
- Build and compile the CNN model.
- Print model summary and parameter counts.
- Save a model architecture diagram when Graphviz support is available.

Step 4:
- Train the model with callbacks.
- Save best and final models.
- Save accuracy/loss training plots.
- Print a concise training summary.
"""

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
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import (
    CSVLogger,
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
)
from tensorflow.keras.layers import (
    BatchNormalization,
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    MaxPooling2D,
)
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator


TRAIN_DIR = "dataset/chest_xray/train"
VAL_DIR = "dataset/chest_xray/val"
TEST_DIR = "dataset/chest_xray/test"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 15

MODEL_DIR = PROJECT_ROOT / "model"
LOGS_DIR = PROJECT_ROOT / "logs"

CLASS_NAMES = {
    0: "NORMAL",
    1: "PNEUMONIA",
}


def resolve_path(relative_path):
    """Resolve project-relative paths from this script's folder."""
    return PROJECT_ROOT / relative_path


def validate_dataset_paths():
    """Fail early with a useful message if the expected dataset folders are missing."""
    required_dirs = [
        resolve_path(TRAIN_DIR) / "NORMAL",
        resolve_path(TRAIN_DIR) / "PNEUMONIA",
        resolve_path(VAL_DIR) / "NORMAL",
        resolve_path(VAL_DIR) / "PNEUMONIA",
        resolve_path(TEST_DIR) / "NORMAL",
        resolve_path(TEST_DIR) / "PNEUMONIA",
    ]

    missing_dirs = [path for path in required_dirs if not path.is_dir()]
    if missing_dirs:
        missing_list = "\n".join(f"  - {path}" for path in missing_dirs)
        raise FileNotFoundError(
            "Dataset folders were not found at the expected locations:\n"
            f"{missing_list}\n\n"
            "Expected structure:\n"
            "  pneumonia_detection/dataset/chest_xray/train/NORMAL\n"
            "  pneumonia_detection/dataset/chest_xray/train/PNEUMONIA\n"
            "  pneumonia_detection/dataset/chest_xray/val/NORMAL\n"
            "  pneumonia_detection/dataset/chest_xray/val/PNEUMONIA\n"
            "  pneumonia_detection/dataset/chest_xray/test/NORMAL\n"
            "  pneumonia_detection/dataset/chest_xray/test/PNEUMONIA"
        )


def count_images_by_class(split_dir):
    """Count image files in NORMAL and PNEUMONIA folders for a split."""
    split_path = resolve_path(split_dir)
    extensions = {".jpg", ".jpeg", ".png"}
    counts = {}

    for class_name in ("NORMAL", "PNEUMONIA"):
        class_path = split_path / class_name
        counts[class_name] = sum(
            1
            for image_path in class_path.iterdir()
            if image_path.is_file() and image_path.suffix.lower() in extensions
        )

    return counts


def print_split_distribution(split_name, split_dir):
    counts = count_images_by_class(split_dir)
    total = counts["NORMAL"] + counts["PNEUMONIA"]

    print(f"{split_name} images: {total}")
    print(f"  NORMAL: {counts['NORMAL']}")
    print(f"  PNEUMONIA: {counts['PNEUMONIA']}")

    return total, counts


def create_data_generators():
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        horizontal_flip=True,
        zoom_range=0.2,
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        fill_mode="nearest",
    )

    validation_test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_generator = train_datagen.flow_from_directory(
        resolve_path(TRAIN_DIR),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary",
        shuffle=True,
    )

    val_generator = validation_test_datagen.flow_from_directory(
        resolve_path(VAL_DIR),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary",
        shuffle=False,
    )

    test_generator = validation_test_datagen.flow_from_directory(
        resolve_path(TEST_DIR),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="binary",
        shuffle=False,
    )

    return train_generator, val_generator, test_generator


def print_dataset_info(train_generator, val_generator, test_generator):
    print("\nDataset Information")
    print("-" * 50)

    print_split_distribution("Total training", TRAIN_DIR)
    print_split_distribution("Total validation", VAL_DIR)
    print_split_distribution("Total test", TEST_DIR)

    print("\nClass indices:")
    for class_name, class_index in train_generator.class_indices.items():
        print(f"  {class_name}: {class_index}")

    print("\nGenerator image counts:")
    print(f"  Training generator samples: {train_generator.samples}")
    print(f"  Validation generator samples: {val_generator.samples}")
    print(f"  Test generator samples: {test_generator.samples}")

    print("\nTraining schedule:")
    print(f"  Steps per epoch: {len(train_generator)}")
    print(f"  Validation steps: {len(val_generator)}")
    print("-" * 50)


def visualize_sample_images(train_generator):
    images, labels = next(train_generator)
    sample_indices = np.random.choice(len(images), size=9, replace=False)

    fig, axes = plt.subplots(3, 3, figsize=(10, 10))
    for axis, index in zip(axes.flat, sample_indices):
        label_index = int(labels[index])
        axis.imshow(images[index])
        axis.set_title(CLASS_NAMES[label_index])
        axis.axis("off")

    fig.suptitle("Sample Training Images", fontsize=16)
    plt.tight_layout()

    output_path = PROJECT_ROOT / "sample_images.png"
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"\nSaved sample image grid to: {output_path}")


def build_cnn_model():
    model = Sequential(
        [
            Conv2D(
                32,
                (3, 3),
                activation="relu",
                padding="same",
                input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
            ),
            BatchNormalization(),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(64, (3, 3), activation="relu", padding="same"),
            BatchNormalization(),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(128, (3, 3), activation="relu", padding="same"),
            BatchNormalization(),
            MaxPooling2D(pool_size=(2, 2)),
            Conv2D(256, (3, 3), activation="relu", padding="same"),
            BatchNormalization(),
            MaxPooling2D(pool_size=(2, 2)),
            Flatten(),
            Dense(512, activation="relu"),
            BatchNormalization(),
            Dropout(0.5),
            Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model


def save_model_architecture_diagram(model):
    output_path = PROJECT_ROOT / "model_architecture.png"

    try:
        tf.keras.utils.plot_model(
            model,
            to_file=str(output_path),
            show_shapes=True,
            show_layer_names=True,
        )
        print(f"\nSaved model architecture diagram to: {output_path}")
    except (ImportError, OSError, ValueError, AttributeError) as error:
        print("\nSkipped model architecture diagram.")
        print(f"Reason: {error}")
        print("Install pydot and Graphviz if you want to generate this PNG.")


def print_model_parameter_info(model):
    total_params = model.count_params()
    trainable_params = int(
        np.sum([np.prod(weight.shape) for weight in model.trainable_weights])
    )
    non_trainable_params = int(
        np.sum([np.prod(weight.shape) for weight in model.non_trainable_weights])
    )
    estimated_model_size_mb = (total_params * 4) / (1024**2)

    print("\nModel Parameter Information")
    print("-" * 50)
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Non-trainable parameters: {non_trainable_params:,}")
    print(f"Estimated model size: {estimated_model_size_mb:.2f} MB")
    print("-" * 50)


def create_output_directories():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)


def create_training_callbacks():
    checkpoint = ModelCheckpoint(
        filepath=str(MODEL_DIR / "best_model.h5"),
        monitor="val_accuracy",
        save_best_only=True,
        mode="max",
        verbose=1,
    )

    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True,
        verbose=1,
    )

    reduce_lr = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1,
    )

    csv_logger = CSVLogger(
        filename=str(LOGS_DIR / "training_log.csv"),
        append=False,
    )

    return [checkpoint, early_stopping, reduce_lr, csv_logger]


def calculate_training_steps(train_generator, val_generator):
    steps_per_epoch = train_generator.samples // BATCH_SIZE
    validation_steps = val_generator.samples // BATCH_SIZE

    if steps_per_epoch == 0:
        steps_per_epoch = 1

    if validation_steps == 0:
        validation_steps = 1

    return steps_per_epoch, validation_steps


def train_model(model, train_generator, val_generator):
    create_output_directories()
    callbacks = create_training_callbacks()
    steps_per_epoch, validation_steps = calculate_training_steps(
        train_generator,
        val_generator,
    )

    print("\nTraining Configuration")
    print("-" * 50)
    print(f"Epochs: {EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Steps per epoch: {steps_per_epoch}")
    print(f"Validation steps: {validation_steps}")
    print(f"Best model path: {MODEL_DIR / 'best_model.h5'}")
    print(f"Training log path: {LOGS_DIR / 'training_log.csv'}")
    print("-" * 50)

    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        steps_per_epoch=steps_per_epoch,
        validation_data=val_generator,
        validation_steps=validation_steps,
        callbacks=callbacks,
        verbose=1,
    )

    model.save(str(MODEL_DIR / "final_model.h5"))
    print("\n✅ Models saved to model/ folder")

    return history


def plot_training_graphs(history):
    epochs = range(1, len(history.history["accuracy"]) + 1)

    plt.figure(figsize=(8, 6))
    plt.plot(epochs, history.history["accuracy"], label="Training Accuracy")
    plt.plot(epochs, history.history["val_accuracy"], label="Validation Accuracy")
    plt.title("Model Accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    accuracy_plot_path = LOGS_DIR / "accuracy_plot.png"
    plt.savefig(accuracy_plot_path, dpi=150)
    plt.close()

    plt.figure(figsize=(8, 6))
    plt.plot(epochs, history.history["loss"], label="Training Loss")
    plt.plot(epochs, history.history["val_loss"], label="Validation Loss")
    plt.title("Model Loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    loss_plot_path = LOGS_DIR / "loss_plot.png"
    plt.savefig(loss_plot_path, dpi=150)
    plt.close()

    print(f"Saved accuracy plot to: {accuracy_plot_path}")
    print(f"Saved loss plot to: {loss_plot_path}")


def get_current_learning_rate(model):
    learning_rate = model.optimizer.learning_rate
    return float(tf.keras.backend.get_value(learning_rate))


def print_training_summary(history, model):
    epochs_run = len(history.history.get("loss", []))
    best_val_accuracy = max(history.history.get("val_accuracy", [0.0]))
    best_val_loss = min(history.history.get("val_loss", [float("inf")]))
    final_learning_rate = get_current_learning_rate(model)

    print("\nTraining Summary")
    print("-" * 50)
    print(f"Total epochs run: {epochs_run}")
    print(f"Best validation accuracy: {best_val_accuracy:.4f}")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Final learning rate: {final_learning_rate:.8f}")
    print("-" * 50)


def main():
    print(f"TensorFlow version: {tf.__version__}")
    print(f"Keras version: {keras.__version__}")
    print(f"Project root: {PROJECT_ROOT}")

    validate_dataset_paths()

    train_generator, val_generator, test_generator = create_data_generators()
    print_dataset_info(train_generator, val_generator, test_generator)
    visualize_sample_images(train_generator)

    model = build_cnn_model()
    print("\nCNN Model Summary")
    print("-" * 50)
    model.summary()
    print_model_parameter_info(model)
    save_model_architecture_diagram(model)

    history = train_model(model, train_generator, val_generator)
    plot_training_graphs(history)
    print_training_summary(history, model)

    print("\nStep 4 model training complete. Evaluation will be added in Step 5.")


if __name__ == "__main__":
    main()
