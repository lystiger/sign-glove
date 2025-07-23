import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.preprocessing import label_binarize
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense   
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import cycle
from core.settings import settings

# Use centralized settings for all paths
gesture_data_path = settings.GESTURE_DATA_PATH
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

from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print(f"Encoded labels: {label_encoder.classes_} -> {np.unique(y_encoded)}")

scaler = StandardScaler()
X = scaler.fit_transform(X)

num_classes = len(np.unique(y_encoded))
y_cat = to_categorical(y_encoded, num_classes=num_classes)

num_features = X.shape[1]
print(f"Number of features: {num_features}")
print(f"Number of classes: {num_classes}")

X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

model = Sequential([
    Dense(256, activation='relu', input_shape=(num_features,)),
    Dense(128, activation='relu'),
    Dense(64, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.1)

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

metrics_data = {
    "accuracy": float(acc),
    "loss": float(loss),
    "confusion_matrix": cm.tolist(),
    "classification_report": class_report,
    "roc_curves": {
        "fpr": {str(k): v.tolist() for k, v in fpr.items()},
        "tpr": {str(k): v.tolist() for k, v in tpr.items()},
        "auc": {str(k): float(v) for k, v in roc_auc.items()}
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
print(f" Đã lưu model thành {model_output_path}")
