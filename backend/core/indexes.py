from pymongo import ASCENDING, DESCENDING
from backend.core.database import sensor_collection, model_collection

async def create_indexes():
    # Sensor Data
    await sensor_collection.create_index([("session_id", ASCENDING)])
    await sensor_collection.create_index([("timestamp", DESCENDING)])
    await sensor_collection.create_index([("session_id", ASCENDING), ("timestamp", DESCENDING)])

    # Model Results
    await model_collection.create_index([("model_name", ASCENDING)])
    await model_collection.create_index([("created_at", DESCENDING)])
    await model_collection.create_index([("session_id", ASCENDING), ("model_name", ASCENDING)])
