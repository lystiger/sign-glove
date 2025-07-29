# ✋ Sign Glove AI – Real-time Gesture Recognition System

This project enables real-time sign language translation using a smart glove equipped with flex sensors and an IMU. The system collects gesture data, allows dataset management, trains machine learning models, and performs real-time prediction using a trained model.

---

## 📦 Tech Stack

- **Backend:** FastAPI + MongoDB + Python
- **AI Model:** TensorFlow Lite (.tflite)
- **Frontend:** React + Vite 
- **Database:** MongoDB (collections: `sensor_data`, `model_results`)

---

## 🚀 Features

### 🎛️ Sensor + Gesture Management
- `POST /sensor-data` – Store incoming glove sensor values
- `GET/POST/PUT/DELETE /gestures` – Manage labeled gesture sessions

### 🤖 Model Training
- `POST /training` – Manually save training result
- `POST /training/run` – Train a model from CSV or database
- `GET /training` – List all training sessions
- `GET /training/latest` – Get most recent training result
- `GET /training/metrics/latest` – Get detailed training metrics
- `GET /training/visualizations/{type}` – Get training visualizations

### 🧠 Prediction
- `POST /predict` – Predict label from 11 sensor values
- `GET /predict/live` – Predict using the most recent MongoDB sensor document

### 📊 System Dashboard
- `GET /dashboard` – System summary:
  - Total gesture sessions
  - Total training models
  - Average accuracy
  - Last activity timestamp

### 🛠️ Admin Tools
- `DELETE /admin/sensor-data` – Clear all sensor data
- `DELETE /admin/training-results` – Clear all training results

---

## 📚 API Usage

- Interactive API docs: [http://localhost:8080/docs](http://localhost:8080/docs)
- Redoc docs: [http://localhost:8080/redoc](http://localhost:8080/redoc)

### Example: Create a Gesture Session

```bash
curl -X POST "http://localhost:8080/gestures/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "timestamp": "2025-07-23T12:00:00Z",
    "sensor_values": [[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1]],
    "gesture_label": "hello",
    "device_info": {"source": "USB", "device_id": "glove-01"}
  }'
```

### Example: Get Dashboard Stats

```bash
curl http://localhost:8080/dashboard/
```

---

## 🧪 Running Tests

From the `backend` directory:

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx
pytest
```

- Some async DB tests may be skipped or xfail due to Motor event loop issues on Windows.

---

## 🐞 Error Handling & Trace IDs

- All error responses include a `trace_id` field.
- If you encounter an error, provide the `trace_id` to the development team for fast debugging.

---

## 🤝 Contributing

- Pull requests are welcome!
- Please follow PEP8 for Python code and use descriptive commit messages.
- Run tests before submitting a PR.

---

## 📈 Training Visualizations & Metrics

The system now provides comprehensive training analytics:

### 📊 **Confusion Matrix**
- Heatmap visualization showing prediction accuracy per class
- Interactive table with color-coded cells
- Available as both image and interactive table

### 📈 **ROC Curves**
- Multi-class ROC curves for each gesture class
- AUC (Area Under Curve) metrics
- Micro-average ROC curve
- Interactive and static visualizations

### 📉 **Training History**
- Accuracy and loss plots over epochs
- Training vs validation metrics
- Real-time progress tracking

### 📋 **Detailed Metrics**
- Precision, Recall, F1-Score per class
- Overall accuracy and loss
- Classification report with support counts
- Performance comparison across training sessions

### 🎨 **Visualization Types**
- **Static Images**: High-quality PNG plots saved during training
- **Interactive Charts**: Real-time charts using Recharts library
- **Heatmaps**: Color-coded confusion matrices
- **Line Charts**: Training progress over epochs

---

## 🖥️ Frontend Pages

| Page              | Path             | Description                              |
|-------------------|------------------|------------------------------------------|
| Dashboard         | `/`              | Welcome panel + live stats               |
| Upload CSV        | `/upload`        | Upload CSV to train                      |
| Manage Gestures   | `/gestures`      | View, edit, delete gesture sessions      |
| Training Results  | `/training`      | View & trigger model training            |
| Predict           | `/predict`       | Manual prediction with sensor values     |
| Live Predict      | `/predict/live`  | Real-time prediction display             |
| Data History      | `/history`       | View prediction history                  |
| Admin Tools       | `/admin`         | System administration                    |

### 🎯 **Enhanced Training Results Page**
The Training Results page now features a tabbed interface:

1. **Overview Tab**: Key metrics and training progress charts
2. **Detailed Metrics Tab**: Confusion matrix and classification reports  
3. **Visualizations Tab**: Static plots and interactive charts

---

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Training a Model
1. Upload gesture data via `/upload` or `/training/upload`
2. Navigate to Training Results page
3. Click "Manual Training" or wait for auto-trigger
4. View comprehensive metrics and visualizations

---

## 📊 Performance Metrics

The system tracks and visualizes:
- **Accuracy**: Overall prediction accuracy
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)  
- **F1-Score**: Harmonic mean of precision and recall
- **AUC**: Area under ROC curve for each class
- **Confusion Matrix**: Detailed class-wise performance

---

## 🔧 Configuration

Key configuration files:
- `backend/core/config.py` - System settings
- `backend/AI/model.py` - Model architecture and training
- `frontend/src/pages/TrainingResults.jsx` - Visualization components

---

## ESP32 TTS Audio Playback (Arduino)

`t t s.ino` enables the ESP32 to receive and play TTS audio files from the backend. It no longer includes LCD display functionality.

### Required Libraries
- ESPAsyncWebServer
- ESPAsyncTCP
- ESP32-audioI2S
- FS and SPIFFS (included with ESP32 core)

### Installation Steps
1. Install ESP32 board support (see previous instructions).
2. Install the above libraries via Library Manager or GitHub.
3. Configure WiFi credentials in `arduino/tts.ino`.
4. Upload the code to your ESP32.
5. The ESP32 will start a server at `http://<ESP32_IP>/play_audio` to receive and play audio files from the backend.

---

## ESP32 LCD Display (Arduino)

`lcd_display.ino` enables the ESP32 to act as a networked LCD display, showing text sent via HTTP POST to `/display_text`.

### Required Libraries
- ESPAsyncWebServer
- ESPAsyncTCP
- LiquidCrystal_I2C

### Installation Steps
1. Install ESP32 board support (see previous instructions).
2. Install the above libraries via Library Manager or GitHub.
3. Configure WiFi credentials in `arduino/lcd_display.ino`.
4. Upload the code to your ESP32.
5. The ESP32 will start a server at `http://<ESP32_IP>/display_text` to receive and display text on the LCD.

---

You can run `tts.ino` and `lcd_display.ino` on separate ESP32 devices for audio and LCD display, or use only the one you need for your application.


