"""
API route for dashboard statistics in the sign glove system.

Endpoint:
- GET /dashboard/: Get summary statistics for sessions, models, accuracy, and last activity.
"""
from fastapi import APIRouter, HTTPException
from core.database import sensor_collection, model_collection
from pymongo import DESCENDING
import logging
import time

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Simple in-memory cache for dashboard stats
_dashboard_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 30  # seconds

@router.get("/")
async def get_dashboard_stats():
    now = time.time()
    if _dashboard_cache["data"] is not None and now - _dashboard_cache["timestamp"] < CACHE_TTL:
        return _dashboard_cache["data"]
    try:
        # Count total gesture sessions
        total_sessions = await sensor_collection.count_documents({})
        # Count total training results
        total_models = await model_collection.count_documents({})
        # Average accuracy
        cursor = model_collection.find({}, {"accuracy": 1})
        acc_list = [doc["accuracy"] async for doc in cursor if "accuracy" in doc]
        avg_accuracy = round(sum(acc_list) / len(acc_list), 4) if acc_list else 0.0
        # Latest timestamp from either collection
        latest_sensor = await sensor_collection.find_one(sort=[("timestamp", DESCENDING)])
        latest_model = await model_collection.find_one(sort=[("timestamp", DESCENDING)])
        latest_time = max(
            latest_sensor.get("timestamp", "") if latest_sensor else "",
            latest_model.get("timestamp", "") if latest_model else "",
        )
        result = {
            "status": "success",
            "data": {
                "total_sessions": total_sessions,
                "total_models": total_models,
                "average_accuracy": avg_accuracy,
                "last_activity": latest_time,
            }
        }
        _dashboard_cache["data"] = result
        _dashboard_cache["timestamp"] = now
        return result
    except Exception as e:
        logging.error(f"Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@router.get("")
async def get_dashboard_stats_alias():
    return await get_dashboard_stats()
