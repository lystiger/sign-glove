import React, { useEffect, useState } from 'react';
import axios from 'axios';

const LivePredict = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      axios.get('http://localhost:8000/predict/live')
        .then(res => {
          setPrediction(res.data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Live prediction error:", err);
          setPrediction(null);
          setLoading(false);
        });
    }, 2000); // fetch every 2 seconds

    return () => clearInterval(interval); // cleanup on unmount
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Live Prediction</h2>

      {loading && <p>Loading...</p>}
      {!loading && prediction && prediction.status === "success" && (
        <div>
          <p><strong>Prediction:</strong> {prediction.prediction}</p>
          <p><strong>Confidence:</strong> {(prediction.confidence * 100).toFixed(2)}%</p>
          <p><strong>From session:</strong> {prediction.source_session}</p>
          <p><strong>Timestamp:</strong> {new Date(prediction.timestamp).toLocaleString()}</p>
        </div>
      )}

      {!loading && !prediction && <p>No prediction available.</p>}
    </div>
  );
};

export default LivePredict;
