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
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from models.sensor_models import SensorData
from core.database import sensor_collection
from datetime import datetime, timezone
import logging
import csv
import io
from utils.cache import cacheable, get_or_set_cache
from typing import List, Dict, Any
from routes.auth_routes import role_required_dep

logger = logging.getLogger("signglove")

router = APIRouter(prefix="/gestures", tags=["Gestures"])

def get_trace_id(request: Request):
    return request.headers.get("x-trace-id", "none")

@router.get(
    "/export",
    summary="Export all gesture data as CSV",
    description="Download all gesture data in CSV format for analysis or backup."
)
async def export_gestures(request: Request):
    """
    Returns a CSV file with all gesture data.
    Example: flexSensor1,flexSensor2,...,label,source,timestamp
    """
    def fetch_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([f"flexSensor{i+1}" for i in range(11)] + ["label", "source", "timestamp"])
        return output.getvalue()
    cached_csv = get_or_set_cache("gestures_export_csv", lambda: None, ttl=30)
    if cached_csv:
        logger.info(f"[trace={get_trace_id(request)}] Served cached gesture export CSV.")
        output = io.StringIO(cached_csv)
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=gesture_data.csv"
        })
    cursor = sensor_collection.find({}, {"_id": 0})
    rows = [doc async for doc in cursor]
    if not rows:
        logger.warning(f"[trace={get_trace_id(request)}] No gesture data found for export.")
        raise HTTPException(status_code=404, detail="No gesture data found")
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
    logger.info(f"[trace={get_trace_id(request)}] Exported {len(rows)} gesture rows.")
    from utils.cache import cache
    cache.set("gestures_export_csv", output.getvalue(), 30)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=gesture_data.csv"
    })

@router.get(
    "",
    summary="List all gesture sessions",
    description="Returns a list of all gesture sessions with session_id and gesture_label."
)
@router.get(
    "/",
    summary="List all gesture sessions (alias with trailing slash)",
    description="Returns a list of all gesture sessions with session_id and gesture_label."
)
@cacheable(ttl=30)
async def list_gestures(request: Request) -> Dict[str, Any]:
    """
    Example response:
    {
        "status": "success",
        "data": [
            {"session_id": "abc123", "gesture_label": "hello"},
            ...
        ],
        "message": "All gestures retrieved"
    }
    """
    trace_id = get_trace_id(request)
    cursor = sensor_collection.find({}, {"_id": 0, "session_id": 1, "gesture_label": 1})
    gestures = await cursor.to_list(length=1000)
    logger.info(f"[trace={trace_id}] Listed {len(gestures)} gestures.")
    return {
        "status": "success",
        "data": gestures,
        "message": "All gestures retrieved"
    }

@router.get(
    "/{session_id}",
    summary="Get sensor data for a session",
    description="Fetch all sensor data for a specific session by session_id."
)
@cacheable(ttl=30)
async def get_sensor_data(session_id: str, request: Request) -> Dict[str, Any]:
    """
    Example response:
    {
        "status": "success",
        "data": { ... },
        "message": "Session data retrieved"
    }
    """
    trace_id = get_trace_id(request)
    data = await sensor_collection.find_one({"session_id": session_id})
    if not data:
        logger.warning(f"[trace={trace_id}] Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    data["_id"] = str(data["_id"])
    logger.info(f"[trace={trace_id}] Retrieved session: {session_id}")
    return {
        "status": "success",
        "data": data,
        "message": "Session data retrieved"
    }

@router.post(
    "",
    summary="Insert new sensor data",
    description="Insert a new batch of sensor data into the database."
)
<<<<<<< HEAD
@router.post(
    "/",
    summary="Insert new sensor data (alias with trailing slash)",
    description="Insert a new batch of sensor data into the database."
)
async def create_sensor_data(data: SensorData, request: Request) -> Dict[str, Any]:
=======
async def create_sensor_data(data: SensorData, request: Request, _user=Depends(role_required_dep("editor"))) -> Dict[str, Any]:
>>>>>>> 9de1e983acf572c97ba2cb123b7d2f0bd6cc1985
    """
    Example response:
    {
        "status": "success",
        "data": {"inserted_id": "..."},
        "message": "Sensor data inserted",
        "trace_id": "..."
    }
    """
    trace_id = get_trace_id(request)
    doc = data.dict()
    doc["_timestamp"] = datetime.now(timezone.utc)
    result = await sensor_collection.insert_one(doc)
    logger.info(f"[trace={trace_id}] Sensor data inserted: session={data.session_id}")
    return {
        "status": "success",
        "session_id": data.session_id,
        "data": {"inserted_id": str(result.inserted_id)},
        "message": "Sensor data inserted",
        "trace_id": trace_id
    }

@router.put(
    "/{session_id}",
    summary="Update gesture label for a session",
    description="Update the gesture label for a specific session by session_id."
)
async def update_label(session_id: str, label: str, request: Request, _user=Depends(role_required_dep("editor"))) -> Dict[str, Any]:
    """
    Example response:
    {
        "status": "success",
        "data": {"updated": 1},
        "message": "Gesture label updated",
        "trace_id": "..."
    }
    """
    trace_id = get_trace_id(request)
    result = await sensor_collection.update_one(
        {"session_id": session_id},
        {"$set": {"gesture_label": label}}
    )
    if result.matched_count == 0:
        logger.warning(f"[trace={trace_id}] Session not found for update: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    logger.info(f"[trace={trace_id}] Label updated for session {session_id} to '{label}'")
    return {
        "status": "success",
        "data": {"updated": result.modified_count},
        "message": "Gesture label updated",
        "trace_id": trace_id
    }

@router.delete(
    "/{session_id}",
    summary="Delete sensor data for a session",
    description="Delete all sensor data for a specific session by session_id."
)
async def delete_sensor_data(session_id: str, request: Request, _user=Depends(role_required_dep("editor"))) -> Dict[str, Any]:
    """
    Example response:
    {
        "status": "success",
        "data": {"deleted": 1},
        "message": "Session deleted",
        "trace_id": "..."
    }
    """
    trace_id = get_trace_id(request)
    result = await sensor_collection.delete_one({"session_id": session_id})
    if result.deleted_count == 0:
        logger.warning(f"[trace={trace_id}] Session not found for delete: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    logger.info(f"[trace={trace_id}] Deleted session: {session_id}")
    return {
        "status": "success",
        "data": {"deleted": result.deleted_count},
        "message": "Session deleted",
        "trace_id": trace_id
    }
