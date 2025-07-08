"""
API route for triggering model training in the sign glove system.

Endpoint:
- POST /training/: Start a new training session (simulated response).
"""
from fastapi import APIRouter, status
from datetime import datetime, timezone
from models.training_models import TrainingRequest, TrainingResponse

router = APIRouter(prefix="/training", tags=["Training"])

@router.post("/", response_model=TrainingResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_training(request: TrainingRequest):
    """
    Trigger a new model training session (simulated response for now).
    """
    # TODO: Insert logic to trigger training script/module
    # For now, just simulate a successful start
    return TrainingResponse(
        status="training_started",
        started_at=datetime.now(timezone.utc)
    )
