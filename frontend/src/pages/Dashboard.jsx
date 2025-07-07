// src/pages/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './styling/Dashboard.css'; // Add this

const Dashboard = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8080/dashboard')
      .then(res => setStats(res.data.data))
      .catch(err => {
        console.error("Dashboard fetch failed", err);
        setStats(null);
      });
  }, []);

  return (
    <div className="dashboard-container">
      <h2 className="dashboard-title">Welcome to the Sign Glove AI Dashboard</h2>

      <div className="card">
        <p className="card-title">Project Overview</p>
        <p>
          This project enables real-time sign language translation using a smart glove
          equipped with flex sensors and an IMU. The system collects gesture data,
          trains machine learning models, and allows uploading, managing, and testing gesture datasets.
        </p>
        <p className="mt">
          Use the navigation above to upload training data, manage gestures, and view AI training results.
        </p>
      </div>

      <div className="card">
        <p className="card-title">System Stats</p>
        {!stats ? (
          <p>Loading stats...</p>
        ) : (
          <ul className="stats-list">
            <li>Total Gesture Sessions: <strong>{stats.total_sessions}</strong></li>
            <li>Total Training Models: <strong>{stats.total_models}</strong></li>
            <li>Average Accuracy: <strong>{(stats.average_accuracy * 100).toFixed(2)}%</strong></li>
            <li>Last Activity: <strong>{new Date(stats.last_activity).toLocaleString()}</strong></li>
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
