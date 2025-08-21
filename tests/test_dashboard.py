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

def test_get_dashboard_stats():
    response = client.get("/dashboard/stats")
    assert response.status_code == 200 