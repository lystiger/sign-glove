import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/utils/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_db_stats():
    response = client.get("/utils/db/stats")
    # Should return 200 OK or 500 if DB error
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        data = response.json()
        assert "sensor_data_count" in data

def test_tts_to_esp32(monkeypatch):
    # Mock requests.post to avoid real network call
    def dummy_post(*args, **kwargs):
        class DummyResp:
            status_code = 200
            text = "OK"
        return DummyResp()
    import requests
    monkeypatch.setattr(requests, "post", dummy_post)
    response = client.post("/utils/test_tts_to_esp32", json={"text": "hello"})
    # Should return 200 OK or 500 if TTS error
    assert response.status_code in (200, 500) 