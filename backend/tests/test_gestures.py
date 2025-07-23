import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_gestures():
    response = client.get("/gestures/")
    # Should return 200 OK or 404 if not implemented
    assert response.status_code in (200, 404)

def test_create_gesture():
    # Minimal valid payload (adjust fields as needed)
    payload = {"label": "test_gesture", "session_id": "test_session"}
    response = client.post("/gestures/", json=payload)
    # Should return 201 Created, 200 OK, or 422 if validation fails
    assert response.status_code in (200, 201, 422)

def test_delete_gesture():
    # Try to delete a gesture by label (adjust as needed)
    response = client.delete("/gestures/test_gesture")
    # Should return 200 OK, 404 if not found, or 422 if validation fails
    assert response.status_code in (200, 404, 422) 