"""
Async WebSocket API for real-time gesture prediction using trained AI
"""

import logging
import asyncio
import json
import time
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import tensorflow as tf

logger = logging.getLogger("signglove")
router = APIRouter(prefix="/ws", tags=["WebSocket"])

# ------------------- CONFIG -------------------
RATE_LIMIT_SECONDS = 0.03  # ~30 messages/sec per client
rate_limiter = {}

# Load TFLite model
TFLITE_MODEL_PATH = "AI/gesture_model.tflite"
interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

GESTURE_LABELS = ["Hello", "Yes", "No", "We", "Are", "Students", "Rest"]  # example labels

# ------------------- HELPERS -------------------
def preprocess_sensor_data(sensor_values):
    if len(sensor_values) != 11:
        raise ValueError(f"Expected 11 features, got {len(sensor_values)}")
    x = np.array(sensor_values, dtype=np.float32).reshape(1, 11)
    # Normalize flex sensors 0-1023
    for i in range(5):
        x[0, i] /= 1023.0
    return x

def predict_gesture(sensor_values):
    x = preprocess_sensor_data(sensor_values)
    interpreter.set_tensor(input_details[0]['index'], x)
    interpreter.invoke()
    y_pred = interpreter.get_tensor(output_details[0]['index'])[0]
    pred_index = int(np.argmax(y_pred))
    pred_label = GESTURE_LABELS[pred_index]
    confidence = float(y_pred[pred_index])
    return pred_label, confidence

# Async wrapper to avoid blocking event loop
async def predict_gesture_async(sensor_values):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, predict_gesture, sensor_values)

# ------------------- WEBSOCKET ENDPOINT -------------------
@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    client_ip = websocket.client.host
    await websocket.accept()
    logger.info(f"WebSocket connected: {client_ip}")

    try:
        while True:
            data_text = await websocket.receive_text()

            # Rate limiting
            now = time.time()
            last_time = rate_limiter.get(client_ip, 0)
            if now - last_time < RATE_LIMIT_SECONDS:
                continue
            rate_limiter[client_ip] = now

            try:
                payload = json.loads(data_text)
                sensor_values = payload.get("right", [])

                if not sensor_values or len(sensor_values) != 11:
                    await websocket.send_json({"error": "Invalid sensor data"})
                    continue

                # --- Async prediction ---
                prediction, confidence = await predict_gesture_async(sensor_values)

                response = {
                    "timestamp": payload.get("timestamp", time.time()),
                    "prediction": prediction,
                    "confidence": confidence
                }

                await websocket.send_json(response)

            except json.JSONDecodeError:
                logger.warning(f"{client_ip}: invalid JSON received")
            except Exception as e:
                logger.error(f"{client_ip}: streaming error: {e}")
                await websocket.send_json({"error": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_ip}")
        rate_limiter.pop(client_ip, None)
    except Exception as e:
        logger.error(f"WebSocket error ({client_ip}): {e}")
        await websocket.close()
