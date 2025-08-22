import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
except ImportError:
    from httpx import Client
    client = Client(app=app, base_url="http://test")

def test_get_gestures():
    response = client.get("/gestures")
    assert response.status_code == 200

def test_get_training_results():
    response = client.get("/training/results")
    assert response.status_code == 200

def test_get_predictions():
    response = client.get("/predict/history")
    assert response.status_code == 200

def test_get_dashboard_stats():
    response = client.get("/dashboard/stats")
    assert response.status_code == 200

def test_get_utils_info():
    response = client.get("/utils/info")
    assert response.status_code == 200

def test_get_admin_info():
    response = client.get("/admin/info")
    assert response.status_code == 200

def test_get_audio_files():
    response = client.get("/audio-files")
    assert response.status_code == 200

def test_get_sensor_data():
    response = client.get("/sensor/data")
    assert response.status_code == 200

def test_get_live_predict():
    response = client.get("/live-predict")
    assert response.status_code == 200

def test_get_training_trigger():
    response = client.get("/training/trigger")
    assert response.status_code == 200

def test_get_data_info():
    response = client.get("/data/info")
    assert response.status_code == 200 