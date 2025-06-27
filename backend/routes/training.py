from fastapi import APIRouter, HTTPException
from backend.models.model_result import ModelResult
from backend.core.database import model_collection

router = APIRouter()

# POST /training → Save training result
@router.post("/")
async def save_model_result(result: ModelResult):
    res = await model_collection.insert_one(result.dict())
    return {"inserted_id": str(res.inserted_id)}

# GET /training → Get all model results
@router.get("/")
async def list_model_results():
    cursor = model_collection.find()
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    return results

# GET /training/{session_id} → Get one by session_id
@router.get("/{session_id}")
async def get_model_result(session_id: str):
    result = await model_collection.find_one({"session_id": session_id})
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    result["_id"] = str(result["_id"])
    return result
