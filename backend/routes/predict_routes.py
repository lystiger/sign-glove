from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.core.database import sensor_collection 
import numpy as np
import logging
import tensorflow as tf  # or tflite_runtime.interpreter

router = APIRouter(prefix="/predict", tags=["Prediction"])

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