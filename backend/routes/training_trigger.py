"""
API route for triggering model training in the sign glove system.

Endpoint:
- POST /training/: Start a new training session (simulated response).
"""
from fastapi import APIRouter, status, HTTPException
from datetime import datetime, timezone
from models.training_models import TrainingRequest, TrainingResponse
from models.model_result import ModelResult
from core.database import model_collection
from uuid import uuid4
import subprocess
import logging

router = APIRouter(prefix="/training", tags=["Training"])

@router.post("/", response_model=TrainingResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_training(request: TrainingRequest):
    """
    Trigger a new model training session (runs the training script and logs the result).
    """
    try:
        # Run the model.py script
        result = subprocess.run(
            ["python", "backend/AI/model.py"],
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
            notes="Triggered via POST /training/"
        )
        res = await model_collection.insert_one(training_result.model_dump())
        logging.info(f"Logged training result with ID {res.inserted_id}")

        return TrainingResponse(
            status="training_completed",
            started_at=datetime.now(timezone.utc)
        )

    except Exception as e:
        logging.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail="Training failed")
