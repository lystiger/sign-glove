from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from core.database import db

router = APIRouter(prefix="/utils", tags=["Utilities"])

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Sign Glove API is running"}

@router.get("/db/stats")
async def db_stats():
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
    result = await db["sensor_data"].delete_many({"timestamp": {"$lt": before}})
    return {"deleted_count": result.deleted_count}
