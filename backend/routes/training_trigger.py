from fastapi import APIRouter, status
from datetime import datetime, timezone
from models.training_models import TrainingRequest, TrainingResponse

router = APIRouter(prefix="/training", tags=["Training"])

@router.post("/", response_model=TrainingResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_training(request: TrainingRequest):
    # TODO: Insert logic to trigger training script/module
    # For now, just simulate a successful start
    return TrainingResponse(
        status="training_started",
        started_at=datetime.now(timezone.utc)
    )
