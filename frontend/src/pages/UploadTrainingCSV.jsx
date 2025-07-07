// src/pages/UploadTrainingCSV.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './styling/UploadTraining.css';

export default function UploadTrainingCSV() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file.');
      return;
    }

    setError('');
    setStatus('Uploading...');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8080/training/upload', formData);
      setStatus(`✅ Uploaded: ${res.data.message || 'Success'}`);
    } catch (err) {
      console.error(err);
      setStatus('');
      setError('Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-training-container">
      <h2 className="upload-training-title">Upload Training CSV</h2>

      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
        className="upload-input"
      />

      {error && <p className="upload-error">{error}</p>}
      {status && <p className="upload-status">{status}</p>}

      <button
        onClick={handleUpload}
        disabled={loading}
        className={`upload-button ${loading ? 'upload-button-disabled' : ''}`}
      >
        {loading ? 'Uploading...' : 'Upload'}
      </button>
    </div>
  );
}
