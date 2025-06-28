from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DeviceInfo(BaseModel):
    source: str  # e.g., "USB", "WiFi"
    device_id: Optional[str] = None

class SensorData(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc123",
                "timestamp": "2025-06-27T12:00:00Z",
                "sensor_values": [[0.1]*11, [0.2]*11, [0.3]*11],
                "gesture_label": "hello",
                "device_info": {
                "source": "USB",
                "device_id": "glove-01"
                }
            }       
        }

    session_id: str = Field(..., description="Unique session identifier")
    timestamp: datetime = Field(..., description="ISO-formatted timestamp")
    sensor_values: List[List[float]] = Field(..., description="List of [11] sensor values per sample")
    gesture_label: Optional[str] = Field(None, description="Optional gesture label for supervised training")
    device_info: DeviceInfo = Field(..., description="Information about the device (e.g., source: USB/WiFi)")

