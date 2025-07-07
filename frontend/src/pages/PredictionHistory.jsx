import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './styling/PredictionHistory.css'; // optional styling

const PredictionHistory = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8080/predict/predictions')
      .then(res => setPredictions(res.data))
      .catch(err => console.error('Failed to load predictions:', err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="prediction-history">
      <h2 className="title">🕒 Prediction History</h2>
      {loading ? (
        <p>Loading...</p>
      ) : predictions.length === 0 ? (
        <p>No predictions found.</p>
      ) : (
        <table className="history-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Prediction</th>
              <th>Confidence</th>
              <th>Left</th>
              <th>Right</th>
              <th>IMU</th>
            </tr>
          </thead>
          <tbody>
            {predictions.map((pred, idx) => (
              <tr key={idx}>
                <td>{new Date(pred.timestamp).toLocaleTimeString()}</td>
                <td>{pred.prediction}</td>
                <td>{pred.confidence ? (pred.confidence * 100).toFixed(1) + '%' : '–'}</td>
                <td><code>{pred.left?.map(v => v.toFixed(2)).join(', ')}</code></td>
                <td><code>{pred.right?.map(v => v.toFixed(2)).join(', ')}</code></td>
                <td>{pred.imu?.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default PredictionHistory;
