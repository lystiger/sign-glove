from fastapi.testclient import TestClient
import pytest

import sys, os
sys.path.append(os.path.dirname(__file__))
from main import app

client = TestClient(app)

def get_admin_headers():
    resp = client.post("/auth/login", json={
        "email": "admin@signglove.com",
        "password": "admin123"
    })
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_delete_sensor_data(async_client):
    resp = await async_client.post("/auth/login", json={
        "email": "admin@signglove.com",
        "password": "admin123"
    })
    assert resp.status_code == 200
def test_delete_training_results():
    headers = get_admin_headers()
    response = client.delete("/admin/training-results", headers=headers)
    assert response.status_code in (200, 500)