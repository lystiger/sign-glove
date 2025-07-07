// src/pages/UploadCSV.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './styling/UploadCSV.css';

const UploadCSV = () => {
  const [file, setFile] = useState(null);
  const [label, setLabel] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a CSV file.');
      return;
    }
    if (!label.trim()) {
      setError('Please enter a label.');
      return;
    }

    setError('');
    setStatus('Uploading...');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('label', label);

    try {
      const response = await axios.post('http://localhost:8080/gestures/upload-csv', formData);
      setStatus(`Upload successful: ${response.data.message}`);
    } catch (err) {
      console.error(err);
      setStatus('');
      setError('Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <h2 className="form-title">Upload Gesture CSV</h2>

      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
        className="form-input"
      />

      <input
        type="text"
        placeholder="Gesture Label"
        value={label}
        onChange={(e) => setLabel(e.target.value)}
        className="form-input"
      />

      {error && <p className="form-error">{error}</p>}
      {status && <p className="form-success">{status}</p>}

      <button
        type="submit"
        disabled={loading}
        className={`btn ${loading ? 'btn-disabled' : 'btn-blue'}`}
      >
        {loading ? 'Uploading...' : 'Upload'}
      </button>
    </form>
  );
};

export default UploadCSV;
