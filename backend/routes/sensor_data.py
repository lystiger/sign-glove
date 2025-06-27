from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.sensor_data import SensorData
from backend.core.database import sensor_collection
import csv
from io import StringIO
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/upload-sensor-data")
async def upload_sensor_data(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    content = await file.read()
    try:
        decoded = content.decode("utf-8")
        csv_reader = csv.reader(StringIO(decoded))
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to read CSV content.")

    session_id = str(uuid.uuid4())
    glove_id = "right"  # default, or add as parameter later

    documents = []
    for i, row in enumerate(csv_reader):
        try:
            values = list(map(float, row))
            if len(values) != 11:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Row {i+1} must contain exactly 11 numeric values.")

        documents.append({
            "session_id": session_id,
            "glove_id": glove_id,
            "timestamp": datetime.utcnow(),
            "values": values
        })

    if not documents:
        raise HTTPException(status_code=400, detail="CSV is empty or invalid.")

    await sensor_collection.insert_many(documents)
    return {"message": "Sensor data uploaded successfully", "session_id": session_id, "samples": len(documents)}
