import React, { useState } from 'react';
import axios from 'axios';

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
      const res = await axios.post('http://localhost:8000/predict', { values });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Prediction failed.");
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Predict Gesture</h2>

      <div className="grid grid-cols-3 gap-2 mb-4">
        {values.map((val, i) => (
          <input
            key={i}
            type="number"
            value={val}
            onChange={(e) => handleChange(i, e.target.value)}
            className="border px-2 py-1 rounded"
            placeholder={`Sensor ${i + 1}`}
          />
        ))}
      </div>

      <button
        onClick={handlePredict}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
      >
        Predict
      </button>

      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded shadow">
          <p><strong>Prediction:</strong> {result.prediction}</p>
          <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};

export default Predict;
