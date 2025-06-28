from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB URI and client
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sign_glove_db"]
sensor_collection = db["sensor_data"]

def get_sensor_collection():
    return sensor_collection

# Add this function to create indexes on startup
async def create_indexes():
    await sensor_collection.create_index("session_id")
    await sensor_collection.create_index("_timestamp")