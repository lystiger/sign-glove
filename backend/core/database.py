"""
Database connection and collection setup for the sign glove system.

- Sets up MongoDB client and main collections (predictions, sensor_data, model_results, gestures, training_sessions).
- Provides async test_connection function to verify MongoDB connectivity.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["sign_glove"]
prediction_collection = db["predictions"]

sensor_collection = db["sensor_data"]
model_collection = db["model_results"]
gesture_collection = db["gestures"]
training_collection = db["training_sessions"]

async def test_connection():
    """
    Test the MongoDB connection by sending a ping command.
    Logs success or failure.
    """
    try:
        await client.admin.command("ping")
        logger.info("✅ Connected to MongoDB Atlas!")
    except Exception as e:
        logger.error("❌ MongoDB connection failed:", exc_info=e)
