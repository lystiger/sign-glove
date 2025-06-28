from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import sensor_routes, training_routes
from backend.routes import gestures
from backend.core.indexes import create_indexes 
from backend.core.database import client
from contextlib import asynccontextmanager
import logging

#  Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

#  Lifecycle event
@asynccontextmanager
async def lifespan(app: FastAPI):
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


#  Root route
@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
