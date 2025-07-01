import React, { useState } from 'react';
import axios from 'axios';

const UploadCSV = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  const handleUpload = async () => {
    if (!file) return setStatus('Please select a CSV file.');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/training/upload', formData);
      setStatus(`Uploaded: ${res.data.message}`);
    } catch (err) {
      setStatus('Upload failed.');
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Upload Training CSV</h2>
      <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
      <button className="ml-2 bg-blue-500 text-white px-4 py-1 rounded" onClick={handleUpload}>
        Upload
      </button>
      <p className="mt-2 text-sm">{status}</p>
    </div>
  );
};

export default UploadCSV;
