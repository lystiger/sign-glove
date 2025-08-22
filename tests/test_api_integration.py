"""
Integration tests for API endpoints with authentication.
"""
import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.integration

class TestGesturesAPI:
    """Test gesture management endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_gesture_session(self, async_client, user_headers, sample_gesture_session):
        """Test creating a new gesture session."""
        client = async_client()
        response = await client.post("/gestures/", json=sample_gesture_session, headers=user_headers)
        assert response.status_code == 200
        await client.aclose()
    
    @pytest.mark.asyncio
    async def test_get_gestures_list(self, async_client, user_headers):
        """Test getting list of gesture sessions."""
        client = async_client()
        response = await client.get("/gestures/", headers=user_headers)
        assert response.status_code == 200
        await client.aclose()
    
    @pytest.mark.asyncio
    async def test_get_gesture_by_id(self, async_client, user_headers, sample_gesture_session):
        """Test getting a specific gesture session."""
        client = async_client()
        # First create a session
        create_response = await client.post("/gestures/", json=sample_gesture_session, headers=user_headers)
        assert create_response.status_code == 200
        
        # Then get it by ID
        session_id = create_response.json().get("session_id")
        response = await client.get(f"/gestures/{session_id}", headers=user_headers)
        assert response.status_code == 200
        await client.aclose()
    
    @pytest.mark.asyncio
    async def test_update_gesture_label(self, async_client, user_headers, sample_gesture_session):
        """Test updating gesture label."""
        client = async_client()
        # First create a session
        create_response = await client.post("/gestures/", json=sample_gesture_session, headers=user_headers)
        assert create_response.status_code == 200
        
        # Then update the label
        session_id = create_response.json().get("session_id")
        update_data = {"gesture_label": "updated_hello"}
        response = await client.put(f"/gestures/{session_id}", json=update_data, headers=user_headers)
        assert response.status_code == 200
        await client.aclose()
    
    @pytest.mark.asyncio
    async def test_delete_gesture_session(self, async_client, user_headers, sample_gesture_session):
        """Test deleting a gesture session."""
        client = async_client()
        # First create a session
        create_response = await client.post("/gestures/", json=sample_gesture_session, headers=user_headers)
        assert create_response.status_code == 200
        
        # Then delete it
        session_id = create_response.json().get("session_id")
        response = await client.delete(f"/gestures/{session_id}", headers=user_headers)
        assert response.status_code == 200
        await client.aclose()

class TestPredictionAPI:
    """Test prediction endpoints."""
    
    @pytest.mark.asyncio
    async def test_predict_gesture(self, async_client, user_headers):
        """Test gesture prediction."""
        client = async_client()
        prediction_data = {
            "values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
        }

        response = await client.post("/predict/", json=prediction_data, headers=user_headers)   
        assert response.status_code == 200
        await client.aclose()

    @pytest.mark.asyncio
    async def test_predict_invalid_input(self, async_client, user_headers):
        """Test prediction with invalid input."""
        client = async_client()
        prediction_data = {
            "values": [0.1, 0.2, 0.3]  # Not enough values
        }

        response = await client.post("/predict/", json=prediction_data, headers=user_headers)   
        assert response.status_code == 422  # Validation error
        await client.aclose()

    @pytest.mark.asyncio
    async def test_live_predict(self, async_client, user_headers):
        """Test live prediction endpoint."""
        client = async_client()
        response = await client.get("/predict/live", headers=user_headers)
        assert response.status_code == 200
        await client.aclose()

class TestDashboardAPI:
    """Test dashboard API endpoints."""

    @pytest.mark.asyncio
    async def test_dashboard_stats(self, async_client, viewer_headers):
        """Test dashboard statistics."""
        client = async_client()
        response = await client.get("/dashboard/", headers=viewer_headers)
        assert response.status_code == 200
        await client.aclose()

class TestTrainingAPI:
    """Test training API endpoints."""

    @pytest.mark.asyncio
    async def test_get_training_results(self, async_client, admin_headers):
        """Test getting training results."""
        client = async_client()
        response = await client.get("/training/", headers=admin_headers)
        assert response.status_code == 200
        await client.aclose()

    @pytest.mark.asyncio
    async def test_get_latest_training_result(self, async_client, admin_headers):        
        """Test getting latest training result."""
        client = async_client()
        response = await client.get("/training/latest", headers=admin_headers)
        assert response.status_code == 200
        await client.aclose()

    @pytest.mark.asyncio
    async def test_get_training_metrics(self, async_client, admin_headers):
        """Test getting training metrics."""
        client = async_client()
        response = await client.get("/training/metrics/latest", headers=admin_headers)
        assert response.status_code == 200
        await client.aclose()

class TestAdminAPI:
    """Test admin API endpoints."""

    @pytest.mark.asyncio
    async def test_admin_clear_sensor_data(self, async_client, admin_headers):
        """Test clearing sensor data (admin only)."""
        client = async_client()
        response = await client.delete("/admin/sensor-data", headers=admin_headers)
        assert response.status_code == 200
        await client.aclose()

    @pytest.mark.asyncio
    async def test_admin_clear_training_results(self, async_client, admin_headers):      
        """Test clearing training results (admin only)."""
        client = async_client()
        response = await client.delete("/admin/training-results", headers=admin_headers)        
        assert response.status_code == 200
        await client.aclose()

    @pytest.mark.asyncio
    async def test_admin_denied_to_user(self, async_client, user_headers):
        """Test that users cannot access admin endpoints."""
        client = async_client()
        response = await client.delete("/admin/sensor-data", headers=user_headers)
        assert response.status_code == 403  # Forbidden
        await client.aclose()

class TestSensorAPI:
    """Test sensor data API endpoints."""

    @pytest.mark.asyncio
    async def test_store_sensor_data(self, async_client, user_headers, sample_sensor_data):
        """Test storing sensor data."""
        client = async_client()
        response = await client.post("/sensor-data/", json=sample_sensor_data, headers=user_headers)
        assert response.status_code == 200
        await client.aclose()

    @pytest.mark.asyncio
    async def test_get_sensor_data(self, async_client, user_headers):
        """Test getting sensor data."""
        client = async_client()
        response = await client.get("/sensor-data/", headers=user_headers)
        assert response.status_code == 200
        await client.aclose()

class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_404_not_found(self, async_client, user_headers):
        """Test 404 error handling."""
        client = async_client()
        response = await client.get("/nonexistent-endpoint", headers=user_headers)
        assert response.status_code == 404
        await client.aclose()

    @pytest.mark.asyncio
    async def test_validation_error(self, async_client, user_headers):
        """Test validation error handling."""
        client = async_client()
        invalid_data = {"invalid": "data"}
        response = await client.post("/gestures/", json=invalid_data, headers=user_headers)     
        assert response.status_code == 422  # Validation error
        await client.aclose() 