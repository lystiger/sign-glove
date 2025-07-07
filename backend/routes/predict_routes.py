import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel
from typing import List
from core.database import sensor_collection, prediction_collection
from core.model import predict_from_dual_hand_data
import numpy as np
import logging
import tensorflow as tf  # or tflite_runtime.interpreter
import requests
import asyncio


router = APIRouter(prefix="/predict", tags=["Prediction"])
prediction_counts = {}
try:
    LAST_TRAIN_COUNT = asyncio.get_event_loop().run_until_complete(
        sensor_collection.count_documents({})
    )
except:
    LAST_TRAIN_COUNT = 0

class SensorInput(BaseModel):
    values: List[float]  # length should be 11 for your glove

@router.post("/")
async def predict_label(input: SensorInput):
    try:
        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path="backend/AI/gesture_model.tflite")
        interpreter.allocate_tensors()

        # Get input/output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Prepare input
        data = np.array([input.values], dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], data)
        interpreter.invoke()

        # Get prediction
        output = interpreter.get_tensor(output_details[0]['index'])
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        # Dummy label map (you can load this from a file)
        label_map = {0: "Hello", 1: "Thanks", 2: "Yes", 3: "No"}
        label = label_map.get(predicted_index, f"Class {predicted_index}")

        return {
            "status": "success",
            "prediction": label,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live")
async def predict_latest():
    try:
        # Get the most recent document from sensor_data
        doc = await sensor_collection.find_one(sort=[("timestamp", -1)])
        if not doc or "values" not in doc:
            raise HTTPException(status_code=404, detail="No recent sensor data found")

        values = doc["values"]

        # Same model prediction logic
        interpreter = tf.lite.Interpreter(model_path="backend/AI/gesture_model.tflite")
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        data = np.array([values], dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], data)
        interpreter.invoke()

        output = interpreter.get_tensor(output_details[0]['index'])
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        label_map = {0: "Hello", 1: "Yes", 2: "No", 3: "Thanks"}  # Adjust this
        label = label_map.get(predicted_index, f"Class {predicted_index}")

        return {
            "status": "success",
            "prediction": label,
            "confidence": confidence,
            "source_session": doc.get("session_id", "unknown"),
            "timestamp": doc.get("timestamp")
        }

    except Exception as e:
        logging.error(f"Live prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Live prediction error")
    
@router.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            prediction = predict_from_dual_hand_data(data)

            # Save to predictions collection
            await prediction_collection.insert_one({
                "left": data.get("left"),
                "right": data.get("right"),
                "imu": data.get("imu"),
                "timestamp": datetime.utcnow(),
                "prediction": prediction["prediction"],
                "confidence": prediction.get("confidence", None)
            })

            label = prediction["prediction"]
            prediction_counts[label] = prediction_counts.get(label, 0) + 1

            if prediction_counts[label] >= 10:  # Seen 10x, reinforce it
                await sensor_collection.insert_one({
                    "values": data["left"] + data["right"] + [data.get("imu", 0)],
                    "label": label,
                    "source": "auto",
                    "timestamp": datetime.utcnow()
                })
                    # === Auto-training trigger ===
                current_count = await sensor_collection.count_documents({})
                global LAST_TRAIN_COUNT
                if current_count - LAST_TRAIN_COUNT >= 50:
                    try:
                        response = requests.post("http://localhost:8080/training")
                        if response.status_code == 200:
                            print("✅ Auto-training triggered after 50 new samples.")
                            LAST_TRAIN_COUNT = current_count
                        else:
                            print("❌ Training failed:", response.status_code, response.text)
                    except Exception as e:
                        print("🚨 Error triggering auto-training:", e)

                prediction_counts[label] = 0  # Reset count

            await websocket.send_json(prediction)
    except WebSocketDisconnect:
        print("Client disconnected")

@router.get("/predictions")
async def get_predictions(limit: int = Query(100, ge=1, le=1000)):
    cursor = prediction_collection.find().sort("timestamp", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for frontend
        results.append(doc)
    return results