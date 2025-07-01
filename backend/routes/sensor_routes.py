from fastapi import APIRouter, HTTPException, Query
from backend.models.sensor_models import SensorData
from backend.core.database import sensor_collection
from bson import ObjectId
from typing import List
from fastapi.encoders import jsonable_encoder

router = APIRouter()

# Helper to convert Mongo _id to str
def convert_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# Create sensor data
@router.post("/sensor-data")
async def create_sensor_data(data: SensorData):
    try:
        result = await sensor_collection.insert_one(data.model_dump())
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Read all sensor data (optionally by label)
@router.get("/sensor-data", response_model=List[SensorData])
async def get_sensor_data(label: str = Query(None)):
    try:
        query = {"label": label} if label else {}
        cursor = sensor_collection.find(query)
        docs = [convert_id(doc) async for doc in cursor]
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update label for a session_id
@router.put("/sensor-data/{session_id}")
async def update_sensor_label(session_id: str, label: str = Query(...)):
    try:
        result = await sensor_collection.update_one(
            {"session_id": session_id},
            {"$set": {"label": label}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Label updated", "modified_count": result.modified_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete sensor data by session_id
@router.delete("/sensor-data/{session_id}")
async def delete_sensor_data(session_id: str):
    try:
        result = await sensor_collection.delete_one({"session_id": session_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Sensor data deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
