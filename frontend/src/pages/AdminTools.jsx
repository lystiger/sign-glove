// src/pages/AdminTools.jsx
import React, { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { apiRequest } from '../api';
import { MdDeleteForever } from 'react-icons/md';

const AdminTools = () => {
  const [showCheckmark, setShowCheckmark] = useState({ sensor: false, training: false });

  const handleClearSensorData = async () => {
    try {
      await apiRequest('delete', '/admin/sensor-data');
      toast.success('Sensor data cleared!');
    } catch (err) {
      toast.error(`Failed to clear sensor data: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    }
    setShowCheckmark(s => ({ ...s, sensor: true }));
    setTimeout(() => setShowCheckmark(s => ({ ...s, sensor: false })), 1200);
  };

  const handleClearTrainingResults = async () => {
    try {
      await apiRequest('delete', '/admin/training-results');
      toast.success('Training results cleared!');
    } catch (err) {
      toast.error(`Failed to clear training results: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    }
    setShowCheckmark(s => ({ ...s, training: true }));
    setTimeout(() => setShowCheckmark(s => ({ ...s, training: false })), 1200);
  };

  return (
    <div role="main" aria-label="Admin Tools Page" className="fade-in">
      <h2 id="admin-tools-title" tabIndex={0}>Admin Tools</h2>
      <div style={{ marginTop: 24, display: 'flex', gap: '1.5rem' }}>
        <button className="btn btn-danger" onClick={handleClearSensorData} aria-label="Clear sensor data">
          <MdDeleteForever style={{ verticalAlign: 'middle', marginRight: 4 }} /> Clear Sensor Data
        </button>
        {showCheckmark.sensor && (
          <span className="checkmark-success" aria-label="Success" style={{ marginLeft: 12, verticalAlign: 'middle' }}></span>
        )}
        <button className="btn btn-danger" onClick={handleClearTrainingResults} aria-label="Clear training results">
          <MdDeleteForever style={{ verticalAlign: 'middle', marginRight: 4 }} /> Clear Training Results
        </button>
        {showCheckmark.training && (
          <span className="checkmark-success" aria-label="Success" style={{ marginLeft: 12, verticalAlign: 'middle' }}></span>
        )}
      </div>
    </div>
  );
};

export default AdminTools;
