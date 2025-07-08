from core.database import sensor_collection
from datetime import datetime, timezone
import logging
from typing import Optional

def save_sensor_data(values: list[list[float]], label: Optional[str], session_id: str):
    """
    Save sensor data to the database.
    Args:
        values (list[list[float]]): List of sensor readings.
        label (Optional[str]): Gesture label, if any.
        session_id (str): Session identifier.
    """
    try:
        result = sensor_collection.insert_one({
            "sensor_values": values,
            "gesture_label": label,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc)
        })
        # Optionally log the inserted_id
        # logging.info(f"Inserted document with ID {result.inserted_id}")
    except Exception as e:
        logging.error(f"Failed to save sensor data for session {session_id} with label {label}: {e}. Data: {values}")
        raise
