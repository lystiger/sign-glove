"""
WebSocket API for real-time gesture prediction and text-to-speech feedback in the sign glove system.

Endpoint:
- WebSocket /ws/predict: Receives sensor data, returns predictions, and speaks the result.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import numpy as np
import asyncio
import pyttsx3
import tensorflow as tf
from core.settings import settings
from services.tts_service import tts_service

router = APIRouter(prefix="/ws", tags=["WebSocket"])
tts_engine = pyttsx3.init()
logger = logging.getLogger("signglove")

@router.websocket("/predict")
async def websocket_predict(websocket: WebSocket):
    """
    WebSocket endpoint for real-time gesture prediction and TTS feedback.
    Receives left/right hand data, returns prediction, and speaks the result.
    Supports multiple languages for TTS.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            # Get language preference from client (default to English)
            language = data.get("language", "en")
            if language not in tts_service.get_available_languages():
                language = "en"  # Fallback to English

            # Check if we have dual-hand data
            left_data = data.get("left")
            right_data = data.get("right")
            
            if left_data and right_data:
                # Dual-hand prediction
                if len(left_data) != 11 or len(right_data) != 11:
                    await websocket.send_json({"error": "Expected 11 sensor values per hand"})
                    continue
                
                # Use dual-hand prediction function
                from core.model import predict_from_dual_hand_data
                prediction_result = predict_from_dual_hand_data({
                    "left": left_data,
                    "right": right_data,
                    "timestamp": data.get("timestamp")
                })
                
                if prediction_result["status"] == "success":
                    await websocket.send_json(prediction_result)
                    
                    # Selective Text-to-speech feedback with language support
                    label = prediction_result["left_prediction"]
                    tts_result = await tts_service.speak_gesture(label, language=language)
                    
                    if tts_result["status"] == "skipped":
                        logger.info(f"TTS skipped for gesture '{label}' in {language}: {tts_result['reason']}")
                    elif tts_result["status"] == "success":
                        text_spoken = tts_service.get_gesture_text(label, language)
                        logger.info(f"TTS spoke '{text_spoken}' for gesture '{label}' in {language}")
                    else:
                        logger.warning(f"TTS error for gesture '{label}' in {language}: {tts_result.get('message', 'Unknown error')}")
                        
                else:
                    await websocket.send_json({"error": prediction_result["message"]})
                    
            else:
                # Fallback to single-hand prediction
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

                # Map to labels
                label_map = {0: "Hello", 1: "Yes", 2: "No", 3: "Thanks"}
                prediction = label_map.get(predicted_index, f"Class {predicted_index}")

                # Send prediction
                prediction_result = {
                    "prediction": prediction,
                    "confidence": confidence,
                    "timestamp": data.get("timestamp"),
                    "model_type": "single_hand",
                    "language": language
                }
                await websocket.send_json(prediction_result)

                # Selective Text-to-speech feedback with language support
                tts_result = await tts_service.speak_gesture(prediction, language=language)
                
                if tts_result["status"] == "skipped":
                    logger.info(f"TTS skipped for gesture '{prediction}' in {language}: {tts_result['reason']}")
                elif tts_result["status"] == "success":
                    text_spoken = tts_service.get_gesture_text(prediction, language)
                    logger.info(f"TTS spoke '{text_spoken}' for gesture '{prediction}' in {language}")
                else:
                    logger.warning(f"TTS error for gesture '{prediction}' in {language}: {tts_result.get('message', 'Unknown error')}")

    except WebSocketDisconnect:
        logger.info("Client disconnected")
