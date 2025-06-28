from fastapi import APIRouter, HTTPException
from backend.models.model_result import ModelResult
from backend.core.database import model_collection
from fastapi.responses import JSONResponse
import logging

router = APIRouter(prefix="/training", tags=["Training"])

# POST /training → Save training result
@router.post("/")
async def save_model_result(result: ModelResult):
    try:
        res = await model_collection.insert_one(result.dict())
        logging.info(f"Inserted training result: {res.inserted_id}")
        return JSONResponse(status_code=201, content={
            "status": "success",
            "data": {"inserted_id": str(res.inserted_id)}
        })
    except Exception as e:
        logging.error(f"Error saving model result: {e}")
        raise HTTPException(status_code=500, detail="Failed to save model result")

# GET /training → Get all model results
@router.get("/")
async def list_model_results():
    try:
        cursor = model_collection.find()
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        logging.info(f"Fetched {len(results)} training results")
        return {"status": "success", "data": results}
    except Exception as e:
        logging.error(f"Error fetching model results: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model results")

# GET /training/{session_id} → Get one by session_id
@router.get("/{session_id}")
async def get_model_result(session_id: str):
    try:
        result = await model_collection.find_one({"session_id": session_id})
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        result["_id"] = str(result["_id"])
        return {"status": "success", "data": result}
    except Exception as e:
        logging.error(f"Error getting model result: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model result")
