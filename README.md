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

## 🖥️ Frontend Pages

| Page              | Path             | Description                              |
|-------------------|------------------|------------------------------------------|
| Dashboard         | `/`              | Welcome panel + live stats               |
| Upload CSV        | `/upload`        | Upload CSV to train                      |
| Manage Gestures   | `/gestures`      | View, edit, delete gesture sessions      |
| Training Results  | `/training`      | View & trigger model training            |
| Predict           | `/predict`       | Manual input of 11 values                |
| Live Predict      | `/predict/live`  | Predict continuously from MongoDB        |
| Admin Tools       | `/admin`         | Clear/reset sensor & model data          |

---

## 🗂️ Project Structure

/backend/
├── routes/
│ ├── sensor_routes.py
│ ├── gesture_routes.py
│ ├── training_routes.py
│ ├── predict_routes.py
│ ├── admin_routes.py
│ └── dashboard_routes.py
├── models/
│ ├── sensor_data.py
│ └── model_result.py
├── core/
│ └── database.py
├── data/
│ └── gesture_data.csv ← for training
└── AI/
└── gesture_model.tflite ← trained model

/frontend/
├── components/
│ ├── Dashboard.jsx
│ ├── UploadCSV.jsx
│ ├── ManageGestures.jsx
│ ├── TrainingResults.jsx
│ ├── Predict.jsx
│ ├── LivePredict.jsx
│ └── AdminTools.jsx
├── App.jsx
└── main.jsx