"""
Model inference logic for dual-hand gesture prediction in the sign glove system.

- predict_from_dual_hand_data: Loads a TFLite model and predicts gesture from left and right hand sensor data.
"""
# core/model.py

import numpy as np
import tensorflow as tf  # or tflite_runtime.interpreter if used on embedded
import os
from core.settings import settings

def predict_from_dual_hand_data(data: dict) -> dict:
    """
    Predicts gesture from dual-hand sensor data using a TFLite model.
    Args:
        data (dict): Dictionary with 'left', 'right', and 'timestamp' keys.
    Returns:
        dict: Prediction result with status, predictions, confidence, and timestamp.
    """
    try:
        left = data.get("left", [])
        right = data.get("right", [])
        timestamp = data.get("timestamp")

        if len(left) != 11 or len(right) != 11:
            return {
                "status": "error",
                "message": "Invalid sensor input (expected 11 values per hand)"
            }

        # Combine left + right data
        combined = np.array([left + right], dtype=np.float32)  # shape: [1, 22]

        # Load TFLite model (dual-hand version, trained on 22 inputs)
        interpreter = tf.lite.Interpreter(model_path=settings.MODEL_DUAL_PATH)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]['index'], combined)
        interpreter.invoke()

        output = interpreter.get_tensor(output_details[0]['index'])
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        label_map = {0: "Hello", 1: "Yes", 2: "No", 3: "Thanks"}
        label = label_map.get(predicted_index, f"Class {predicted_index}")

        return {
            "status": "success",
            "left_prediction": label,       # Or split if you use 2 models
            "right_prediction": label,      # Same as left for now unless you run 2 heads
            "confidence": confidence,
            "timestamp": timestamp
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def predict_gesture(values: list) -> dict:
    """
    Predicts gesture from single hand sensor data using a TFLite model.
    Args:
        values (list): List of 11 sensor values.
    Returns:
        dict: Prediction result with status, prediction, and confidence.
    """
    try:
        if len(values) != 11:
            return {
                "status": "error",
                "message": "Invalid sensor input (expected 11 values)"
            }

        # Check if model file exists
        if not os.path.exists(settings.MODEL_PATH):
            return {
                "status": "error",
                "message": "Model file not found"
            }

        # Prepare input data
        input_data = np.array([values], dtype=np.float32)

        # Load TFLite model
        interpreter = tf.lite.Interpreter(model_path=settings.MODEL_PATH)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        output = interpreter.get_tensor(output_details[0]['index'])
        predicted_index = int(np.argmax(output))
        confidence = float(np.max(output))

        label_map = {0: "Hello", 1: "Yes", 2: "No", 3: "Thanks"}
        label = label_map.get(predicted_index, f"Class {predicted_index}")

        return {
            "status": "success",
            "prediction": label,
            "confidence": confidence
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error loading model: {str(e)}"
        }
