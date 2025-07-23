"""
API routes for utility operations in the sign glove system.

Endpoints:
- GET /utils/health: Health check for the API.
- GET /utils/db/stats: Get database statistics.
- DELETE /utils/sensor-data: Delete sensor data before a given timestamp.
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from core.database import db
from core.settings import settings
import requests
from services.tts_service import tts_service
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter(prefix="/utils", tags=["Utilities"])

class TTSRequest(BaseModel):
    text: str

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok", "message": "Sign Glove API is running"}

@router.get("/db/stats")
async def db_stats():
    """
    Get statistics for all main collections in the database.
    """
    sensor_count = await db["sensor_data"].count_documents({})
    gesture_count = await db["gestures"].count_documents({})
    model_count = await db["model_results"].count_documents({})
    training_sessions = await db["training_sessions"].count_documents({})

    return {
        "sensor_data_count": sensor_count,
        "gesture_count": gesture_count,
        "model_results_count": model_count,
        "training_sessions_count": training_sessions,
    }

@router.delete("/sensor-data")
async def delete_old_sensor_data(before: datetime = Query(..., description="Delete data before this timestamp (UTC)")):
    """
    Delete sensor data with a timestamp older than the specified value.
    """
    result = await db["sensor_data"].delete_many({"timestamp": {"$lt": before}})
    return {"deleted_count": result.deleted_count}

@router.post("/test_tts_to_esp32")
async def test_tts_to_esp32(req: TTSRequest):
    """
    Generate TTS audio for the given text and send it to the ESP32 for playback.
    """
    try:
        tts_result = await tts_service.speak(req.text)
        audio_path = tts_result.get("audio_path")
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="TTS audio file not found.")
        with open(audio_path, "rb") as f:
            files = {"file": ("audio.mp3", f, "audio/mpeg")}
            try:
                url = f"http://{settings.ESP32_IP}/play_audio"
                response = requests.post(url, files=files, timeout=5)
                return {
                    "status": "sent",
                    "esp32_status": response.status_code,
                    "esp32_response": response.text
                }
            except Exception as e:
                raise HTTPException(status_code=502, detail=f"Failed to send audio to ESP32: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS or send error: {e}")
