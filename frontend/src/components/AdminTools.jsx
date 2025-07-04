import React from 'react';
import axios from 'axios';

const AdminTools = () => {
  const clearSensorData = async () => {
    try {
      const res = await axios.delete('http://localhost:8000/admin/sensor-data');
      alert(`Deleted ${res.data.deleted} sensor entries`);
    } catch (err) {
      console.error(err);
      alert("Failed to clear sensor data");
    }
  };

  const clearTrainingResults = async () => {
    try {
      const res = await axios.delete('http://localhost:8000/admin/training-results');
      alert(`Deleted ${res.data.deleted} training results`);
    } catch (err) {
      console.error(err);
      alert("Failed to clear training results");
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Admin Tools</h2>
      <button onClick={clearSensorData} className="mr-4 px-4 py-2 bg-red-600 text-white rounded">
        Clear Sensor Data
      </button>
      <button onClick={clearTrainingResults} className="px-4 py-2 bg-red-600 text-white rounded">
        Clear Training Results
      </button>
    </div>
  );
};

export default AdminTools;
