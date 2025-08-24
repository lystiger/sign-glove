#!/usr/bin/env python3
"""
Test script for dual-hand sign glove system
Tests the dual-hand prediction function with sample data
"""

import sys
import os
import numpy as np

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from core.model import predict_from_dual_hand_data

def test_dual_hand_prediction():
    """Test the dual-hand prediction function"""
    
    print("🧤 Testing Dual-Hand Sign Glove System")
    print("=" * 50)
    
    # Test 1: Valid dual-hand data
    print("\n✅ Test 1: Valid dual-hand data (22 sensors)")
    left_hand = [100, 200, 300, 400, 500,  # 5 flex sensors
                 10, 20, 30,                 # 3 accelerometer
                 5, 15, 25]                  # 3 gyroscope
    
    right_hand = [150, 250, 350, 450, 550,  # 5 flex sensors
                  15, 25, 35,                # 3 accelerometer
                  8, 18, 28]                 # 3 gyroscope
    
    test_data = {
        "left": left_hand,
        "right": right_hand,
        "timestamp": 1234567890
    }
    
    result = predict_from_dual_hand_data(test_data)
    print(f"Result: {result}")
    
    # Test 2: Invalid data (wrong number of sensors)
    print("\n❌ Test 2: Invalid data (wrong sensor count)")
    invalid_data = {
        "left": [1, 2, 3],  # Only 3 values
        "right": [4, 5, 6], # Only 3 values
        "timestamp": 1234567890
    }
    
    result = predict_from_dual_hand_data(invalid_data)
    print(f"Result: {result}")
    
    # Test 3: Missing data
    print("\n❌ Test 3: Missing hand data")
    missing_data = {
        "left": left_hand,
        "timestamp": 1234567890
        # Missing right hand
    }
    
    result = predict_from_dual_hand_data(missing_data)
    print(f"Result: {result}")
    
    print("\n" + "=" * 50)
    print("🧪 Dual-hand testing completed!")
    
    return True

def test_model_files():
    """Check if required model files exist"""
    
    print("\n📁 Checking Model Files")
    print("-" * 30)
    
    from core.settings import settings
    
    # Check single-hand model
    single_model = settings.MODEL_PATH
    if os.path.exists(single_model):
        print(f"✅ Single-hand model: {single_model}")
    else:
        print(f"❌ Single-hand model not found: {single_model}")
    
    # Check dual-hand model
    dual_model = settings.MODEL_DUAL_PATH
    if os.path.exists(dual_model):
        print(f"✅ Dual-hand model: {dual_model}")
    else:
        print(f"⚠️  Dual-hand model not found: {dual_model}")
        print("   (This is expected if you haven't trained it yet)")
    
    return True

def main():
    """Main test function"""
    
    try:
        # Test model files
        test_model_files()
        
        # Test dual-hand prediction
        test_dual_hand_prediction()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next steps:")
        print("1. Upload the dual_hand_sketch.ino to your second Arduino")
        print("2. Connect both gloves to different COM ports")
        print("3. Run collect_dual_hand_data.py to collect training data")
        print("4. Run train_dual_hand_model.py to train the model")
        print("5. Test real-time prediction with both gloves!")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 