import React, { useState, useRef } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { MdLink, MdSend } from 'react-icons/md';

const LivePredict = () => {
  const [prediction, setPrediction] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const [showCheckmark, setShowCheckmark] = useState(false);

  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close();
    const ws = new window.WebSocket('ws://localhost:8080/ws/predict');
    wsRef.current = ws;
    ws.onopen = () => {
      setConnected(true);
      toast.success('WebSocket connected!');
      setShowCheckmark(true);
      setTimeout(() => setShowCheckmark(false), 1200);
    };
    ws.onclose = () => {
      setConnected(false);
      toast.info('WebSocket disconnected.');
    };
    ws.onerror = (e) => {
      toast.error('WebSocket error.');
    };
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setPrediction(data.prediction || data);
      } catch (err) {
        toast.error('Failed to parse prediction message.');
      }
    };
  };

  const sendTestData = () => {
    if (!wsRef.current || wsRef.current.readyState !== 1) {
      toast.error('WebSocket not connected.');
      return;
    }
    // Example test data
    wsRef.current.send(
      JSON.stringify({
        left: Array(11).fill(0.1),
        right: Array(11).fill(0.2),
        timestamp: Date.now(),
      })
    );
  };

  return (
    <div role="main" aria-label="Live Prediction Page">
      <div className="card fade-in">
        <h2 id="live-prediction-title" tabIndex={0}>Live Prediction</h2>
        <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem' }}>
          <button className="btn btn-primary" onClick={connectWebSocket} disabled={connected} aria-label="Connect to WebSocket" aria-busy={connected}>
            <MdLink style={{ verticalAlign: 'middle', marginRight: 4 }} /> Connect
          </button>
          {showCheckmark && (
            <span className="checkmark-success" aria-label="Success" style={{ marginLeft: 12, verticalAlign: 'middle' }}></span>
          )}
          <button className="btn btn-primary" onClick={sendTestData} disabled={!connected} aria-label="Send test data to WebSocket">
            <MdSend style={{ verticalAlign: 'middle', marginRight: 4 }} /> Send Test Data
          </button>
        </div>
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

export default LivePredict;
