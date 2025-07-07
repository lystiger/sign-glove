// src/pages/Predict.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './styling/Predict.css';

const Predict = () => {
  const [values, setValues] = useState(Array(11).fill(0));
  const [result, setResult] = useState(null);

  const handleChange = (index, value) => {
    const updated = [...values];
    updated[index] = parseFloat(value);
    setValues(updated);
  };

  const handlePredict = async () => {
    try {
      const res = await axios.post('http://localhost:8080/predict', { values });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Prediction failed.");
    }
  };

  return (
    <div className="predict-wrapper">
      <h2 className="predict-title">Predict Gesture</h2>

      <div className="predict-grid">
        {values.map((val, i) => (
          <input
            key={i}
            type="number"
            value={val}
            onChange={(e) => handleChange(i, e.target.value)}
            className="predict-input"
            placeholder={`Sensor ${i + 1}`}
          />
        ))}
      </div>

      <button onClick={handlePredict} className="btn btn-green">
        Predict
      </button>

      {result && (
        <div className="predict-result">
          <p><strong>Prediction:</strong> {result.prediction}</p>
          <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};

export default Predict;
