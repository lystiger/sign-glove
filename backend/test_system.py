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

BASE_URL = "http://localhost:8080"

def test_health():
    """Test if the backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        return False

def test_prediction():
    """Test prediction with sample data"""
    try:
        # Sample sensor data
        sample_data = {
            "values": [1024, 1024, 1024, 1024, 1024, 0, 0, 16384, 0, 0, 0]
        }
        
        response = requests.post(f"{BASE_URL}/predict/", json=sample_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction successful: {result}")
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Prediction test error: {e}")
        return False

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
        
        response = requests.post(f"{BASE_URL}/gestures/", json=gesture_data)
        if response.status_code == 200:
            print("✅ Gesture creation successful")
            return True
        else:
            print(f"❌ Gesture creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Gesture creation error: {e}")
        return False

def test_dashboard():
    """Test dashboard endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard accessible - Gestures: {data.get('total_gestures', 0)}")
            return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard test error: {e}")
        return False

def test_training():
    """Test training trigger"""
    try:
        response = requests.post(f"{BASE_URL}/training/trigger")
        if response.status_code == 200:
            print("✅ Training trigger successful")
            return True
        else:
            print(f"❌ Training trigger failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Training test error: {e}")
        return False

def main():
    print("🧪 Testing Sign Glove System...")
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
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 