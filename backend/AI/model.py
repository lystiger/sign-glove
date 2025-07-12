import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense   
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
import os

# Get absolute paths
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(current_dir), 'data')
gesture_data_path = os.path.join(data_dir, 'gesture_data.csv')
model_output_path = os.path.join(current_dir, 'gesture_model.tflite')

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
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.1)
# epoch là loop nhé, epochs = 50 nghĩa là train 50 vòng, train càng nhiều vòng thì loss càng giảm
# loss giảm dẫn tới accuracy tăng
# fit function là để train nhé 
# Đánh giá 
loss, acc = model.evaluate(X_test, y_test)
print(f"\n Test accuracy: {acc:.3f}")

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
