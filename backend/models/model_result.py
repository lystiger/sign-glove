 # Pydantic schema for model results

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ModelResult(BaseModel):
    session_id: str = Field(..., description="Training session ID")
    timestamp: datetime = Field(..., description="When training occurred")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Model accuracy (0.0 to 1.0)")
    model_name: Optional[str] = Field(None, description="Name of the model used")
    notes: Optional[str] = Field(None, description="Optional training notes")
