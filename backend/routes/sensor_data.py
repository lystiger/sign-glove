from fastapi import APIRouter, HTTPException
from backend.models.sensor_data import SensorData
from backend.core.database import sensor_collection  

router = APIRouter()
