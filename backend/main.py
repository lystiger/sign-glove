from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes import training_routes, sensor_routes, predict_routes, admin_routes,dashboard_routes
from routes import gestures
from core.indexes import create_indexes 
from core.database import client, test_connection
from contextlib import asynccontextmanager
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
models_path = os.path.join(BASE_DIR, "data")

#  Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

#  Lifecycle event
@asynccontextmanager
async def lifespan(app: FastAPI):
    await test_connection() 
    await create_indexes()
    logging.info("✅ Indexes created. App is starting...")
    yield
    client.close()
    logging.info("🛑 MongoDB connection closed. App is shutting down...")

#  App instance with lifespan
app = FastAPI(title="Sign Glove API", lifespan=lifespan)

origins = [
    "http://localhost:5173",  # React frontend
    # Add more if deployed
]
#  CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,  # Allow all for now; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Mount routers
app.include_router(gestures.router)
app.include_router(training_routes.router)
app.include_router(sensor_routes.router)
app.include_router(predict_routes.router)
app.include_router(admin_routes.router)
app.include_router(dashboard_routes.router)
app.mount("/models", StaticFiles(directory=models_path), name="models")


#  Root route
@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}

