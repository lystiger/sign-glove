from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.sensor_models import SensorData
from backend.core.database import sensor_collection
from pydantic import BaseModel
from typing import List
import csv
from io import StringIO
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class UploadResponse(BaseModel):
    message: str
    session_id: str
    samples: int

class SensorData(BaseModel):
    sensor_id: str
    values: list[float]

@router.post("/")
async def add_sensor_data(data: SensorData):
    return {"message": "Data received", "data": data}

def parse_sensor_csv(content: str, session_id: str, glove_id: str) -> List[dict]:
    csv_reader = csv.reader(StringIO(content))
    documents = []
    for i, row in enumerate(csv_reader):
        try:
            values = list(map(float, row))
            if len(values) != 11:
                raise ValueError
        except ValueError:
            logger.error(f"Row {i+1} is invalid: {row}")
            raise HTTPException(status_code=400, detail=f"Row {i+1} must contain exactly 11 numeric values.")

        documents.append({
            "session_id": session_id,
            "glove_id": glove_id,
            "timestamp": datetime.now(timezone.utc),
            "values": values
        })
    return documents

@router.post("/upload-sensor-data", response_model=UploadResponse, summary="Upload CSV Sensor Data")
async def upload_sensor_data(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    glove_id = "right"  # This can be extended to come from metadata

    logger.info(f"Received file '{file.filename}' for upload. Generated session_id: {session_id}")

    if not file.filename.endswith(".csv"):
        logger.warning("Upload rejected: not a CSV file")
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    try:
        content = (await file.read()).decode("utf-8")
        documents = parse_sensor_csv(content, session_id, glove_id)

        if not documents:
            logger.warning("Upload failed: empty or invalid CSV")
            raise HTTPException(status_code=400, detail="CSV is empty or invalid.")

        await sensor_collection.insert_many(documents)
        logger.info(f"Successfully inserted {len(documents)} sensor records for session {session_id}")

        return UploadResponse(
            message="Sensor data uploaded successfully",
            session_id=session_id,
            samples=len(documents)
        )

    except HTTPException as e:
        logger.warning(f"HTTPException during upload: {e.detail}")
        raise e
    except Exception as e:
        logger.exception("Unexpected error during CSV upload")
        raise HTTPException(status_code=500, detail="Internal server error while processing CSV.")
