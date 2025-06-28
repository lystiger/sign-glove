from fastapi import APIRouter, HTTPException
from backend.models.sensor_models import SensorData
from backend.core.database import sensor_collection
from datetime import datetime
import logging

router = APIRouter()

# 🔹 POST /gestures → Insert new sensor data
@router.post("/")
async def create_sensor_data(data: SensorData):
    doc = data.dict()
    doc["_timestamp"] = datetime.utcnow()
    result = await sensor_collection.insert_one(doc)
    logging.info(f"Sensor data inserted: session={data.session_id}")
    return {
        "status": "success",
        "data": {"inserted_id": str(result.inserted_id)},
        "message": "Sensor data inserted"
    }

# 🔹 GET /gestures/{session_id}
@router.get("/{session_id}")
async def get_sensor_data(session_id: str):
    data = await sensor_collection.find_one({"session_id": session_id})
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    data["_id"] = str(data["_id"])
    return {
        "status": "success",
        "data": data,
        "message": "Session data retrieved"
    }

# 🔹 PUT /gestures/{session_id}?label=X
@router.put("/{session_id}")
async def update_label(session_id: str, label: str):
    result = await sensor_collection.update_one(
        {"session_id": session_id},
        {"$set": {"gesture_label": label}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    logging.info(f"Label updated for session {session_id} to '{label}'")
    return {
        "status": "success",
        "data": {"updated": result.modified_count},
        "message": "Gesture label updated"
    }

# 🔹 DELETE /gestures/{session_id}
@router.delete("/{session_id}")
async def delete_sensor_data(session_id: str):
    result = await sensor_collection.delete_one({"session_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    logging.info(f"Deleted session: {session_id}")
    return {
        "status": "success",
        "data": {"deleted": result.deleted_count},
        "message": "Session deleted"
    }
