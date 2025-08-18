from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from routes import training_trigger, training_routes, sensor_routes, predict_routes, admin_routes, dashboard_routes
from routes import gestures, liveWS, utils_routes, auth_routes
from routes import audio_files_routes
from routes import auth_routes
from core.indexes import create_indexes 
from core.database import client, test_connection
from core.settings import settings
from core.auth import get_required_role_for_path, require_admin, require_user, require_viewer
from core.middleware import setup_middleware
from core.error_handler import create_error_response, error_tracker, performance_monitor
from contextlib import asynccontextmanager
import logging
import os
import asyncio
import subprocess
import uuid
from routes.auth_routes import ensure_default_editor

# Improved logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("signglove")

async def automated_pipeline_loop():
    import time
    RAW_DATA_PATH = settings.RAW_DATA_PATH
    LAST_PROCESSED_PATH = os.path.join(os.path.dirname(RAW_DATA_PATH), 'last_processed.txt')

    def get_last_processed_time():
        if os.path.exists(LAST_PROCESSED_PATH):
            try:
                with open(LAST_PROCESSED_PATH, 'r') as f:
                    return float(f.read().strip())
            except Exception:
                return None
        return None

    def set_last_processed_time(mtime):
        with open(LAST_PROCESSED_PATH, 'w') as f:
            f.write(str(mtime))

    last_mtime = get_last_processed_time()
    while True:
        try:
            if not os.path.exists(RAW_DATA_PATH):
                logging.info("[AUTO] No raw_data.csv found, skipping this cycle.")
            else:
                mtime = os.path.getmtime(RAW_DATA_PATH)
                if last_mtime is None or mtime > last_mtime:
                    last_mtime = mtime
                    set_last_processed_time(mtime)
                    logging.info("[AUTO] New data detected in raw_data.csv. Running noise reduction and training...")
                    result = subprocess.run([
                        "python", "-m", "processors.noise_reducer"
                    ], capture_output=True, text=True)
                    if result.returncode != 0:
                        logging.error(f"[AUTO] Noise reducer error: {result.stderr}")
                    else:
                        logging.info(f"[AUTO] Noise reduction complete: {result.stdout.strip()}")

                    logging.info("[AUTO] Triggering model training...")
                    import requests
                    try:
                        resp = requests.post(
                            "http://localhost:8080/training/trigger",
                            headers={"X-API-KEY": settings.SECRET_KEY}
                        )
                        if resp.status_code == 200:
                            logging.info(f"[AUTO] Training triggered successfully: {resp.json()}")
                        else:
                            logging.error(f"[AUTO] Training trigger failed: {resp.status_code} - {resp.text}")
                    except Exception as e:
                        logging.error(f"[AUTO] Error triggering training: {e}")
                else:
                    logging.info("[AUTO] No new data in raw_data.csv. Skipping noise reduction and training.")
        except Exception as e:
            logging.error(f"[AUTO] Pipeline error: {e}")
        await asyncio.sleep(300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await test_connection() 
    await create_indexes()
    await ensure_default_editor()
    logging.info("Indexes created. App is starting...")
    loop = asyncio.get_event_loop()
    # Disable automated pipeline during testing to avoid event loop issues
    if not settings.is_testing():
        loop.create_task(automated_pipeline_loop())
    yield
    client.close()
    logging.info("MongoDB connection closed. App is shutting down...")

app = FastAPI(title="Sign Glove API", lifespan=lifespan)

# Setup middleware
setup_middleware(app)

# Global error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return create_error_response(exc, request)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response(exc, request)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return create_error_response(exc, request)

# Use CORS origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_routes.router)
app.include_router(gestures.router)
app.include_router(training_trigger.router)
app.include_router(training_routes.router)
app.include_router(sensor_routes.router)
app.include_router(predict_routes.router)
app.include_router(admin_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(liveWS.router)
app.include_router(utils_routes.router)
app.include_router(audio_files_routes.router)

# Mount models directory for static files if needed
app.mount("/models", StaticFiles(directory=settings.DATA_DIR), name="models")

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker containers"""
    try:
        # Test database connection
        await test_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def get_metrics():
    """Get performance metrics."""
    return {
        "performance": performance_monitor.get_performance_stats(),
        "errors": len(error_tracker.error_log)
    }

