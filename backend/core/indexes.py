from core.database import (
    sensor_collection,
    model_collection,
    gesture_collection,
    training_collection
)

async def create_indexes():
    # Sensor data
    await sensor_collection.create_index("session_id")
    await sensor_collection.create_index("gesture_label")
    await sensor_collection.create_index("timestamp")

    # Model results
    await model_collection.create_index("model_name")

    # Training sessions
    await training_collection.create_index("model_name")
    await training_collection.create_index("started_at")

    # Gestures (optional — only if needed)
    await gesture_collection.create_index("session_id")
    await gesture_collection.create_index("label")
