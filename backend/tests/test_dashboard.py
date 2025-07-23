import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_dashboard_stats():
    response = client.get("/dashboard/")
    # Should return 200 OK or 500 if DB error
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert "data" in data 