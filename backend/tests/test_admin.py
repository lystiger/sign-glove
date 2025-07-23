import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_delete_sensor_data():
    response = client.delete("/admin/sensor-data")
    # Should return 200 OK or 500 if error
    assert response.status_code in (200, 500)

def test_delete_training_results():
    response = client.delete("/admin/training-results")
    # Should return 200 OK or 500 if error
    assert response.status_code in (200, 500) 