import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import { apiRequest } from '../api';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar
} from 'recharts';
import './styling/TrainingResult.css';

const TrainingResults = () => {
  const [result, setResult] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [training, setTraining] = useState(false);
  const [trainStatus, setTrainStatus] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [showCheckmark, setShowCheckmark] = useState(false);

  useEffect(() => {
    fetchLatestResults();
  }, []);

  const fetchLatestResults = async () => {
    setLoading(true);
    try {
      // Fetch basic training result
      const resultRes = await apiRequest('get', '/training/latest');
      setResult(resultRes.data);
      
      // Fetch detailed metrics
      const metricsRes = await apiRequest('get', '/training/metrics/latest');
      setMetrics(metricsRes.data.data);
    } catch (err) {
      toast.error(`Failed to fetch training results: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  const handleManualTrain = async () => {
    setActionLoading(true);
    setTrainStatus('Training in progress...');
    try {
      await apiRequest('post', '/training/trigger');
      toast.success('Training triggered!');
      setShowCheckmark(true);
      setTimeout(() => setShowCheckmark(false), 1200);
      // Refresh results after training
      setTimeout(fetchLatestResults, 2000);
    } catch (err) {
      toast.error(`Failed to trigger training: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setActionLoading(false);
    }
  };

  if (!result) {
    return <p>Loading training results...</p>;
  }

  const accuracyData = metrics?.training_history?.accuracy?.map((val, i) => ({
    epoch: i + 1,
    accuracy: val,
    val_accuracy: metrics.training_history.val_accuracy[i],
    loss: metrics.training_history.loss[i],
    val_loss: metrics.training_history.val_loss[i]
  })) || [];

  const matrix = metrics?.confusion_matrix || [];
  const labels = metrics?.labels || [];

  // Prepare ROC curve data
  const rocData = metrics?.roc_curves ? Object.keys(metrics.roc_curves.fpr).map(key => {
    if (key === 'micro') return null;
    const fpr = metrics.roc_curves.fpr[key];
    const tpr = metrics.roc_curves.tpr[key];
    const auc = metrics.roc_curves.auc[key];
    return {
      label: labels[parseInt(key)] || `Class ${key}`,
      fpr: fpr,
      tpr: tpr,
      auc: auc
    };
  }).filter(Boolean) : [];

  return (
    <div className="training-container" role="main" aria-label="Training Results Page">
      <div className="card fade-in" style={{ marginBottom: '2rem' }}>
        <h2 className="title" id="training-results-title" tabIndex={0}>📊 Training Results</h2>
        <button
          onClick={handleManualTrain}
          disabled={actionLoading}
          className="btn btn-primary"
          style={{ marginBottom: '1rem' }}
          aria-busy={actionLoading}
          aria-label="Trigger manual training"
        >
          {actionLoading ? 'Training...' : 'Manual Training'}
        </button>
        {showCheckmark && (
          <span className="checkmark-success" aria-label="Success" style={{ marginLeft: 12, verticalAlign: 'middle' }}></span>
        )}
        {trainStatus && <p style={{ marginBottom: '1rem' }} aria-live="polite">{trainStatus}</p>}
        <nav className="tab-navigation" aria-label="Training Results Tabs" style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <button
            className={`btn btn-secondary${activeTab === 'overview' ? ' btn-primary' : ''}`}
            onClick={() => setActiveTab('overview')}
            aria-selected={activeTab === 'overview'}
            aria-controls="overview-section"
          >
            Overview
          </button>
          <button
            className={`btn btn-secondary${activeTab === 'metrics' ? ' btn-primary' : ''}`}
            onClick={() => setActiveTab('metrics')}
            aria-selected={activeTab === 'metrics'}
            aria-controls="metrics-section"
          >
            Detailed Metrics
          </button>
          <button
            className={`btn btn-secondary${activeTab === 'visualizations' ? ' btn-primary' : ''}`}
            onClick={() => setActiveTab('visualizations')}
            aria-selected={activeTab === 'visualizations'}
            aria-controls="visualizations-section"
          >
            Visualizations
          </button>
        </nav>
      </div>
      <div className="card fade-in">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-section" id="overview-section" aria-labelledby="training-results-title">
            <div className="metrics-grid">
              <div className="metric-card">
                <h3>Final Accuracy</h3>
                <p className="metric-value">{Math.round(result.accuracy * 100)}%</p>
              </div>
              <div className="metric-card">
                <h3>Session ID</h3>
                <p className="metric-value">{result.session_id}</p>
              </div>
              <div className="metric-card">
                <h3>Training Date</h3>
                <p className="metric-value">{new Date(result.timestamp).toLocaleString()}</p>
              </div>
              {metrics && (
                <div className="metric-card">
                  <h3>Loss</h3>
                  <p className="metric-value">{(metrics.loss * 100).toFixed(2)}%</p>
                </div>
              )}
            </div>
            <div className="chart-section">
              <h3>Training Progress</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={accuracyData} aria-label="Training Progress Chart">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="epoch" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="accuracy" stroke="#2563eb" strokeWidth={2} name="Training Accuracy" />
                  <Line type="monotone" dataKey="val_accuracy" stroke="#dc2626" strokeWidth={2} name="Validation Accuracy" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
        {/* Detailed Metrics Tab */}
        {activeTab === 'metrics' && metrics && (
          <div className="metrics-section" id="metrics-section" aria-labelledby="training-results-title">
            <div className="confusion-matrix-section">
              <h3>Confusion Matrix</h3>
              <div className="matrix-container">
                <table className="confusion-matrix" aria-label="Confusion Matrix">
                  <thead>
                    <tr>
                      <th>True \ Pred</th>
                      {labels.map((label, i) => <th key={i}>{label}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {matrix.map((row, i) => (
                      <tr key={i}>
                        <th>{labels[i]}</th>
                        {row.map((val, j) => (
                          <td
                            key={j}
                            style={{
                              backgroundColor: val > 0 ? `rgba(37, 99, 235, ${Math.min(val / Math.max(...row), 0.8)})` : '#f9fafb',
                              color: val > 0 ? 'white' : 'black'
                            }}
                          >
                            {val}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            {metrics.classification_report && (
              <div className="classification-report">
                <h3>Classification Report</h3>
                <div className="report-grid">
                  {Object.keys(metrics.classification_report).map(key => {
                    if (key === 'accuracy') return null;
                    const report = metrics.classification_report[key];
                    if (typeof report === 'object') {
                      return (
                        <div key={key} className="report-card">
                          <h4>{key}</h4>
                          <p>Precision: {(report.precision * 100).toFixed(1)}%</p>
                          <p>Recall: {(report.recall * 100).toFixed(1)}%</p>
                          <p>F1-Score: {(report['f1-score'] * 100).toFixed(1)}%</p>
                          <p>Support: {report.support}</p>
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              </div>
            )}
          </div>
        )}
        {/* Visualizations Tab */}
        {activeTab === 'visualizations' && (
          <div className="visualizations-section" id="visualizations-section" aria-labelledby="training-results-title">
            <div className="viz-grid">
              <div className="viz-card">
                <h3>Confusion Matrix Heatmap</h3>
                <img
                  src="http://localhost:8000/training/visualizations/confusion_matrix"
                  alt="Confusion Matrix"
                  className="viz-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <p style={{ display: 'none', color: '#666' }}>Confusion matrix not available. Run training first.</p>
              </div>
              <div className="viz-card">
                <h3>ROC Curves</h3>
                <img
                  src="http://localhost:8000/training/visualizations/roc_curves"
                  alt="ROC Curves"
                  className="viz-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <p style={{ display: 'none', color: '#666' }}>ROC curves not available. Run training first.</p>
              </div>
              <div className="viz-card">
                <h3>Training History</h3>
                <img
                  src="http://localhost:8000/training/visualizations/training_history"
                  alt="Training History"
                  className="viz-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <p style={{ display: 'none', color: '#666' }}>Training history not available. Run training first.</p>
              </div>
            </div>
            {rocData.length > 0 && (
              <div className="roc-curves-interactive">
                <h3>Interactive ROC Curves</h3>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={rocData[0]?.fpr.map((fpr, i) => ({ fpr, tpr: rocData[0]?.tpr[i] }))} aria-label="ROC Curve Chart">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fpr" domain={[0, 1]} />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    {rocData.map((curve, index) => (
                      <Area
                        key={index}
                        type="monotone"
                        dataKey="tpr"
                        stroke={`hsl(${index * 60}, 70%, 50%)`}
                        fill={`hsl(${index * 60}, 70%, 50%)`}
                        fillOpacity={0.3}
                        name={`${curve.label} (AUC: ${curve.auc.toFixed(2)})`}
                      />
                    ))}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainingResults;
