"""
WebSocket API for real-time gesture prediction and text-to-speech feedback in the sign glove system.
"""
import logging
import numpy as np
import asyncio
import pyttsx3
import tensorflow as tf
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError
from pathlib import Path
import json
import time

from core.settings import settings
from services.tts_service import tts_service
print("TTS Configuration:")
print(f"TTS Enabled: {settings.TTS_ENABLED}")
print(f"TTS Provider: {settings.TTS_PROVIDER}")
print(f"TTS Voice: {settings.TTS_VOICE}")
print(f"Pygame Available: {tts_service.pygame_available if hasattr(tts_service, 'pygame_available') else 'N/A'}")

# Initialize logger at module level
logger = logging.getLogger("signglove")

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Constants
SENSOR_COUNT = 11
MAX_REQUESTS_PER_MINUTE = 1000
RATE_LIMIT_SECONDS = 60

class SensorData(BaseModel):
    values: List[float]
    timestamp: float

    @validator('values')
    def validate_values(cls, v):
        if len(v) != SENSOR_COUNT:
            raise ValueError(f'Must contain exactly {SENSOR_COUNT} sensor values')
        if not all(-1000 <= val <= 1000 for val in v):  # Adjust range as needed
            raise ValueError('Sensor values out of valid range (-1000 to 1000)')
        return v

class WebSocketMessage(BaseModel):
    left: Optional[Dict[str, Union[List[float], float]]] = None
    right: Optional[Dict[str, Union[List[float], float]]] = None
    language: str = "en"
    timestamp: Optional[float] = None

    @validator('language')
    def validate_language(cls, v):
        available_languages = tts_service.get_available_languages()
        if v not in available_languages:
            logger.warning(f"Unsupported language '{v}'. Defaulting to 'en'")
            return "en"
        return v

rate_limiter = {}

@router.websocket("/predict")
async def websocket_predict(websocket: WebSocket):
    """WebSocket endpoint for real-time gesture prediction."""
    client_ip = websocket.client.host
    await websocket.accept()
    logger.info(f"WebSocket connection established with {client_ip}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Rate limiting
            current_time = time.time()
            if client_ip in rate_limiter:
                if current_time - rate_limiter[client_ip] < RATE_LIMIT_SECONDS:
                    continue
            rate_limiter[client_ip] = current_time
            
            try:
                # Parse and validate message
                message_data = json.loads(data)
                message = WebSocketMessage(**message_data)
                
                # Process single-hand data only
                await process_single_hand(websocket, message, client_ip)
                
            except ValidationError as e:
                error_msg = f"Invalid message format: {str(e)}"
                logger.error(f"{client_ip}: {error_msg}")
                await websocket.send_json({"error": error_msg, "type": "validation_error"})
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON: {str(e)}"
                logger.error(f"{client_ip}: {error_msg}")
                await websocket.send_json({"error": error_msg, "type": "json_error"})
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for {client_ip}")
        if client_ip in rate_limiter:
            del rate_limiter[client_ip]
    except Exception as e:
        logger.error(f"WebSocket error for {client_ip}: {str(e)}")
        await websocket.close()

async def process_single_hand(websocket: WebSocket, message: WebSocketMessage, client_ip: str):
    """Process single-hand gesture prediction."""
    try:
        # Get sensor data from either left or right hand
        sensor_data = None
        if message.left is not None:
            sensor_data = SensorData(**message.left)
        elif message.right is not None:
            sensor_data = SensorData(**message.right)
        else:
            error_msg = "No sensor data provided"
            logger.error(f"{client_ip}: {error_msg}")
            await websocket.send_json({"error": error_msg, "type": "validation_error"})
            return
        
        from core.model import predict_gesture
        prediction_result = predict_gesture(sensor_data.values)
        
        if prediction_result["status"] == "success":
            response = {
                "status": "success",
                "prediction": prediction_result["prediction"],
                "confidence": prediction_result["confidence"],
                "timestamp": message.timestamp or datetime.now().timestamp()
            }
            await websocket.send_json(response)
            # await handle_tts(response["prediction"], message.language, client_ip)  # Disabled - using frontend TTS instead
        else:
            logger.error(f"Prediction failed for {client_ip}: {prediction_result.get('message', 'Unknown error')}")
            await websocket.send_json({
                "error": prediction_result.get("message", "Prediction failed"),
                "type": "prediction_error"
            })
            
    except ValidationError as e:
        error_msg = f"Invalid sensor data: {str(e)}"
        logger.error(f"{client_ip}: {error_msg}")
        await websocket.send_json({"error": error_msg, "type": "validation_error"})

async def handle_tts(label: str, language: str, client_ip: str):
    """Handle text-to-speech conversion with dual output support."""
    try:
        logger.debug(f"TTS requested - Label: {label}, Language: {language}")
        
        # Check if TTS is enabled in settings
        if not settings.TTS_ENABLED:
            logger.warning(f"TTS is disabled in settings for {client_ip}")
            return {"status": "disabled", "message": "TTS is disabled in settings"}
        
        # Check if the label should be spoken
        if not tts_service.should_speak_gesture(label):
            logger.debug(f"TTS skipped for label '{label}' - not a speakable gesture")
            return {"status": "skipped", "reason": "Gesture does not require TTS"}
            
        # Get the text to speak
        text = tts_service.get_gesture_text(label, language)
        if not text:
            logger.warning(f"No translation found for label '{label}' in language '{language}'")
            return {"status": "error", "message": f"No translation for '{label}' in '{language}'"}
        
        logger.debug(f"Attempting TTS - Text: {text}, Language: {language}")
        
        # Play on both laptop and ESP32 by default
        tts_result = await tts_service.speak_gesture(
            label, 
            language=language,
            play_on_laptop=True,  # Enable laptop audio
            play_on_esp32=False   # Disable ESP32 for now to simplify debugging
        )
        
        logger.debug(f"TTS result: {tts_result}")
        
        if tts_result.get("status") == "skipped":
            logger.debug(f"TTS skipped for {client_ip}: {tts_result.get('reason', 'No reason provided')}")
        elif tts_result.get("status") != "success":
            logger.warning(f"TTS error for {client_ip}: {tts_result.get('message', 'Unknown error')}")
        
        # Log successful TTS operations
        if tts_result.get("laptop_playback") == "success":
            logger.info(f"Played TTS on laptop for {client_ip}: {tts_result.get('text', '')}")
        
        return tts_result
        
    except Exception as e:
        logger.error(f"TTS processing failed for {client_ip}: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}
