import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer
} from 'recharts';
import './styling/TrainingResult.css'; // Create this for custom styles

const TrainingResults = () => {
  const [result, setResult] = useState(null);
  const [training, setTraining] = useState(false);
  const [trainStatus, setTrainStatus] = useState('');

  useEffect(() => {
    axios.get('http://localhost:8080/training/latest')
      .then((res) => setResult(res.data))
      .catch((err) => console.error('Failed to fetch training result:', err));
  }, []);

  const handleManualTrain = async () => {
    setTraining(true);
    setTrainStatus('Training in progress...');
    try {
      const res = await axios.post('http://localhost:8000/training/trigger');
      setTrainStatus('✅ Training complete!');
      // Optionally refresh results
      axios.get('http://localhost:8080/training/latest')
        .then((res) => setResult(res.data));
    } catch (err) {
      setTrainStatus('❌ Training failed. See logs.');
    } finally {
      setTraining(false);
    }
  };

  if (!result) {
    return <p>Loading training results...</p>;
  }

  const accuracyData = result.accuracies?.map((val, i) => ({
    epoch: i + 1,
    acc: val
  })) || [];

  const matrix = result.confusion_matrix || [];
  const labels = result.labels || [];

  return (
    <div className="training-container">
      <h2 className="title">📊 Training Results</h2>
      <button
        onClick={handleManualTrain}
        disabled={training}
        className="manual-train-btn"
        style={{ marginBottom: '1rem' }}
      >
        {training ? 'Training...' : 'Manual Training'}
      </button>
      {trainStatus && <p style={{ marginBottom: '1rem' }}>{trainStatus}</p>}
      <p><strong>Final Accuracy:</strong> {Math.round(result.accuracy * 100)}%</p>
      <p><strong>Session:</strong> {result.session_id}</p>
      <p><strong>Date:</strong> {new Date(result.timestamp).toLocaleString()}</p>

      <div className="chart-section">
        <h3>Accuracy Over Epochs</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={accuracyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="epoch" />
            <YAxis domain={[0, 1]} />
            <Tooltip />
            <Line type="monotone" dataKey="acc" stroke="#2563eb" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="matrix-section">
        <h3>Confusion Matrix</h3>
        <table className="confusion-matrix">
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
                  <td key={j} style={{ backgroundColor: val > 0 ? '#dbeafe' : '#f9fafb' }}>
                    {val}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TrainingResults;
