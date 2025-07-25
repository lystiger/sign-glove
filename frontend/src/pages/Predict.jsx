// src/pages/Predict.jsx
import React, { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { apiRequest } from '../api';
import { MdPlayArrow } from 'react-icons/md';

const Predict = () => {
  const [input, setInput] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCheckmark, setShowCheckmark] = useState(false);

  const handlePredict = async () => {
    const values = input
      .split(',')
      .map((v) => parseFloat(v.trim()))
      .filter((v) => !isNaN(v));
    if (values.length !== 11) {
      toast.error('Input must be 11 numbers, comma-separated.');
      return;
    }
    setLoading(true);
    try {
      const res = await apiRequest('post', '/predict/', { values });
      setPrediction(res.prediction || res);
      toast.success('Prediction successful!');
      setShowCheckmark(true);
      setTimeout(() => setShowCheckmark(false), 1200);
    } catch (err) {
      toast.error(`Prediction failed: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div role="main" aria-label="Manual Prediction Page">
      <div className="card fade-in">
        <h2 id="manual-prediction-title" tabIndex={0}>Manual Prediction</h2>
        <label htmlFor="sensor-input" style={{ display: 'block', marginBottom: 8 }}>Comma-separated 11 sensor values</label>
        <input
          id="sensor-input"
          type="text"
          placeholder="Comma-separated 11 sensor values"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-required="true"
          aria-label="Sensor values input"
          style={{ marginBottom: 16 }}
        />
        <div style={{ marginTop: 20 }}>
          <button className="btn btn-primary" onClick={handlePredict} disabled={loading} aria-busy={loading} aria-label="Predict">
            <MdPlayArrow style={{ verticalAlign: 'middle', marginRight: 4 }} /> Predict
          </button>
          {showCheckmark && (
            <span className="checkmark-success" aria-label="Success" style={{ marginLeft: 12, verticalAlign: 'middle' }}></span>
          )}
        </div>
        {loading && <div aria-live="polite">Loading...</div>}
        {prediction && (
          <div style={{ marginTop: '1rem' }}>
            <h3>Prediction Result:</h3>
            <pre>{JSON.stringify(prediction, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default Predict;
