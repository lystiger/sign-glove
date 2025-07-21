from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes import training_trigger, training_routes, sensor_routes, predict_routes, admin_routes, dashboard_routes
from routes import gestures, liveWS
from core.indexes import create_indexes 
from core.database import client, test_connection
from contextlib import asynccontextmanager
import logging
import os
import asyncio
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
models_path = os.path.join(BASE_DIR, "data")

#  Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

async def automated_pipeline_loop():
    """
    Background task: runs noise reduction and triggers training in a loop, only if new data is present.
    Persists last processed mtime in a file to avoid reprocessing on restart.
    """
    import time
    RAW_DATA_PATH = os.path.join(BASE_DIR, 'data/raw_data.csv')
    LAST_PROCESSED_PATH = os.path.join(BASE_DIR, 'data/last_processed.txt')

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
                    # Run noise_reducer.py as a module
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
                        resp = requests.post("http://localhost:8080/training/trigger")
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
        # Wait 5 minutes before next run
        await asyncio.sleep(300)

#  Lifecycle event
@asynccontextmanager
async def lifespan(app: FastAPI):
    await test_connection() 
    await create_indexes()
    logging.info("✅ Indexes created. App is starting...")
    # Start the automated pipeline loop
    loop = asyncio.get_event_loop()
    loop.create_task(automated_pipeline_loop())
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
app.include_router(training_trigger.router)
app.include_router(training_routes.router)
app.include_router(sensor_routes.router)
app.include_router(predict_routes.router)
app.include_router(admin_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(liveWS.router)
app.mount("/models", StaticFiles(directory=models_path), name="models")


#  Root route
@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}

