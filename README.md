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

## Frontend Buttons: Functions and Use Cases

### 1. Manual Training Features

- **Manual Training Button**
  - **Function:** Triggers model training on demand using the current cleaned data (`gesture_data.csv`).
  - **Use Case:** Use after collecting new data, cleaning up, or experimenting with different datasets.

- **Upload CSV Button**
  - **Function:** Uploads a CSV file containing gesture data to the backend.
  - **Use Case:** Import data from other devices, collaborators, or re-upload previous data for retraining or analysis. Can be raw or cleaned data.

- **Upload Gesture Training Button**
  - **Function:** Uploads a pre-trained model file (e.g., `.tflite`) for live prediction.
  - **Use Case:** Deploy a model trained offline, revert to a previous model, or test different models for accuracy/performance.

### 2. Automatic Training Features

- **Automated Training (No Button)**
  - **Function:** The backend automatically monitors for new data, runs noise reduction, and triggers training at regular intervals or when new data is detected.
  - **Use Case:** Keeps the model up-to-date as new data is collected, requiring no manual intervention.

- **Live Prediction and TTS**
  - **Function:** The frontend displays live predictions and can convert them to speech automatically or with a button.
  - **Use Case:** See and/or hear the AI’s predictions in real time as gestures are performed.

#### Summary Table

| Button/Feature             | Type         | Function/Use Case                                                                 |
|----------------------------|--------------|-----------------------------------------------------------------------------------|
| **Manual Training**        | Manual       | User triggers model training on demand                                            |
| **Upload CSV**             | Manual       | User uploads gesture data for training or analysis                                |
| **Upload Gesture Training**| Manual       | User uploads a pre-trained model for live prediction                              |
| **Automated Training**     | Automatic    | Backend retrains model automatically when new data is detected                    |
| **Live Prediction & TTS**  | Both         | Shows predictions and speaks them, either automatically or on user request        |

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