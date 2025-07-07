from core.database import sensor_collection
from datetime import datetime, timezone

def save_sensor_data(values: list, label: str, session_id: str):
    sensor_collection.insert_one({
        "values": values,
        "label": label,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc)
    })
