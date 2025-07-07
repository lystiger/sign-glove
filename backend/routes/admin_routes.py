from fastapi import APIRouter, HTTPException
from core.database import sensor_collection, model_collection
import logging

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.delete("/sensor-data")
async def clear_sensor_data():
    try:
        result = await sensor_collection.delete_many({})
        logging.info(f"Deleted {result.deleted_count} sensor documents")
        return {"status": "success", "deleted": result.deleted_count}
    except Exception as e:
        logging.error(f"Failed to clear sensor data: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear sensor data")

@router.delete("/training-results")
async def clear_training_results():
    try:
        result = await model_collection.delete_many({})
        logging.info(f"Deleted {result.deleted_count} training results")
        return {"status": "success", "deleted": result.deleted_count}
    except Exception as e:
        logging.error(f"Failed to clear training results: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear training results")
