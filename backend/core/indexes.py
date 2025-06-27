from pymongo import ASCENDING, DESCENDING
from .database import sensor_data_collection, model_results_collection

def create_indexes():
    # Sensor Data
    sensor_data_collection.create_index([("session_id", ASCENDING)])
    sensor_data_collection.create_index([("timestamp", DESCENDING)])
    sensor_data_collection.create_index([("session_id", ASCENDING), ("timestamp", DESCENDING)])

    # Model Results
    model_results_collection.create_index([("model_name", ASCENDING)])
    model_results_collection.create_index([("created_at", DESCENDING)])
    model_results_collection.create_index([("session_id", ASCENDING), ("model_name", ASCENDING)])
