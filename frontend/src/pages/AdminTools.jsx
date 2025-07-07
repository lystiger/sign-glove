// src/pages/AdminTools.jsx
import React from 'react';
import axios from 'axios';
import './styling/Admin.css';

const AdminTools = () => {
  const clearSensorData = async () => {
    try {
      const res = await axios.delete('http://localhost:8080/admin/sensor-data');
      alert(`Deleted ${res.data.deleted} sensor entries`);
    } catch (err) {
      console.error(err);
      alert("Failed to clear sensor data");
    }
  };

  const clearTrainingResults = async () => {
    try {
      const res = await axios.delete('http://localhost:8080/admin/training-results');
      alert(`Deleted ${res.data.deleted} training results`);
    } catch (err) {
      console.error(err);
      alert("Failed to clear training results");
    }
  };

  return (
    <div className="admin-container">
      <h2 className="admin-title">Admin Tools</h2>
      <div className="admin-buttons">
        <button onClick={clearSensorData} className="btn btn-danger">
          Clear Sensor Data
        </button>
        <button onClick={clearTrainingResults} className="btn btn-danger">
          Clear Training Results
        </button>
      </div>
    </div>
  );
};

export default AdminTools;
