import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { apiRequest } from '../api';
import './styling/CSVManager.css';

const CSVManager = () => {
  const [rawCsvFile, setRawCsvFile] = useState(null);
  const [trainingCsvFile, setTrainingCsvFile] = useState(null);
  const [uploadingRaw, setUploadingRaw] = useState(false);
  const [uploadingTraining, setUploadingTraining] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState('idle');
  const [trainingProgress, setTrainingProgress] = useState('');
  const [trainingResults, setTrainingResults] = useState([]);
  const [trainingMetrics, setTrainingMetrics] = useState(null);
  const [modelStatus, setModelStatus] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInitialData();
    const interval = setInterval(() => {
      if (trainingStatus === 'running') {
        checkTrainingProgress();
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [trainingStatus]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadTrainingResults(),
        loadLatestMetrics(),
        checkModelStatus()
      ]);
    } catch (err) {
      console.error('Error loading initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTrainingResults = async () => {
    try {
      const response = await apiRequest('get', '/training/');
      setTrainingResults(response.data || []);
    } catch (err) {
      console.error('Error loading training results:', err);
    }
  };

  const loadLatestTrainingResult = async () => {
    try {
      const response = await apiRequest('get', '/training/latest');
      setLatestResult(response.data);
    } catch (err) {
      // Handle expected errors gracefully
      if (err.status === 404) {
        console.log('No training results found yet - this is normal for fresh installations');
        setLatestResult(null);
      } else if (err.status === 503) {
        console.log('Database connection not available - running in standalone mode');
        setLatestResult(null);
      } else {
        console.error('Error loading training results:', err);
        setLatestResult(null);
      }
    }
  };

  const loadLatestMetrics = async () => {
    try {
      const response = await apiRequest('get', '/training/metrics/latest');
      setTrainingMetrics(response.data);
    } catch (err) {
      // Metrics might not exist if no training has been run yet - this is expected
      if (err.status === 404) {
        console.log('No training metrics found yet - this is normal if no training has been completed');
      } else {
        console.error('Error loading metrics:', err);
      }
      setTrainingMetrics(null);
    }
  };

  const checkModelStatus = async () => {
    try {
      // Check if models exist by trying to make a prediction
      const response = await apiRequest('get', '/predict/live');
      setModelStatus({
        singleHand: true,
        dualHand: response.model_type === 'dual_hand',
        lastUpdated: new Date().toISOString()
      });
    } catch (err) {
      // Models might not exist if no training has been run yet - this is expected
      if (err.status === 404) {
        console.log('No trained models found yet - upload training data to create models');
      } else {
        console.error('Error checking model status:', err);
      }
      setModelStatus({
        singleHand: false,
        dualHand: false,
        lastUpdated: new Date().toISOString(),
        error: err.detail || 'No trained models available'
      });
    }
  };

  const checkTrainingProgress = async () => {
    try {
      const response = await apiRequest('get', '/utils/training/logs');
      setTrainingProgress(response.lines?.join('') || '');
      
      // Check if training completed
      if (response.lines?.join('').includes('Training finished')) {
        setTrainingStatus('completed');
        await loadTrainingResults();
        await loadLatestMetrics();
        await checkModelStatus();
        toast.success('Training completed successfully!');
      }
    } catch (err) {
      console.error('Error checking training progress:', err);
    }
  };

  const handleRawCsvUpload = async () => {
    if (!rawCsvFile) {
      toast.error('Please select a CSV file first');
      return;
    }

    try {
      setUploadingRaw(true);
      const formData = new FormData();
      formData.append('file', rawCsvFile);

      const response = await apiRequest('post', '/gestures/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 'success') {
        toast.success(`Uploaded ${response.rows_processed} rows of raw sensor data`);
        setRawCsvFile(null);
        const fileInput = document.getElementById('raw-csv-input');
        if (fileInput) {
          fileInput.value = '';
        }
      }
    } catch (err) {
      toast.error(`Raw CSV upload failed: ${err.detail || err.message}`);
    } finally {
      setUploadingRaw(false);
    }
  };

  const handleTrainingCsvUpload = async () => {
    if (!trainingCsvFile) {
      toast.error('Please select a training CSV file first');
      return;
    }

    try {
      setUploadingTraining(true);
      setTrainingStatus('running');
      const formData = new FormData();
      formData.append('file', trainingCsvFile);

      const response = await apiRequest('post', '/training/run', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 'started') {
        toast.success('Training started! Monitor progress below.');
        setTrainingCsvFile(null);
        const fileInput = document.getElementById('training-csv-input');
        if (fileInput) {
          fileInput.value = '';
        }
      }
    } catch (err) {
      toast.error(`Training CSV upload failed: ${err.detail || err.message}`);
      setTrainingStatus('idle');
    } finally {
      setUploadingTraining(false);
    }
  };

  const triggerTrainingFromDatabase = async () => {
    try {
      setTrainingStatus('running');
      const response = await apiRequest('post', '/training/trigger');
      
      if (response.status === 'started') {
        toast.success('Training started using database data!');
      }
    } catch (err) {
      toast.error(`Training trigger failed: ${err.detail || err.message}`);
      setTrainingStatus('idle');
    }
  };

  const exportGestureData = async () => {
    try {
      const response = await apiRequest('get', '/gestures/export', null, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'gesture_data.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Gesture data exported successfully!');
    } catch (err) {
      toast.error(`Export failed: ${err.detail || err.message}`);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="csv-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading CSV Manager...</p>
        </div>
      </div>
    );
  }

  return (
    <div role="main" aria-label="CSV & Training Manager">
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h1>CSV & Training Manager</h1>
        <p>Upload CSV files, manage training, and monitor AI model status</p>
      </div>

      {/* Model Status Section */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2>Model Status</h2>
        <div className="model-status-grid">
          <div className={`model-card ${modelStatus.singleHand ? 'active' : 'inactive'}`}>
            <div className="model-icon"></div>
            <div className="model-info">
              <h3>Single Hand Model</h3>
              <p className="status">{modelStatus.singleHand ? 'Available' : 'Not Available'}</p>
              {modelStatus.error && <p className="error">{modelStatus.error}</p>}
            </div>
          </div>
          <div className={`model-card ${modelStatus.dualHand ? 'active' : 'inactive'}`}>
            <div className="model-icon"></div>
            <div className="model-info">
              <h3>Dual Hand Model</h3>
              <p className="status">{modelStatus.dualHand ? 'Available' : 'Not Available'}</p>
              <p className="last-updated">Last checked: {formatTimestamp(modelStatus.lastUpdated)}</p>
            </div>
          </div>
        </div>
        <button className="refresh-btn" onClick={checkModelStatus}>
          🔄 Refresh Status
        </button>
      </div>

      {/* CSV Upload Section */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2>CSV File Management</h2>
        
        {/* Raw Data Upload */}
        <div className="upload-card">
          <h3>Raw Sensor Data Upload</h3>
          <p>Upload raw sensor data CSV files to the database for future training</p>
          <div className="upload-controls">
            <input
              id="raw-csv-input"
              type="file"
              accept=".csv"
              onChange={(e) => setRawCsvFile(e.target.files[0])}
              className="file-input"
            />
            <button
              onClick={handleRawCsvUpload}
              disabled={!rawCsvFile || uploadingRaw}
              className="upload-btn"
            >
              {uploadingRaw ? 'Uploading...' : 'Upload Raw Data'}
            </button>
          </div>
          {rawCsvFile && (
            <div className="file-info">
              <p>Selected: {rawCsvFile.name} ({(rawCsvFile.size / 1024).toFixed(2)} KB)</p>
            </div>
          )}
        </div>

        {/* Training Data Upload */}
        <div className="upload-card">
          <h3>Training Data Upload</h3>
          <p>Upload gesture.csv file to train a new AI model (100 epochs)</p>
          <div className="upload-controls">
            <input
              id="training-csv-input"
              type="file"
              accept=".csv"
              onChange={(e) => setTrainingCsvFile(e.target.files[0])}
              className="file-input"
            />
            <button
              onClick={handleTrainingCsvUpload}
              disabled={!trainingCsvFile || uploadingTraining || trainingStatus === 'running'}
              className="upload-btn primary"
            >
              {uploadingTraining ? 'Starting Training...' : 'Upload & Train Model'}
            </button>
          </div>
          {trainingCsvFile && (
            <div className="file-info">
              <p>Selected: {trainingCsvFile.name} ({(trainingCsvFile.size / 1024).toFixed(2)} KB)</p>
            </div>
          )}
        </div>

        {/* Database Training */}
        <div className="upload-card">
          <h3>Train from Database</h3>
          <p>Use existing sensor data from database to train a new model</p>
          <div className="upload-controls">
            <button
              onClick={triggerTrainingFromDatabase}
              disabled={trainingStatus === 'running'}
              className="upload-btn secondary"
            >
              Train from Database
            </button>
            <button
              onClick={exportGestureData}
              className="export-btn"
            >
              Export Database CSV
            </button>
          </div>
        </div>
      </div>

      {/* Training Progress Section */}
      {trainingStatus !== 'idle' && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2>Training Progress</h2>
          <div className="training-status">
            <div className={`status-indicator ${trainingStatus}`}>
              {trainingStatus === 'running' && <div className="spinner-small"></div>}
              <span className="status-text">
                {trainingStatus === 'running' ? 'Training in Progress...' : 
                 trainingStatus === 'completed' ? 'Training Completed' : 'Training Status'}
              </span>
            </div>
          </div>
          {trainingProgress && (
            <div className="training-logs">
              <h3>Training Logs</h3>
              <pre className="logs-content">{trainingProgress}</pre>
            </div>
          )}
        </div>
      )}

      {/* Training Metrics Section */}
      {trainingMetrics && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2>Latest Training Metrics</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Accuracy</h3>
              <p className="metric-value">{(trainingMetrics.accuracy * 100).toFixed(2)}%</p>
            </div>
            <div className="metric-card">
              <h3>Loss</h3>
              <p className="metric-value">{trainingMetrics.loss.toFixed(4)}</p>
            </div>
            <div className="metric-card">
              <h3>Classes</h3>
              <p className="metric-value">{trainingMetrics.labels?.length || 0}</p>
            </div>
          </div>
          
          {trainingMetrics.labels && (
            <div className="labels-section">
              <h3>Trained Labels</h3>
              <div className="labels-list">
                {trainingMetrics.labels.map((label, index) => (
                  <span key={index} className="label-tag">{label}</span>
                ))}
              </div>
            </div>
          )}

          <div className="visualizations-section">
            <h3>Training Visualizations</h3>
            <div className="viz-buttons">
              <button onClick={() => window.open('/api/training/visualizations/confusion_matrix', '_blank')}>
                Confusion Matrix
              </button>
              <button onClick={() => window.open('/api/training/visualizations/roc_curves', '_blank')}>
                ROC Curves
              </button>
              <button onClick={() => window.open('/api/training/visualizations/training_history', '_blank')}>
                Training History
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Training History Section */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h2>Training History</h2>
        {trainingResults.length > 0 ? (
          <div className="history-table">
            <table>
              <thead>
                <tr>
                  <th>Session ID</th>
                  <th>Timestamp</th>
                  <th>Accuracy</th>
                  <th>Model Name</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {trainingResults.slice(0, 10).map((result) => (
                  <tr key={result.session_id}>
                    <td className="session-id">{result.session_id.substring(0, 8)}...</td>
                    <td>{formatTimestamp(result.timestamp)}</td>
                    <td className="accuracy">{(result.accuracy * 100).toFixed(2)}%</td>
                    <td>{result.model_name || 'N/A'}</td>
                    <td>{result.notes || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-history">
            <p>No training history found. Start training to see results here.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CSVManager;
