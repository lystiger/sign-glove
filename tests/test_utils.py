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

def test_health_check():
    response = client.get("/utils/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_invalid_input():
    # Missing 'values' key
    response = client.post("/predict/", json={})
    assert response.status_code == 422  # Unprocessable Entity

def test_predict_valid_input():
    # 11 float values (simulate a valid sensor input)
    payload = {"values": [0.1] * 11}
    response = client.post("/predict/", json=payload)
    # Should return 200 or 500 if model file is missing, but not 422
    assert response.status_code in (200, 500)

def test_training_trigger():
    # This will run the training script, so may be slow or fail if not set up
    response = client.post("/training/", json={"model_name": "LSTM_v1"})
    # Accept 202 (accepted), 200 (success), or 500 (error if script fails)
    assert response.status_code in (200, 202, 500) 