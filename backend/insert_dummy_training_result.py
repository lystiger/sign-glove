from core.database import model_collection
import asyncio
from datetime import datetime

async def insert_manual_result():
    doc = {
        "session_id": "manual",
        "timestamp": datetime.utcnow().isoformat(),
        "accuracy": 0.95,
        "model_name": "gesture_model.tflite",
        "notes": "Manually added for testing"
    }
    result = await model_collection.insert_one(doc)
    print(f"Inserted dummy training result with _id: {result.inserted_id}")

if __name__ == "__main__":
    asyncio.run(insert_manual_result()) 