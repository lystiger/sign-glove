"""
Utility for importing sensor data from a CSV file into the MongoDB database for the sign glove system.

- import_csv: Reads a CSV file, parses sensor values, and inserts them as a session document in MongoDB.
"""
import csv
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging
from typing import Optional

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["sign_glove_db"]
sensor_collection = db["sensor_data"]

def import_csv(file_path: str, session_id: str, label: Optional[str] = None, source="csv"):
    """
    Import sensor data from a CSV file and insert it into the MongoDB collection.

    Args:
        file_path (str): Path to the CSV file.
        session_id (str): Unique session identifier for the data.
        label (Optional[str]): Optional gesture label for the session.
        source (str): Source of the data (default: 'csv').

    Raises:
        Exception: If reading/parsing the CSV or inserting into MongoDB fails.
    """
    sensor_rows = []
    try:
        with open(file_path, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                # Parse 11 float values
                values = list(map(float, row[:11]))
                sensor_rows.append(values)
    except Exception as e:
        logging.error(f"Failed to read or parse CSV file: {e}")
        raise
    document = {
        "_id": ObjectId(),
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc),
        "sensor_values": sensor_rows,
        "gesture_label": label,
        "device_info": {
            "source": source
        }
    }
    try:
        result = sensor_collection.insert_one(document)
        print(f"Inserted session {session_id} with ID {result.inserted_id}")
    except Exception as e:
        logging.error(f"Failed to insert document into MongoDB: {e}")
        raise

if __name__ == "__main__":
    import_csv(
        file_path="backend/data/test_data.csv",
        session_id="test_session_1",
        label="TEST"
    )
