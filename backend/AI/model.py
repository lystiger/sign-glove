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

# Get absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(current_dir), 'data')
gesture_data_path = os.path.join(data_dir, 'gesture_data.csv')
model_output_path = os.path.join(current_dir, 'gesture_model.tflite')
metrics_output_path = os.path.join(current_dir, 'training_metrics.json')
results_dir = os.path.join(current_dir, 'results')
os.makedirs(results_dir, exist_ok=True)

# Load CSV
df = pd.read_csv(gesture_data_path)  # absolute path to CSV file

# Remove session_id column if it exists (it contains string values)
if 'session_id' in df.columns:
    df = df.drop('session_id', axis=1)
    print(f"Removed session_id column from features")

# Separate features and labels properly
# Features: all columns except 'label'
# Label: only the 'label' column
feature_columns = [col for col in df.columns if col != 'label']
X = df[feature_columns].values  # features (excluding label column)
y = df['label'].values          # label column

print(f"Feature columns: {feature_columns}")
print(f"Label values: {np.unique(y)}")

# Convert string labels to numeric for training
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print(f"Encoded labels: {label_encoder.classes_} -> {np.unique(y_encoded)}")

# Chuẩn hóa dữ liệu -> cause neural network works best with normalized data
scaler = StandardScaler()
X = scaler.fit_transform(X)

# One-hot encode label 
num_classes = len(np.unique(y_encoded))
y_cat = to_categorical(y_encoded, num_classes=num_classes)

# Get number of features dynamically
num_features = X.shape[1]
print(f"Number of features: {num_features}")
print(f"Number of classes: {num_classes}")

#Chia dữ liệu train/test : 80% train 20% test
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# Xây mô hình MLP phức tạp hơn
# Tăng số lượng layer và số lượng neuron để model học tốt hơn các đặc trưng phức tạp
model = Sequential([
    Dense(256, activation='relu', input_shape=(num_features,)),  # Layer ẩn lớn đầu tiên
    Dense(128, activation='relu'),  # Layer ẩn thứ hai
    Dense(64, activation='relu'),   # Layer ẩn thứ ba
    Dense(num_classes, activation='softmax')  # Output layer
])
# Giải thích:
# - 256, 128, 64 là số lượng neuron ở mỗi layer, càng nhiều thì model càng "mạnh" (nhưng cũng dễ overfit nếu data ít)
# - relu vẫn là active function phổ biến cho hidden layer
# - softmax cho output layer để dự đoán xác suất từng class

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()
# loss ở đây là loss function, check xem kết quả dự đoán là good hay bad
# sau khi loss dự đoán rồi sẽ truyền data đó cho optimizer
# optimizer function sau đó sẽ đưa ra dự đoán tốt hơn loss function
# sau đó lặp lại vòng lặp đó loss function -> optimizer
# well về cơ bản thì loss function với optimizer function thì có nhiều cái lắm nên tui cx chọn cái tốt nhất

# Huấn luyện
history = model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.1)
# epoch là loop nhé, epochs = 50 nghĩa là train 50 vòng, train càng nhiều vòng thì loss càng giảm
# loss giảm dẫn tới accuracy tăng
# fit function là để train nhé 

# Đánh giá 
loss, acc = model.evaluate(X_test, y_test)
print(f"\n Test accuracy: {acc:.3f}")

# Generate predictions for metrics
y_pred_proba = model.predict(X_test)
y_pred_classes = np.argmax(y_pred_proba, axis=1)
y_true_classes = np.argmax(y_test, axis=1)

# Calculate confusion matrix
cm = confusion_matrix(y_true_classes, y_pred_classes)

# Calculate classification report
class_report = classification_report(y_true_classes, y_pred_classes, output_dict=True)

# Calculate ROC curves for each class
fpr = dict()
tpr = dict()
roc_auc = dict()

# Binarize the output for ROC calculation
y_test_bin = label_binarize(y_true_classes, classes=range(num_classes))

for i in range(num_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_pred_proba[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Calculate micro-average ROC curve and ROC area
fpr["micro"], tpr["micro"], _ = roc_curve(y_test_bin.ravel(), y_pred_proba.ravel())
roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

# Save metrics to JSON file
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

# Generate and save visualization plots
plt.style.use('default')

# 1. Confusion Matrix Heatmap
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

# 2. ROC Curves
plt.figure(figsize=(12, 8))
colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'red', 'green', 'purple'])

# Plot ROC curves for each class
for i, color in zip(range(num_classes), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=2,
             label=f'{label_encoder.classes_[i]} (AUC = {roc_auc[i]:.2f})')

# Plot micro-average ROC curve
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

# 3. Training History
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Accuracy plot
ax1.plot(history.history['accuracy'], label='Training Accuracy')
ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
ax1.set_title('Model Accuracy')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True)

# Loss plot
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

# Convert sang TensorFlow Lite (quantization float16 hoặc int8) 
# quantization đơn giản là nén nhỏ lại hay là tối ưu hóa model cho nó bớt bytes
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # enable quantization

# Với dữ liệu float chuẩn hóa → để TensorFlow tự chọn cách tốt nhất
tflite_model = converter.convert()

# Lưu file .tflite 
with open(model_output_path, "wb") as f:
    f.write(tflite_model)

print(f" Đã lưu model thành {model_output_path}")
