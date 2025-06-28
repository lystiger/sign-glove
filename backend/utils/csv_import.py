import csv
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["sign_glove_db"]
sensor_collection = db["sensor_data"]

def import_csv(file_path: str, session_id: str, label: str = None, source="csv"):
    sensor_rows = []

    with open(file_path, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            # Parse 11 float values
            values = list(map(float, row[:11]))

            sensor_rows.append(values)

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

    result = sensor_collection.insert_one(document)
    print(f"Inserted session {session_id} with ID {result.inserted_id}")   

    if __name__ == "__main__":
        import_csv(
            file_path="backend/data/test_data.csv",
            session_id="test_session_1",
            label="TEST"
        )
