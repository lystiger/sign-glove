"""
WebSocket API for real-time gesture prediction and text-to-speech feedback in the sign glove system.

Endpoint:
- WebSocket /ws/predict: Receives sensor data, returns predictions, and speaks the result.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import numpy as np
import asyncio
import pyttsx3
import tensorflow as tf
from core.settings import settings

router = APIRouter(prefix="/ws", tags=["WebSocket"])
tts_engine = pyttsx3.init()

@router.websocket("/predict")
async def websocket_predict(websocket: WebSocket):
    """
    WebSocket endpoint for real-time gesture prediction and TTS feedback.
    Receives left/right hand data, returns prediction, and speaks the result.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            # Use left hand data for prediction (or combine if needed)
            sensor_values = data.get("left", data.get("values", []))
            
            if len(sensor_values) != 11:
                await websocket.send_json({"error": "Expected 11 sensor values"})
                continue

            # Load and use the regular model
            interpreter = tf.lite.Interpreter(model_path=settings.MODEL_PATH)
            interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()

            # Prepare input data
            input_data = np.array([sensor_values], dtype=np.float32)
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()

            # Get prediction
            output = interpreter.get_tensor(output_details[0]['index'])
            predicted_index = int(np.argmax(output))
            confidence = float(np.max(output))

            # Map to labels (A, B, C based on your sample data)
            label_map = {0: "A", 1: "B", 2: "C"}
            prediction = label_map.get(predicted_index, f"Class {predicted_index}")

            # Send to frontend
            await websocket.send_json({"prediction": prediction, "confidence": confidence})

            # Speak the prediction
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, tts_engine.say, prediction)
            loop.run_in_executor(None, tts_engine.runAndWait)

    except WebSocketDisconnect:
        print("Client disconnected")
