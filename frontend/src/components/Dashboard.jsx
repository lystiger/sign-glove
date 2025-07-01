import React from 'react';

const Dashboard = () => {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Welcome to the Sign Glove AI Dashboard</h2>
      
      <div className="bg-white p-4 rounded shadow text-gray-700">
        <p className="text-lg font-semibold mb-2">Project Overview</p>
        <p>
          This project enables real-time sign language translation using a smart glove
          equipped with flex sensors and an IMU. The system collects gesture data,
          trains machine learning models, and allows uploading, managing, and testing gesture datasets.
        </p>
        <p className="mt-2">
          Use the navigation above to upload training data, manage gestures, and view AI training results.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
