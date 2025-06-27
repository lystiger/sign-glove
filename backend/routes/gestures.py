from fastapi import APIRouter, HTTPException
from backend.models.sensor_data import SensorData
from backend.core.database import sensor_collection

router = APIRouter()

# 🔹 POST /gestures → Insert new sensor data
@router.post("/")
async def create_sensor_data(data: SensorData):
    result = await sensor_collection.insert_one(data.dict())
    return {"inserted_id": str(result.inserted_id)}

# 🔹 GET /gestures/{session_id} → Fetch data by session_id
@router.get("/{session_id}")
async def get_sensor_data(session_id: str):
    data = await sensor_collection.find_one({"session_id": session_id})
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    data["_id"] = str(data["_id"])  # ObjectId → str
    return data

# 🔹 PUT /gestures/{session_id}?label=X → Update label
@router.put("/{session_id}")
async def update_label(session_id: str, label: str):
    result = await sensor_collection.update_one(
        {"session_id": session_id},
        {"$set": {"gesture_label": label}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"updated": result.modified_count}

# 🔹 DELETE /gestures/{session_id} → Delete session
@router.delete("/{session_id}")
async def delete_sensor_data(session_id: str):
    result = await sensor_collection.delete_one({"session_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": result.deleted_count}
