# core/model.py

import numpy as np
import tensorflow as tf  # or tflite_runtime.interpreter if used on embedded

def predict_from_dual_hand_data(data: dict) -> dict:
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
        interpreter = tf.lite.Interpreter(model_path="backend/AI/gesture_model_dual.tflite")
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
