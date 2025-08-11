#!/usr/bin/env python3
"""
System Test Script for Sign Glove
Tests the backend functionality without hardware
"""

import requests
import json
import time
import sys
import os
import pytest

BASE_URL = "http://localhost:8080"

def test_health():
    """Test if the backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, f"Backend health check failed: {response.status_code}"
        print("Backend is running")
    except requests.exceptions.ConnectionError:
        print("Backend not running - skipping test")
        pytest.skip("Backend not running")
    except Exception as e:
        print(f"Health check error: {e}")
        raise

def test_prediction():
    """Test prediction with sample data"""
    try:
        # Sample sensor data
        sample_data = {
            "values": [1024, 1024, 1024, 1024, 1024, 0, 0, 16384, 0, 0, 0]
        }
        
        response = requests.post(f"{BASE_URL}/predict/", json=sample_data, timeout=5)
        assert response.status_code == 200, f"Prediction failed: {response.status_code} - {response.text}"
        result = response.json()
        print(f"Prediction successful: {result}")
    except requests.exceptions.ConnectionError:
        print("Backend not running - skipping test")
        pytest.skip("Backend not running")
    except Exception as e:
        print(f"Prediction test error: {e}")
        raise

def test_gesture_creation():
    """Test creating a gesture session"""
    try:
        gesture_data = {
            "session_id": "test_session",
            "timestamp": "2024-01-01T12:00:00Z",
            "sensor_values": [[1024, 1024, 1024, 1024, 1024, 0, 0, 16384, 0, 0, 0]],
            "gesture_label": "test_gesture",
            "device_info": {"source": "test", "device_id": "test_device"}
        }
        
        response = requests.post(f"{BASE_URL}/gestures/", json=gesture_data, timeout=5)
        assert response.status_code == 200, f"Gesture creation failed: {response.status_code} - {response.text}"
        print("Gesture creation successful")
    except requests.exceptions.ConnectionError:
        print("Backend not running - skipping test")
        pytest.skip("Backend not running")
    except Exception as e:
        print(f"Gesture creation error: {e}")
        raise

def test_dashboard():
    """Test dashboard endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/", timeout=5)
        assert response.status_code == 200, f"Dashboard failed: {response.status_code}"
        data = response.json()
        print(f"Dashboard accessible - Gestures: {data.get('total_gestures', 0)}")
    except requests.exceptions.ConnectionError:
        print("Backend not running - skipping test")
        pytest.skip("Backend not running")
    except Exception as e:
        print(f"Dashboard test error: {e}")
        raise

def test_training():
    """Test training trigger"""
    try:
        response = requests.post(f"{BASE_URL}/training/trigger", timeout=5)
        assert response.status_code == 200, f"Training trigger failed: {response.status_code} - {response.text}"
        print("Training trigger successful")
    except requests.exceptions.ConnectionError:
        print("Backend not running - skipping test")
        pytest.skip("Backend not running")
    except Exception as e:
        print(f"Training test error: {e}")
        raise

def main():
    print("Testing Sign Glove System...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Dashboard", test_dashboard),
        ("Gesture Creation", test_gesture_creation),
        ("Prediction", test_prediction),
        ("Training Trigger", test_training),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"Test failed: {e}")
        except Exception as e:
            print(f"Test error: {e}")
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! System is ready.")
        return 0
    else:
        print("Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 