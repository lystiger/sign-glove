import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.preprocessing import label_binarize
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense   
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import cycle
import sys
from datetime import datetime
from uuid import uuid4
import asyncio

# Add the parent directory to Python path so we can import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.database import model_collection
    from models.model_result import ModelResult
except ImportError as e:
    print(f"Warning: Could not import database modules: {e}")
    model_collection = None
    ModelResult = None

try:
    from core.settings import settings
except ImportError:
    # Fallback if core.settings is not available
    class Settings:
        GESTURE_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'gesture_data.csv')
        MODEL_PATH = os.path.join(os.path.dirname(__file__), 'gesture_model.tflite')
        METRICS_PATH = os.path.join(os.path.dirname(__file__), 'training_metrics.json')
        RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
    
    settings = Settings()

# Use centralized settings for all paths
# Check if a specific data file is specified via environment variable
gesture_data_path = os.environ.get('GESTURE_DATA_FILE', settings.GESTURE_DATA_PATH)
model_output_path = settings.MODEL_PATH
metrics_output_path = settings.METRICS_PATH
results_dir = settings.RESULTS_DIR
os.makedirs(results_dir, exist_ok=True)

# Load CSV
df = pd.read_csv(gesture_data_path)  # absolute path to CSV file

# Remove session_id column if it exists (it contains string values)
if 'session_id' in df.columns:
    df = df.drop('session_id', axis=1)
    print(f"Removed session_id column from features")

# Separate features and labels properly
feature_columns = [col for col in df.columns if col != 'label']
X = df[feature_columns].values  # features (excluding label column)
y = df['label'].values          # label column

print(f"Feature columns: {feature_columns}")
print(f"Label values: {np.unique(y)}")

# Detect if this is single-hand (11 features) or dual-hand (22 features) data
num_features = X.shape[1]
if num_features == 11:
    print("Detected single-hand configuration (11 features)")
    hand_config = "single"
elif num_features == 22:
    print("Detected dual-hand configuration (22 features)")
    hand_config = "dual"
else:
    raise ValueError(f"Unsupported feature count: {num_features}. Expected 11 (single-hand) or 22 (dual-hand)")

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print(f"Encoded labels: {label_encoder.classes_} -> {np.unique(y_encoded)}")

scaler = StandardScaler()
X = scaler.fit_transform(X)

num_classes = len(np.unique(y_encoded))
y_cat = to_categorical(y_encoded, num_classes=num_classes)

print(f"Number of features: {num_features} ({hand_config}-hand)")
print(f"Number of classes: {num_classes}")

X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# Adjust model architecture based on input size
if hand_config == "single":
    # Optimized for single-hand (11 features)
    model = Sequential([
        Dense(128, activation='relu', input_shape=(num_features,)),
        Dense(64, activation='relu'),
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
else:
    # Larger architecture for dual-hand (22 features)
    model = Sequential([
        Dense(512, activation='relu', input_shape=(num_features,)),
        Dense(256, activation='relu'),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])

print(f"Model architecture optimized for {hand_config}-hand configuration")

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

history = model.fit(X_train, y_train, epochs=100, batch_size=16, validation_split=0.1)

loss, acc = model.evaluate(X_test, y_test)
print(f"\n Test accuracy: {acc:.3f}")

y_pred_proba = model.predict(X_test)
y_pred_classes = np.argmax(y_pred_proba, axis=1)
y_true_classes = np.argmax(y_test, axis=1)

cm = confusion_matrix(y_true_classes, y_pred_classes)
class_report = classification_report(y_true_classes, y_pred_classes, output_dict=True)
fpr = dict()
tpr = dict()
roc_auc = dict()
y_test_bin = label_binarize(y_true_classes, classes=range(num_classes))
for i in range(num_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_pred_proba[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])
fpr["micro"], tpr["micro"], _ = roc_curve(y_test_bin.ravel(), y_pred_proba.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

def safe_float(value):
    """Convert value to float, handling NaN and infinity values"""
    if np.isnan(value) or np.isinf(value):
        return None
    return float(value)

def safe_list(arr):
    """Convert array to list, handling NaN values"""
    return [safe_float(x) if isinstance(x, (int, float, np.number)) else x for x in arr]

metrics_data = {
    "accuracy": float(acc),
    "loss": float(loss),
    "confusion_matrix": cm.tolist(),
    "classification_report": class_report,
    "roc_curves": {
        "fpr": {str(k): safe_list(v) for k, v in fpr.items()},
        "tpr": {str(k): safe_list(v) for k, v in tpr.items()},
        "auc": {str(k): safe_float(v) for k, v in roc_auc.items()}
    },
    "labels": label_encoder.classes_.tolist(),
    "training_history": {
        "accuracy": [float(x) for x in history.history['accuracy']],
        "val_accuracy": [float(x) for x in history.history['val_accuracy']],
        "loss": [float(x) for x in history.history['loss']],
        "val_loss": [float(x) for x in history.history['val_loss']]
    }
}

with open(metrics_output_path, 'w') as f:
    json.dump(metrics_data, f, indent=2)

print(f"Metrics saved to {metrics_output_path}")

plt.style.use('default')

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=label_encoder.classes_, 
            yticklabels=label_encoder.classes_)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
plt.close()

plt.figure(figsize=(12, 8))
colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'red', 'green', 'purple'])
for i, color in zip(range(num_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label=f'{label_encoder.classes_[i]} (AUC = {roc_auc[i]:.2f})')
plt.plot(fpr["micro"], tpr["micro"], color='deeppink', linestyle=':', linewidth=4,
         label=f'Micro-average (AUC = {roc_auc["micro"]:.2f})')
plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves for Multi-class Classification')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'roc_curves.png'), dpi=300, bbox_inches='tight')
plt.close()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
ax1.plot(history.history['accuracy'], label='Training Accuracy')
ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
ax1.set_title('Model Accuracy')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True)
ax2.plot(history.history['loss'], label='Training Loss')
ax2.plot(history.history['val_loss'], label='Validation Loss')
ax2.set_title('Model Loss')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.legend()
ax2.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'training_history.png'), dpi=300, bbox_inches='tight')
plt.close()

print("Visualization plots saved!")

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
with open(model_output_path, "wb") as f:
    f.write(tflite_model)
print(f" Model saved to {model_output_path}")

try:
    # Only try to save to database if imports were successful
    if model_collection is not None and ModelResult is not None:
        # Create a ModelResult instance
        result = ModelResult(
            session_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            accuracy=float(acc),            # test accuracy from model evaluation
            model_name="SignGloveModel",    # optional, you can use a meaningful name
            notes="Training completed successfully"
        )

        # Insert into MongoDB asynchronously
        async def insert_result():
            res = await model_collection.insert_one(result.model_dump())
            print(f"Inserted training result into MongoDB: {res.inserted_id}")

        asyncio.run(insert_result())
    else:
        print("Database modules not available - skipping result storage")

except Exception as e:
    print(f"Failed to insert training result into MongoDB: {e}")

print("Training completed successfully!")