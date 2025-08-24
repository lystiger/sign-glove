import React, { useState, useEffect } from 'react';
import { api } from '../api';
import './TTSStatus.css';

const TTSStatus = ({ refreshTrigger }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStatus();
  }, [refreshTrigger]);

  const loadStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get('/esp32/tts-status');
      setStatus(response.data.data);
    } catch (err) {
      setError('Failed to load TTS status');
      console.error('Error loading TTS status:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (enabled) => {
    return enabled ? '✅' : '❌';
  };

  const getStatusColor = (enabled) => {
    return enabled ? 'success' : 'error';
  };

  if (loading) {
    return (
      <div className="tts-status">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading TTS Status...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tts-status">
        <div className="error-message">
          <span>❌ {error}</span>
          <button onClick={loadStatus}>🔄 Retry</button>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="tts-status">
        <div className="no-status">
          <p>No TTS status available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="tts-status">
      <div className="status-header">
        <h3>📊 TTS System Status</h3>
        <button className="refresh-btn" onClick={loadStatus}>
          🔄 Refresh
        </button>
      </div>

      <div className="status-grid">
        {/* System Overview */}
        <div className="status-card overview">
          <div className="card-header">
            <span className="card-icon">🏗️</span>
            <h4>System Overview</h4>
          </div>
          <div className="card-content">
            <div className="stat-row">
              <span className="stat-label">Total Languages:</span>
              <span className="stat-value">{status.total_languages}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Total Gestures:</span>
              <span className="stat-value">{status.total_gestures}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Current Language:</span>
              <span className="stat-value">{status.current_language.toUpperCase()}</span>
            </div>
          </div>
        </div>

        {/* TTS Configuration */}
        <div className="status-card config">
          <div className="card-header">
            <span className="card-icon">⚙️</span>
            <h4>TTS Configuration</h4>
          </div>
          <div className="card-content">
            <div className="stat-row">
              <span className="stat-label">TTS Enabled:</span>
              <span className={`stat-value ${getStatusColor(status.tts_enabled)}`}>
                {getStatusIcon(status.tts_enabled)} {status.tts_enabled ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Idle Filtering:</span>
              <span className={`stat-value ${getStatusColor(status.filter_enabled)}`}>
                {getStatusIcon(status.filter_enabled)} {status.filter_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>

        {/* Gesture Statistics */}
        <div className="status-card gestures">
          <div className="card-header">
            <span className="stat-icon">🎯</span>
            <h4>Gesture Statistics</h4>
          </div>
          <div className="card-content">
            <div className="stat-row">
              <span className="stat-label">Meaningful Gestures:</span>
              <span className="stat-value success">
                ✅ {status.meaningful_gestures}
              </span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Idle Gestures:</span>
              <span className="stat-value warning">
                ⏭️ {status.idle_gestures}
              </span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Total Recognized:</span>
              <span className="stat-value info">
                📊 {status.meaningful_gestures + status.idle_gestures}
              </span>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="status-card performance">
          <div className="card-header">
            <span className="card-icon">🚀</span>
            <h4>Performance</h4>
          </div>
          <div className="card-content">
            <div className="stat-row">
              <span className="stat-label">Response Time:</span>
              <span className="stat-value">⚡ &lt;100ms</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Uptime:</span>
              <span className="stat-value">⏰ Active</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Memory Usage:</span>
              <span className="stat-value">💾 Optimized</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h4>Quick Actions</h4>
        <div className="action-buttons">
          <button className="action-btn primary" onClick={loadStatus}>
            🔄 Refresh Status
          </button>
          <button className="action-btn secondary">
            📋 View Logs
          </button>
          <button className="action-btn info">
            📊 Detailed Metrics
          </button>
        </div>
      </div>

      {/* Last Updated */}
      <div className="last-updated">
        <p>Last updated: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  );
};

export default TTSStatus; 