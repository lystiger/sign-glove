"""
API routes for managing model training and results in the sign glove system.

Endpoints:
- POST /training/: Save a training result manually.
- GET /training/: List all training results.
- GET /training/{session_id}: Fetch a training result by session ID.
- POST /training/run: Upload CSV, run training, and log result.
- GET /training/metrics: Fetch detailed training metrics and visualizations.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from models.model_result import ModelResult
from core.database import model_collection, sensor_collection
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime, timezone
from uuid import uuid4
from core.settings import settings
import logging
import subprocess
import shutil
import os
import json
from utils.cache import cacheable
from typing import Dict, Any, List
import csv
from routes.auth_routes import role_required_dep, role_or_internal_dep

router = APIRouter(prefix="/training", tags=["Training"])

@router.post("/")
async def save_model_result(result: ModelResult, _user=Depends(role_or_internal_dep("editor"))):
    """
    Save a training result to the database.
    """
    try:
        res = await model_collection.insert_one(result.model_dump())
        logging.info(f"Inserted training result: {res.inserted_id}")
        return JSONResponse(status_code=201, content={
            "status": "success",
            "data": {"inserted_id": str(res.inserted_id)}
        })
    except Exception as e:
        logging.error(f"Error saving model result: {e}")
        raise HTTPException(status_code=500, detail="Failed to save model result")

@router.get(
    "/",
    summary="List all training results",
    description="Returns a list of all training results, sorted by timestamp (most recent first)."
)
@cacheable(ttl=30)
async def list_training_results() -> Dict[str, Any]:
    """
    Example response:
    {
        "status": "success",
        "data": [
            {"session_id": "abc123", "accuracy": 0.98, ...},
            ...
        ]
    }
    """
    try:
        cursor = model_collection.find().sort("timestamp", -1)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        logging.info(f"Fetched {len(results)} training results")
        return {"status": "success", "data": results}
    except Exception as e:
        logging.error(f"Error listing training results: {e}")
        raise HTTPException(status_code=500, detail="Failed to list training results")

@router.get(
    "/{session_id}",
    summary="Get a training result by session ID",
    description="Fetch a specific training result by its session_id."
)
@cacheable(ttl=30)
async def get_training_result(session_id: str) -> Dict[str, Any]:
    """
    Example response:
    {
        "status": "success",
        "data": { ... }
    }
    """
    try:
        doc = await model_collection.find_one({"session_id": session_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Training result not found")
        doc["_id"] = str(doc["_id"])
        return {"status": "success", "data": doc}
    except Exception as e:
        logging.error(f"Error fetching training result: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch training result")

@router.get("/latest")
async def get_latest_training_result():
    """
    Fetch the most recent training result.
    """
    try:
        result = await model_collection.find_one(sort=[("timestamp", -1)])
        if not result:
            raise HTTPException(status_code=404, detail="No training results found")
        result["_id"] = str(result["_id"])
        return {"status": "success", "data": result}
    except HTTPException as e:
        # Pass through 404 and other HTTPExceptions
        raise
    except Exception as e:
        logging.error(f"Error getting latest training result: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch latest training result")

@router.get("/metrics/latest")
async def get_latest_training_metrics():
    """
    Fetch the latest training metrics including confusion matrix, ROC curves, and performance data.
    """
    try:
        metrics_path = settings.METRICS_PATH
        
        if not os.path.exists(metrics_path):
            raise HTTPException(status_code=404, detail="No training metrics found. Please run training first.")
        
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        logging.error(f"Error fetching training metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch training metrics")

@router.get("/visualizations/{plot_type}")
async def get_training_visualization(plot_type: str):
    """
    Fetch training visualization plots.
    plot_type: 'confusion_matrix', 'roc_curves', 'training_history'
    """
    try:
        ai_dir = settings.AI_DIR
        
        plot_files = {
            'confusion_matrix': 'confusion_matrix.png',
            'roc_curves': 'roc_curves.png', 
            'training_history': 'training_history.png'
        }
        
        if plot_type not in plot_files:
            raise HTTPException(status_code=400, detail=f"Invalid plot type. Must be one of: {list(plot_files.keys())}")
        
        plot_path = os.path.join(ai_dir, plot_files[plot_type])
        
        if not os.path.exists(plot_path):
            raise HTTPException(status_code=404, detail=f"Plot {plot_type} not found. Please run training first.")
        
        return FileResponse(plot_path, media_type="image/png")
    except Exception as e:
        logging.error(f"Error fetching visualization {plot_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch {plot_type} visualization")

@router.post("/run")
async def run_training(file: UploadFile = File(...), _user=Depends(role_or_internal_dep("editor"))):
    """
    Upload a CSV file, run the training script, and log the result.
    """
    try:
        os.makedirs(settings.AI_DIR, exist_ok=True)
        file_path = settings.GESTURE_DATA_PATH
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run the model.py script with absolute path
        script_path = os.path.join(os.path.dirname(__file__), '..', 'AI', 'model.py')
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"Training script error: {result.stderr}")
            raise HTTPException(status_code=500, detail="Training script error")

        logging.info("Training completed successfully")
        stdout = result.stdout

        # Parse test accuracy from stdout
        acc = None
        for line in stdout.splitlines():
            if "Test accuracy" in line:
                try:
                    acc = float(line.split(":")[-1].strip())
                    break
                except ValueError:
                    continue

        if acc is None:
            raise HTTPException(status_code=500, detail="Failed to parse accuracy from output")

        # Save result using your full schema
        session_id = str(uuid4())
        training_result = ModelResult(
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            accuracy=acc,
            model_name=settings.MODEL_PATH,
            notes="Auto-trained via /training/run"
        )
        res = await model_collection.insert_one(training_result.model_dump())
        logging.info(f"Logged training result with ID {res.inserted_id}")

        return {
            "status": "success",
            "data": {
                "inserted_id": str(res.inserted_id),
                "session_id": session_id,
                "accuracy": acc
            }
        }

    except Exception as e:
        logging.error(f"Training run failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to run training")

@router.post("/trigger")
async def trigger_training_run(_user=Depends(role_or_internal_dep("editor"))):
    """
    Trigger the model training job (same as POST /training/run but without upload).
    """
    try:
        # Export latest sensor data from MongoDB to CSV so training uses fresh data
        export_path = settings.GESTURE_DATA_PATH
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        cursor = sensor_collection.find().sort("timestamp", 1)
        rows: List[Dict[str, Any]] = []
        async for doc in cursor:
            values = doc.get("values", [])
            if isinstance(values, list) and len(values) == 11:
                rows.append({
                    "session_id": doc.get("session_id", "auto"),
                    "label": doc.get("label", "unknown"),
                    "values": values
                })
        if not rows:
            logging.warning("No sensor data found to export for training. Using existing CSV if present.")
        else:
            header = [
                "session_id", "label",
                "flex1", "flex2", "flex3", "flex4", "flex5",
                "accel_x", "accel_y", "accel_z",
                "gyro_x", "gyro_y", "gyro_z"
            ]
            with open(export_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for r in rows:
                    writer.writerow([r["session_id"], r["label"], *r["values"]])
            logging.info(f"Exported {len(rows)} sensor rows to {export_path} for training.")

        # Assumes gesture_data.csv already exists
        script_path = os.path.join(os.path.dirname(__file__), '..', 'AI', 'model.py')
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"Training script error: {result.stderr}")
            raise HTTPException(status_code=500, detail="Training script error")

        # Parse accuracy
        acc = None
        for line in result.stdout.splitlines():
            if "Test accuracy" in line:
                try:
                    acc = float(line.split(":")[-1].strip())
                    break
                except ValueError:
                    continue

        if acc is None:
            raise HTTPException(status_code=500, detail="Failed to parse accuracy")

        session_id = str(uuid4())
        training_result = ModelResult(
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            accuracy=acc,
            model_name=settings.MODEL_PATH,
            notes="Triggered via POST /training/trigger"
        )
        res = await model_collection.insert_one(training_result.model_dump())
        logging.info(f"Logged training result with ID {res.inserted_id}")

        return {
            "status": "success",
            "data": {
                "inserted_id": str(res.inserted_id),
                "session_id": session_id,
                "accuracy": acc
            }
        }

    except Exception as e:
        logging.error(f"Triggered training failed: {e}")
        raise HTTPException(status_code=500, detail="Training failed")