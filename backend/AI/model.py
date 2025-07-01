import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense   
from tensorflow.keras.utils import to_categorical
import tensorflow as tf

# Load CSV
df = pd.read_csv('gesture_data.csv')  # đường dẫn đến file CSV

# Tách input và label để phân loại cử chỉ, giả dụ 11 giá trị khác nhau = 1 label khác nhau
X = df.iloc[:, :-1].values     # 11 features
y = df.iloc[:, -1].values      # label (int)

# Chuẩn hóa dữ liệu -> cause neural network works best with normalized data
scaler = StandardScaler()
X = scaler.fit_transform(X)

# One-hot encode label 
num_classes = len(np.unique(y))
y_cat = to_categorical(y, num_classes=num_classes)

#Chia dữ liệu train/test : 80% train 20% test
X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# Xây mô hình MLP 
model = Sequential([
    Dense(32, activation='relu', input_shape=(11,)),
    Dense(32, activation='relu'),
    Dense(num_classes, activation='softmax')
])
# ae có thể băn khoăn activation ở đây là gì thì...
# mỗi layers of neuron cần 1 active function để bảo layer đó làm gì, giống não người chia thành nhiều vùng í
# mỗi vùng 1 chức năng riêng biệt
# active function thì đa dạng lắm nên chọn cái nào tốt nhất thui
# Dense ở đây là layer nhé ae, do mình không dùng ảnh nên shape của nó sẽ là linear 11 giá trị
# relu ở đây hiểu đơn giản là if x > 0 return x else return 0 hay nghĩa là x phải > o thì pass tiếp value cho layer tiếp theo
# softmax hiểu đơn giản là ae sẽ có 1 list values, xong ae scale nó sao cho tổng các values = 1
# xong với từng scaled values thì ae hiểu nó như là probability của output 
# ví dụ như là ở các output layers đi thì ở index = 4 nó có giá trị prob cao nhất -> nó dự đoán input là cử chỉ A
# nếu ở index = 5 có giá trị prob cao nhất -> nó dự đoán input là cử chỉ B

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
with open("gesture_model.tflite", "wb") as f:
    f.write(tflite_model)

print(" Đã lưu model thành gesture_model.tflite")
