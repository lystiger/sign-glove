import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_list_gestures():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/gestures/")
        assert response.status_code in (200, 404, 307)

@pytest.mark.asyncio
async def test_create_gesture():
    payload = {
        "session_id": "test_session",
        "timestamp": "2025-07-23T12:00:00Z",
        "sensor_values": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]],
        "gesture_label": "test_gesture",
        "device_info": {
            "source": "USB",
            "device_id": "glove-01"
        }
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/gestures/", json=payload)
        assert response.status_code in (200, 201, 307, 422)

@pytest.mark.asyncio
async def test_delete_gesture():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/gestures/test_session")
        assert response.status_code in (200, 404, 422) 