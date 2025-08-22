import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from core.model import predict_from_dual_hand_data

def test_predict_from_dual_hand_data_invalid():
    # Not enough values
    data = {"left": [0.1] * 5, "right": [0.2] * 5}
    result = predict_from_dual_hand_data(data)
    assert result["status"] == "error"
    assert "Invalid sensor input" in result["message"]

def test_predict_from_dual_hand_data_valid(monkeypatch):
    # Patch tf.lite.Interpreter to avoid loading a real model
    class DummyInterpreter:
        def allocate_tensors(self): pass
        def get_input_details(self): return [{"index": 0}]
        def get_output_details(self): return [{"index": 0}]
        def set_tensor(self, idx, val): pass
        def invoke(self): pass
        def get_tensor(self, idx): return [[0.1, 0.9, 0.0, 0.0]]
    import core.model as model_mod
    monkeypatch.setattr(model_mod.tf.lite, "Interpreter", lambda model_path: DummyInterpreter())
    data = {"left": [0.1] * 11, "right": [0.2] * 11}
    result = predict_from_dual_hand_data(data)
    assert result["status"] == "success"
    assert "confidence" in result 