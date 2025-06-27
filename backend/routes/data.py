from fastapi import APIRouter, Request
from backend.db.mongo import get_sensor_collection
from datetime import datetime

router = APIRouter()
collection = get_sensor_collection()

@router.post("/data")
async def receive_data(request: Request):
    payload = await request.json()
    payload["_timestamp"] = datetime.utcnow()
    result = await collection.insert_one(payload)
    return {"status": "success", "inserted_id": str(result.inserted_id)}

@router.get("/data")
async def get_data(limit: int = 10):
    items = await collection.find().sort("_timestamp", -1).to_list(length=limit)
    return items

@router.delete("/data")
async def delete_all():
    result = await collection.delete_many({})
    return {"deleted_count": result.deleted_count}
