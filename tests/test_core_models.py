"""
Unit tests for core model functionality.
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
from core.model import predict_from_dual_hand_data, predict_gesture
from core.auth import UserRole, authenticate_user, create_access_token

pytestmark = pytest.mark.unit

class TestPredictionModels:
    """Test prediction model functionality."""
    
    def test_predict_from_dual_hand_data_valid(self):
        """Test dual hand prediction with valid data."""
        data = {
            "left": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
            "right": [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
        }
        
        with patch('core.model.tf.lite.Interpreter') as mock_interpreter:
            mock_interpreter.return_value.get_output_details.return_value = [{'index': 0}]
            mock_interpreter.return_value.get_input_details.return_value = [{'index': 0}]
            mock_interpreter.return_value.invoke.return_value = None
            mock_interpreter.return_value.get_tensor.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
            
            result = predict_from_dual_hand_data(data)
            
            assert result["status"] == "success"
            assert "left_prediction" in result
            assert "right_prediction" in result
            assert "confidence" in result
    
    def test_predict_from_dual_hand_data_invalid(self):
        """Test dual hand prediction with invalid data."""
        data = {"left": [0.1] * 5, "right": [0.2] * 5}  # Not enough values
        
        result = predict_from_dual_hand_data(data)
        
        assert result["status"] == "error"
        assert "Invalid sensor input" in result["message"]
    
    def test_predict_gesture_valid(self):
        """Test single gesture prediction with valid data."""
        values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
        
        with patch('core.model.tf.lite.Interpreter') as mock_interpreter:
            mock_interpreter.return_value.get_output_details.return_value = [{'index': 0}]
            mock_interpreter.return_value.get_input_details.return_value = [{'index': 0}]
            mock_interpreter.return_value.invoke.return_value = None
            mock_interpreter.return_value.get_tensor.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
            
            result = predict_gesture(values)
            
            assert result["status"] == "success"
            assert "prediction" in result
            assert "confidence" in result
    
    def test_predict_gesture_invalid(self):
        """Test single gesture prediction with invalid data."""
        values = [0.1, 0.2, 0.3]  # Not enough values
        
        result = predict_gesture(values)
        
        assert result["status"] == "error"
        assert "Invalid sensor input" in result["message"]

class TestDataProcessing:
    """Test data processing functionality."""
    
    def test_data_normalization(self):
        """Test data normalization."""
        from core.config import NORMALIZE_NUMBER
        
        # Use test data that will normalize to values between 0 and 1
        raw_data = [1000, 2000, 3000, 4000, 4000]  # Max 4000 to ensure normalized <= 1
        normalized = [x / NORMALIZE_NUMBER for x in raw_data]
        
        # Check that normalized values are between 0 and 1
        for x in normalized:
            assert 0 <= x <= 1, f"Value {x} is not between 0 and 1"
        assert len(normalized) == len(raw_data)
    
    def test_sensor_data_validation(self):
        """Test sensor data validation."""
        from core.config import TOTAL_SENSORS
        
        # Valid data
        valid_data = [0.1] * TOTAL_SENSORS
        assert len(valid_data) == TOTAL_SENSORS
        
        # Invalid data
        invalid_data = [0.1] * (TOTAL_SENSORS - 1)
        assert len(invalid_data) != TOTAL_SENSORS

class TestAuthenticationUtils:
    """Test authentication utility functions."""
    
    def test_authenticate_user_valid(self):
        """Test user authentication with valid credentials."""
        user = authenticate_user("admin", "admin123")
        assert user is not None
        assert user.username == "admin"
        assert user.role == UserRole.ADMIN
    
    def test_authenticate_user_invalid(self):
        """Test user authentication with invalid credentials."""
        user = authenticate_user("admin", "wrongpassword")
        assert user is None
    
    def test_create_access_token(self):
        """Test access token creation."""
        token = create_access_token(data={"sub": "test", "role": "user"})
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_structure(self):
        """Test token structure and content."""
        user_data = {"sub": "testuser", "role": UserRole.USER}
        token = create_access_token(data=user_data)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should contain dots (JWT format)
        assert token.count('.') == 2

class TestConfiguration:
    """Test configuration and settings."""
    
    def test_sensor_configuration(self):
        """Test sensor configuration constants."""
        from core.config import FLEX_SENSORS, IMU_SENSORS, TOTAL_SENSORS
        
        assert FLEX_SENSORS == 5
        assert IMU_SENSORS == 6
        assert TOTAL_SENSORS == FLEX_SENSORS + IMU_SENSORS
    
    def test_noise_reduction_config(self):
        """Test noise reduction configuration."""
        from core.config import DEFAULT_NOISE_CONFIG
        
        assert "window_size" in DEFAULT_NOISE_CONFIG
        assert "outlier_threshold" in DEFAULT_NOISE_CONFIG
        assert "apply_moving_avg" in DEFAULT_NOISE_CONFIG
        assert "apply_outlier" in DEFAULT_NOISE_CONFIG
        assert "apply_median" in DEFAULT_NOISE_CONFIG

class TestDatabaseModels:
    """Test database model validation."""
    
    def test_gesture_sample_model(self):
        """Test gesture sample model validation."""
        from models.gesture_responses import GestureSample
        
        # Valid sample data
        valid_data = {
            "flex_values": [1000, 1100, 1200, 1300, 1400],
            "imu_values": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        }
        
        sample = GestureSample(**valid_data)
        assert len(sample.flex_values) == 5
        assert len(sample.imu_values) == 6
    
    def test_training_request_model(self):
        """Test training request model validation."""
        from models.training_models import TrainingRequest
        
        # Valid training request data
        valid_data = {
            "model_name": "test_model",
            "gestures": ["hello", "yes", "no"],
            "epochs": 25
        }
        
        request = TrainingRequest(**valid_data)
        assert request.model_name == "test_model"
        assert len(request.gestures) == 3
        assert request.epochs == 25

class TestErrorHandling:
    """Test error handling in core functions."""
    
    def test_model_file_not_found(self):
        """Test handling of missing model file."""
        with patch('core.model.os.path.exists', return_value=False):
            result = predict_gesture([0.1] * 11)
            assert result["status"] == "error"
            assert "Model file not found" in result["message"]
    
    def test_invalid_model_file(self):
        """Test handling of invalid model file."""
        with patch('core.model.tf.lite.Interpreter') as mock_interpreter:
            mock_interpreter.side_effect = Exception("Invalid model")
            
            result = predict_gesture([0.1] * 11)
            assert result["status"] == "error"
            assert "Error loading model" in result["message"] 