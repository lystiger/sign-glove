"""
WebSocket API for real-time gesture prediction and text-to-speech feedback in the sign glove system.

Endpoint:
- WebSocket /ws/predict: Receives dual-hand sensor data, returns predictions, and speaks the result.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.model import predict_from_dual_hand_data
import numpy as np
import asyncio
import pyttsx3

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

            # Combine left and right into a single feature vector
            left = np.array(data["left"])
            right = np.array(data["right"])
            # combined = np.concatenate((left, right)).reshape(1, -1)

            # Predict full word or letter
            prediction = predict_from_dual_hand_data({"left": left.tolist(), "right": right.tolist(), "timestamp": data.get("timestamp")})  # returns a string, e.g. "Care"

            # Send to frontend
            await websocket.send_json({"prediction": prediction})

            # Speak the prediction
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, tts_engine.say, prediction)
            loop.run_in_executor(None, tts_engine.runAndWait)

    except WebSocketDisconnect:
        print("Client disconnected")
