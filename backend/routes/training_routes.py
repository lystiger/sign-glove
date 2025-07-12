"""
API routes for managing model training and results in the sign glove system.

Endpoints:
- POST /training/: Save a training result manually.
- GET /training/: List all training results.
- GET /training/{session_id}: Fetch a training result by session ID.
- POST /training/run: Upload CSV, run training, and log result.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from models.model_result import ModelResult
from core.database import model_collection
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from uuid import uuid4
import logging
import subprocess
import shutil
import os

router = APIRouter(prefix="/training", tags=["Training"])

@router.post("/")
async def save_model_result(result: ModelResult):
    """
    Save a training result to the database.
    """
    try:
        res = await model_collection.insert_one(result.model_dump())
        logging.info(f"Inserted training result: {res.inserted_id}")
        return JSONResponse(status_code=201, content={
            "status": "success",
            "data": {"inserted_id": str(res.inserted_id)}
        })
    except Exception as e:
        logging.error(f"Error saving model result: {e}")
        raise HTTPException(status_code=500, detail="Failed to save model result")

@router.get("/")
async def list_model_results():
    """
    List all training results from the database.
    """
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

@router.get("/{session_id}")
async def get_model_result(session_id: str):
    """
    Fetch a training result by session ID.
    """
    try:
        result = await model_collection.find_one({"session_id": session_id})
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        result["_id"] = str(result["_id"])
        return {"status": "success", "data": result}
    except Exception as e:
        logging.error(f"Error getting model result: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch model result")

@router.post("/run")
async def run_training(file: UploadFile = File(...)):
    """
    Upload a CSV file, run the training script, and log the result.
    """
    try:
        # Save uploaded CSV as gesture_data.csv in backend/data/
        os.makedirs("backend/AI", exist_ok=True)
        file_path = "backend/data/gesture_data.csv"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run the model.py script with absolute path
        script_path = os.path.join(os.path.dirname(__file__), '..', 'AI', 'model.py')
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"Training script error: {result.stderr}")
            raise HTTPException(status_code=500, detail="Training script error")

        logging.info("Training completed successfully")
        stdout = result.stdout

        # Parse test accuracy from stdout
        acc = None
        for line in stdout.splitlines():
            if "Test accuracy" in line:
                try:
                    acc = float(line.split(":")[-1].strip())
                    break
                except ValueError:
                    continue

        if acc is None:
            raise HTTPException(status_code=500, detail="Failed to parse accuracy from output")

        # Save result using your full schema
        session_id = str(uuid4())
        training_result = ModelResult(
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            accuracy=acc,
            model_name="gesture_model.tflite",
            notes="Auto-trained via /training/run"
        )
        res = await model_collection.insert_one(training_result.model_dump())
        logging.info(f"Logged training result with ID {res.inserted_id}")

        return {
            "status": "success",
            "data": {
                "inserted_id": str(res.inserted_id),
                "session_id": session_id,
                "accuracy": acc
            }
        }

    except Exception as e:
        logging.error(f"Training run failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to run training")

@router.post("/trigger")
async def trigger_training_run():
    """
    Trigger the model training job (same as POST /training/run but without upload).
    """
    try:
        # Assumes gesture_data.csv already exists
        script_path = os.path.join(os.path.dirname(__file__), '..', 'AI', 'model.py')
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"Training script error: {result.stderr}")
            raise HTTPException(status_code=500, detail="Training script error")

        # Parse accuracy
        acc = None
        for line in result.stdout.splitlines():
            if "Test accuracy" in line:
                try:
                    acc = float(line.split(":")[-1].strip())
                    break
                except ValueError:
                    continue

        if acc is None:
            raise HTTPException(status_code=500, detail="Failed to parse accuracy")

        session_id = str(uuid4())
        training_result = ModelResult(
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            accuracy=acc,
            model_name="gesture_model.tflite",
            notes="Triggered via POST /training/trigger"
        )
        res = await model_collection.insert_one(training_result.model_dump())
        logging.info(f"Logged training result with ID {res.inserted_id}")

        return {
            "status": "success",
            "data": {
                "inserted_id": str(res.inserted_id),
                "session_id": session_id,
                "accuracy": acc
            }
        }

    except Exception as e:
        logging.error(f"Triggered training failed: {e}")
        raise HTTPException(status_code=500, detail="Training failed")