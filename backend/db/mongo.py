from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB URI and client
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["sign_glove_db"]

def get_sensor_collection():
    return db["sensor_data"]
