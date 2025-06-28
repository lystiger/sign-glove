from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)

db = client["sign_glove_"]

sensor_collection = db["sensor_data"]
model_collection = db["model_results"]
gesture_collection = db["gestures"]
training_collection = db["training_sessions"]

async def init_indexes():
    await sensor_collection.create_index("session_id")
    await sensor_collection.create_index("gesture_label")
    await sensor_collection.create_index("timestamp")
    await model_collection.create_index("model_name")  
    await training_collection.create_index("model_name")
    await training_collection.create_index("started_at")


