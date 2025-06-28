import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_add_sensor_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "sensor_id": "glove1",
            "values": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        response = await ac.post("/sensor/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Data received"
