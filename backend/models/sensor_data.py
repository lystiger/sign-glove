 # Pydantic schema for sensor data

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SensorData(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    timestamp: datetime = Field(..., description="ISO-formatted timestamp")
    sensor_values: List[List[float]] = Field(..., description="List of [11] sensor values per sample")
    gesture_label: Optional[str] = Field(None, description="Optional gesture label for supervised training")
    device_info: dict = Field(..., description="Information about the device (e.g., source: USB/WiFi)")
