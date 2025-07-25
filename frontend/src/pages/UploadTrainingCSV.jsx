// src/pages/UploadTrainingCSV.jsx
import React, { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import { apiRequest } from '../api';
import { MdUpload } from 'react-icons/md';

const UploadTrainingCSV = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCheckmark, setShowCheckmark] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a CSV file to upload.');
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await apiRequest('post', '/training/run', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      toast.success('CSV uploaded and training started!');
      setShowCheckmark(true);
      setTimeout(() => setShowCheckmark(false), 1200);
    } catch (err) {
      toast.error(`Upload failed: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div role="main" aria-label="Upload Training CSV Page">
      <div className="card fade-in">
        <h2 id="upload-training-csv-title" tabIndex={0}>Upload Training CSV</h2>
        {loading ? (
          <>
            <Skeleton width={200} height={32} style={{ marginBottom: 8 }} />
            <Skeleton width={100} height={32} />
          </>
        ) : (
          <form aria-label="Upload Training CSV form" onSubmit={e => { e.preventDefault(); handleUpload(); }}>
            <label htmlFor="training-csv-file-input" style={{ display: 'block', marginBottom: 8 }}>Select CSV file</label>
            <input id="training-csv-file-input" type="file" accept=".csv" onChange={handleFileChange} aria-required="true" style={{ marginBottom: 16 }} />
            <div style={{ marginTop: 20 }}>
              <button type="submit" className="btn btn-primary" onClick={handleUpload} disabled={loading} aria-busy={loading} aria-label="Upload Training CSV">
                <MdUpload style={{ verticalAlign: 'middle', marginRight: 4 }} /> Upload
              </button>
              {showCheckmark && (
                <span className="checkmark-success" aria-label="Success" style={{ marginLeft: 12, verticalAlign: 'middle' }}></span>
              )}
            </div>
          </form>
        )}
        {loading && <div aria-live="polite">Uploading...</div>}
      </div>
    </div>
  );
};

export default UploadTrainingCSV;
