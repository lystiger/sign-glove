import React, { useEffect, useState, useRef } from 'react';
import './styling/LivePredict.css';

const LivePredict = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [muted, setMuted] = useState(false);
  const [streaming, setStreaming] = useState(true);
  const [sensorData, setSensorData] = useState(null);
  const ws = useRef(null);
  const prevPrediction = useRef('');

  // Generate simulated sensor data
  const generateDummySensorData = () => {
    const randArray = () => Array.from({ length: 11 }, () => Math.random());
    return {
      left: randArray(),
      right: randArray(),
      timestamp: Date.now()
    };
  };

  // Text-to-Speech function
  const speakText = (text) => {
    if (muted) return;
    const synth = window.speechSynthesis;
    const utter = new SpeechSynthesisUtterance(text);
    synth.cancel(); // Stop ongoing speech
    synth.speak(utter);
  };

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8080/ws/predict');

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setLoading(false);
      setConnected(true);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const newPrediction = data.prediction;

      if (newPrediction && newPrediction !== prevPrediction.current) {
        speakText(newPrediction);
        prevPrediction.current = newPrediction;
      }

      setPrediction(newPrediction);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setLoading(false);
    };

    ws.current.onclose = () => {
      console.log('WebSocket closed');
      setConnected(false);
    };

    const gloveSocket = new WebSocket('ws://localhost:8080/ws/glove'); // <- your real sensor stream

  gloveSocket.onmessage = (event) => {
    const realSensorData = JSON.parse(event.data); // { left: [...], right: [...], timestamp: ... }
    setSensorData(realSensorData);

    if (ws.current?.readyState === WebSocket.OPEN && streaming) {
      ws.current.send(JSON.stringify(realSensorData)); // Send to prediction socket
    }
  };

  return () => {
    gloveSocket.close();
  };
}, [streaming]);

  return (
    <div className="live-container">
      <h2 className="live-title">
        Live Prediction <span className="pulse-dot" title="Streaming active" />
      </h2>

      <div className="prediction-display">
        {loading && <p className="loading-text">Connecting to server...</p>}

        {!loading && prediction && (
          <div className="prediction-box">
            <p><strong>Prediction:</strong> {prediction}</p>
          </div>
        )}

        {!loading && !prediction && (
          <p className="no-data">No prediction received yet.</p>
        )}
      </div>

      <div className="controls">
        <p className="status-text">
          Status: {connected ? "🟢 Connected" : "🔴 Disconnected"}
        </p>
        <div className="button-group">
          <button onClick={() => setMuted(!muted)}>
            {muted ? "🔇 Unmute TTS" : "🔊 Mute TTS"}
          </button>
          <button onClick={() => setStreaming(!streaming)}>
            {streaming ? "⏸️ Stop Streaming" : "▶️ Start Streaming"}
          </button>
        </div>
      </div>

      {sensorData && (
        <div className="sensor-preview">
          <p><strong>Last Sensor Data:</strong></p>
          <pre>{JSON.stringify(sensorData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default LivePredict;
