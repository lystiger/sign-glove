from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class TrainingRequest(BaseModel):
    model_name: str = Field(..., example="LSTM_v1")
    gestures: Optional[List[str]] = Field(default=None, example=["hello", "yes", "no"])
    epochs: Optional[int] = Field(default=20, example=20)

class TrainingResponse(BaseModel):
    status: str = Field(..., example="training_started")
    started_at: datetime = Field(..., example="2025-06-27T12:00:00Z")

class TrainingSession(BaseModel):
    model_name: str
    gestures_used: List[str]
    params: Dict[str, int]  # like {"epochs": 20}
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_sec: Optional[int] = None
    notes: Optional[str] = None
