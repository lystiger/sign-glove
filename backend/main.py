from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.routes import gestures, training
from backend.core.indexes import create_indexes 
from backend.core.database import client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run on startup
    create_indexes()
    print("✅ Indexes created. App is starting...")

    yield  

    client.close()
    print("🛑 MongoDB connection closed. App is shutting down...")

app = FastAPI(title="Sign Glove API", lifespan=lifespan)

app.include_router(gestures.router, prefix="/gestures", tags=["Gestures"])
#app.include_router(training.router, prefix="/training", tags=["Training"])

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
