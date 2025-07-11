"""
API routes for managing gesture sensor data in the sign glove system.

Endpoints:
- GET /export: Export all gesture data as CSV.
- GET /gestures: List all gesture sessions.
- GET /gestures/{session_id}: Get data for a specific session.
- POST /: Insert new sensor data.
- PUT /{session_id}: Update gesture label for a session.
- DELETE /{session_id}: Delete session data.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models.sensor_models import SensorData
from core.database import sensor_collection
from datetime import datetime, timezone
import logging
import csv
import io


router = APIRouter()

@router.get("/export")
async def export_gestures():
    """
    Export all gesture data as a CSV file for download.
    """
    cursor = sensor_collection.find({}, {"_id": 0})
    rows = [doc async for doc in cursor]

    if not rows:
        raise HTTPException(status_code=404, detail="No gesture data found")

    # Prepare CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([f"flexSensor{i+1}" for i in range(11)] + ["label", "source", "timestamp"])

    for row in rows:
        values = row.get("values", [])
        label = row.get("label", "")
        source = row.get("source", "")
        ts = row.get("timestamp", "")
        writer.writerow(values + [label, source, ts])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=gesture_data.csv"
    })

@router.get("/gestures")
async def list_gestures():
    """
    List all gesture sessions with session_id and gesture_label.
    """
    cursor = sensor_collection.find({}, {"_id": 0, "session_id": 1, "gesture_label": 1})
    gestures = await cursor.to_list(length=1000)
    return {
        "status": "success",
        "data": gestures,
        "message": "All gestures retrieved"
    }

@router.get("/{session_id}")
async def get_sensor_data(session_id: str):
    """
    Get sensor data for a specific session by session_id.
    """
    data = await sensor_collection.find_one({"session_id": session_id})
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    data["_id"] = str(data["_id"])
    return {
        "status": "success",
        "data": data,
        "message": "Session data retrieved"
    }

@router.post("/")
async def create_sensor_data(data: SensorData):
    """
    Insert new sensor data into the database.
    """
    doc = data.dict()
    doc["_timestamp"] = datetime.now(timezone.utc)
    result = await sensor_collection.insert_one(doc)
    logging.info(f"Sensor data inserted: session={data.session_id}")
    return {
        "status": "success",
        "data": {"inserted_id": str(result.inserted_id)},
        "message": "Sensor data inserted"
    }

@router.put("/{session_id}")
async def update_label(session_id: str, label: str):
    """
    Update the gesture label for a specific session.
    """
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

@router.delete("/{session_id}")
async def delete_sensor_data(session_id: str):
    """
    Delete sensor data for a specific session by session_id.
    """
    result = await sensor_collection.delete_one({"session_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    logging.info(f"Deleted session: {session_id}")
    return {
        "status": "success",
        "data": {"deleted": result.deleted_count},
        "message": "Session deleted"
    }
