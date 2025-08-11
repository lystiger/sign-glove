"""
API routes for gesture prediction and live inference in the sign glove system.

Endpoints:
- POST /predict/: Predict gesture label from sensor input.
- GET /predict/live: Predict gesture from the latest sensor data.
- WebSocket /predict/ws/predict: Real-time prediction and auto-training trigger.
- GET /predict/predictions: List recent predictions.
"""

import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from core.database import sensor_collection, prediction_collection
from core.model import predict_from_dual_hand_data
from core.settings import settings
import numpy as np
import logging
try:
    import tensorflow as tf  # type: ignore
except Exception as _tf_exc:  # pragma: no cover
    tf = None  # type: ignore
import requests
import asyncio
from utils.cache import cacheable

router = APIRouter(prefix="/predict", tags=["Prediction"])
prediction_counts: Dict[str, int] = {}
LAST_TRAIN_COUNT: Optional[int] = None

class SensorInput(BaseModel):
    values: List[float] = Field(..., description="List of 11 sensor values")  # Expecting 11 values total

@router.post("/")
async def predict_label(input: SensorInput):
    """
    Predict gesture label from a single sensor input using a TFLite model.
    """
    # Validate input length
    if len(input.values) != 11:
        raise HTTPException(status_code=422, detail="'values' must contain exactly 11 numbers")
    
    if tf is None:
        raise HTTPException(status_code=500, detail="TensorFlow not available for prediction")
    try:
        interpreter = tf.lite.Interpreter(model_path=settings.MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        data = np.array([input.values], dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], data)
        interpreter.invoke()

        output = interpreter.get_tensor(output_details[0]['index'])
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        label = f"Class {predicted_index}"

        return {
            "status": "success",
            "prediction": label,
            "confidence": confidence
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live")
async def predict_latest():
    """
    Predict gesture from the most recent sensor data in the database.
    """
    if tf is None:
        raise HTTPException(status_code=500, detail="TensorFlow not available for prediction")
    try:
        doc = await sensor_collection.find_one(sort=[("timestamp", -1)])
        if not doc or "values" not in doc:
            raise HTTPException(status_code=404, detail="No recent sensor data found")

        values = doc["values"]
        if not isinstance(values, list) or len(values) != 11:
            raise HTTPException(status_code=422, detail="Stored 'values' must contain exactly 11 numbers")

        interpreter = tf.lite.Interpreter(model_path=settings.MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        data = np.array([values], dtype=np.float32)
        interpreter.set_tensor(input_details[0]['index'], data)
        interpreter.invoke()

        output = interpreter.get_tensor(output_details[0]['index'])
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        label = f"Class {predicted_index}"

        return {
            "status": "success",
            "prediction": label,
            "confidence": confidence,
            "source_session": doc.get("session_id", "unknown"),
            "timestamp": doc.get("timestamp")
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Live prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Live prediction error")

@router.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    """
    WebSocket endpoint for real-time gesture prediction and auto-training trigger.
    Receives sensor data as:
    {
        "flex": [5],
        "accel": [3],
        "gyro": [3],
        "timestamp": ...
    }
    """
    await websocket.accept()
    try:
        global LAST_TRAIN_COUNT
        if LAST_TRAIN_COUNT is None:
            try:
                LAST_TRAIN_COUNT = await sensor_collection.count_documents({})
            except Exception:
                LAST_TRAIN_COUNT = 0
        while True:
            data = await websocket.receive_json()

            # Build input vector (flex + accel + gyro)
            if not all(k in data for k in ["flex", "accel", "gyro"]):
                await websocket.send_json({"error": "Missing keys"})
                continue

            if len(data["flex"]) != 5 or len(data["accel"]) != 3 or len(data["gyro"]) != 3:
                await websocket.send_json({"error": "Invalid input lengths"})
                continue

            input_vector = data["flex"] + data["accel"] + data["gyro"]
            prediction = predict_from_dual_hand_data(np.array(input_vector).reshape(1, -1))

            # Save prediction
            await prediction_collection.insert_one({
                "flex": data["flex"],
                "accel": data["accel"],
                "gyro": data["gyro"],
                "timestamp": datetime.datetime.utcnow(),
                "prediction": prediction["prediction"],
                "confidence": prediction.get("confidence")
            })

            label = prediction["prediction"]
            prediction_counts[label] = prediction_counts.get(label, 0) + 1

            if prediction_counts[label] >= 10:
                await sensor_collection.insert_one({
                    "values": input_vector,
                    "label": label,
                    "source": "auto",
                    "timestamp": datetime.datetime.utcnow()
                })

                current_count = await sensor_collection.count_documents({})
                if LAST_TRAIN_COUNT is None:
                    LAST_TRAIN_COUNT = 0
                if current_count - LAST_TRAIN_COUNT >= 50:
                    try:
                        response = requests.post("http://localhost:8080/training")
                        if response.status_code == 200:
                            print("Auto-training triggered after 50 new samples.")
                            LAST_TRAIN_COUNT = current_count
                        else:
                            print("Training failed:", response.status_code, response.text)
                    except Exception as e:
                        print("Error triggering auto-training:", e)

                prediction_counts[label] = 0  # Reset counter

            await websocket.send_json(prediction)
    except WebSocketDisconnect:
        print("Client disconnected")

@router.get(
    "/predictions",
    summary="List recent predictions",
    description="Returns a list of recent predictions from the predictions collection, sorted by timestamp."
)
@cacheable(ttl=30)
async def get_predictions(limit: int = Query(100, ge=1, le=1000)) -> List[Dict[str, Any]]:
    """
    Example response:
    [
        {"_id": "...", "prediction": "hello", "timestamp": "...", ...},
        ...
    ]
    """
    cursor = prediction_collection.find().sort("timestamp", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results
