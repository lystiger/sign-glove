// src/pages/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import { apiRequest } from '../api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await apiRequest('get', '/dashboard/');
      setStats(res.data);
    } catch (err) {
      toast.error(`Failed to fetch dashboard stats: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div role="main" aria-label="Dashboard Page">
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2 id="dashboard-title" tabIndex={0}>Sign Glove Project Dashboard</h2>
        <p style={{ marginTop: 8, color: '#555' }}>
          <strong>Sign Glove</strong> is a smart wearable system for translating hand gestures into text and speech using flex sensors, IMU, machine learning, and a web interface. This dashboard provides a quick overview and access to key utilities.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <h3>Project Statistics</h3>
        {loading ? (
          <ul aria-busy="true" aria-live="polite">
            <li><Skeleton width={200} /></li>
            <li><Skeleton width={200} /></li>
            <li><Skeleton width={200} /></li>
            <li><Skeleton width={200} /></li>
          </ul>
        ) : stats && (
          <ul aria-label="Dashboard statistics">
            <li>Total Sessions: {stats.total_sessions || stats.totalSessions}</li>
            <li>Total Models: {stats.total_models || stats.totalModels}</li>
            <li>Average Accuracy: {stats.average_accuracy || stats.averageAccuracy}</li>
            <li>Last Activity: {stats.last_activity || stats.lastActivity}</li>
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
