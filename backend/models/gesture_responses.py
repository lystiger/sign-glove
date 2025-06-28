from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class GestureSample(BaseModel):
    flex_values: List[int]
    imu_values: List[float]

class GestureUpload(BaseModel):
    session_id: str
    label: str
    samples: List[GestureSample]
    timestamp: datetime
