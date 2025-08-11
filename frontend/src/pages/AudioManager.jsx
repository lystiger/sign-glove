import React, { useEffect, useState, useRef } from 'react';
import { toast } from 'react-toastify';
import { apiRequest } from '../api';
import './styling/AudioManager.css';

const API_BASE = '/audio-files';
const MAX_SIZE_MB = 5;
const ESP32_BASE_URL = 'http://<ESP32_IP>'; // TODO: Replace with your ESP32's IP address

const AudioManager = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [errorLog, setErrorLog] = useState('');
  const [logLoading, setLogLoading] = useState(false);
  const fileInput = useRef();

  // Fetch audio file list
  const fetchFiles = async () => {
    setLoading(true);
    try {
      const res = await apiRequest('get', API_BASE + '/');
      setFiles(res);
    } catch (e) {
      toast.error('Failed to fetch audio files');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  // Upload audio file
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return toast.error('No file selected');
    if (selectedFile.size > MAX_SIZE_MB * 1024 * 1024) {
      return toast.error(`File too large (max ${MAX_SIZE_MB}MB)`);
    }
    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      await apiRequest('post', API_BASE + '/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      toast.success('File uploaded');
      setSelectedFile(null);
      fileInput.current.value = '';
      fetchFiles();
    } catch (e) {
      if (e.status === 413) {
        toast.error('File too large');
      } else if (e.status === 409) {
        toast.error('File already exists');
      } else {
        toast.error('Upload failed');
      }
    }
    setUploading(false);
  };

  // Delete audio file
  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete ${filename}?`)) return;
    try {
      await apiRequest('delete', `${API_BASE}/${filename}`);
      toast.success('File deleted');
      fetchFiles();
    } catch {
      toast.error('Delete failed');
    }
  };

  // Play audio file
  const handlePlay = async (filename) => {
    try {
      const res = await apiRequest('post', `${API_BASE}/${filename}/play`);
      toast.success(`Sent to ESP32: ${res.esp32_status}`);
    } catch (e) {
      toast.error('Failed to play on ESP32');
    }
  };

  // Download audio file
  const handleDownload = (filename) => {
    // Use the same BASE_URL as in api.js
    const BASE_URL = 'http://localhost:8080';
    window.open(`${BASE_URL}${API_BASE}/${filename}`, '_blank');
  };

  // Fetch ESP32 error log
  const fetchErrorLog = async () => {
    setLogLoading(true);
    try {
      const res = await apiRequest('get', `${API_BASE}/esp32/error-log`);
      setErrorLog(typeof res === 'string' ? res : JSON.stringify(res));
    } catch {
      setErrorLog('No log or failed to fetch');
    }
    setLogLoading(false);
  };

  const handleSpeaker = async (on) => {
    try {
      await fetch(`${ESP32_BASE_URL}/speaker/${on ? 'on' : 'off'}`, { method: 'POST' });
      toast.success(`Speaker turned ${on ? 'ON' : 'OFF'}`);
    } catch {
      toast.error('Failed to control speaker');
    }
  };

  return (
    <div className="audio-manager-card fade-in">
      <h2>Audio File Manager</h2>
      {/* Speaker on/off buttons */}
      <div style={{ marginBottom: 16 }}>
        <button
          className="audio-manager-btn audio-manager-btn-primary"
          onClick={() => handleSpeaker(true)}
          style={{ marginRight: 8 }}
        >
          Turn On Speaker
        </button>
        <button
          className="audio-manager-btn audio-manager-btn-danger"
          onClick={() => handleSpeaker(false)}
        >
          Turn Off Speaker
        </button>
      </div>
      <form onSubmit={handleUpload} style={{ marginBottom: 24 }}>
        <input
          type="file"
          accept="audio/*"
          ref={fileInput}
          onChange={e => setSelectedFile(e.target.files[0])}
          aria-label="Select audio file"
          className="audio-manager-file-input"
        />
        <button className="audio-manager-btn audio-manager-btn-primary" type="submit" disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
        <span style={{ marginLeft: 16, color: '#888' }}>
          Max size: {MAX_SIZE_MB}MB
        </span>
      </form>
      <h3>Files</h3>
      {loading ? <div>Loading...</div> : (
        <table className="audio-manager-table">
          <thead>
            <tr>
              <th>Filename</th>
              <th>Uploaded</th>
              <th>Uploader</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {files.map(f => (
              <tr key={f.filename}>
                <td>{f.filename}</td>
                <td>{new Date(f.upload_time).toLocaleString()}</td>
                <td>{f.uploader}</td>
                <td>
                  <button className="audio-manager-btn audio-manager-btn-primary" onClick={() => handlePlay(f.filename)}>
                    Play
                  </button>
                  <button className="audio-manager-btn audio-manager-btn-secondary" onClick={() => handleDownload(f.filename)}>
                    Download
                  </button>
                  <button className="audio-manager-btn audio-manager-btn-danger" onClick={() => handleDelete(f.filename)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <h3>ESP32 Error Log</h3>
      <button className="audio-manager-btn audio-manager-btn-secondary" onClick={fetchErrorLog} disabled={logLoading} style={{ marginBottom: 8 }}>
        {logLoading ? 'Loading...' : 'Fetch Log'}
      </button>
      <pre className="audio-manager-log">
        {errorLog}
      </pre>
    </div>
  );
};

export default AudioManager; 