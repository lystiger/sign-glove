import pytest

@pytest.mark.asyncio
async def test_login(async_client):
    resp = await async_client.post("/auth/login", json={
        "email": "admin@signglove.com",
        "password": "admin123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "access_token" in data
