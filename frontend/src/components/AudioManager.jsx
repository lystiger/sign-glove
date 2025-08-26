import React, { useState, useEffect } from 'react';
import { getAudioFiles, uploadAudioFile, deleteAudioFile, playAudioOnESP32, playAudioOnLaptop } from '../api';
import { toast } from 'react-toastify';
import { MdVolumeUp, MdSpeaker, MdUpload, MdDelete, MdPlayArrow } from 'react-icons/md';
import './styling/AudioManager.css';

const AudioManager = ({ user }) => {
  const [audioFiles, setAudioFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [playingFiles, setPlayingFiles] = useState(new Set());
  const [selectedFile, setSelectedFile] = useState(null);

  const fetchAudioFiles = async () => {
    if (!user) return;
    
    setLoading(true);
    try {
      const files = await getAudioFiles();
      setAudioFiles(files);
    } catch (err) {
      toast.error(`Failed to fetch audio files: ${err.detail}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudioFiles();
  }, [user]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file type
    if (!file.type.startsWith('audio/')) {
      toast.error('Please select an audio file');
      return;
    }

    // Check file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    setUploading(true);
    try {
      await uploadAudioFile(file, user?.username || 'unknown');
      toast.success('Audio file uploaded successfully!');
      fetchAudioFiles();
      event.target.value = ''; // Reset file input
    } catch (err) {
      toast.error(`Upload failed: ${err.detail}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    if (!confirm(`Are you sure you want to delete ${filename}?`)) return;

    try {
      await deleteAudioFile(filename);
      toast.success('Audio file deleted!');
      fetchAudioFiles();
    } catch (err) {
      toast.error(`Delete failed: ${err.detail}`);
    }
  };

  const handlePlayOnLaptop = async (filename) => {
    setPlayingFiles(prev => new Set([...prev, filename]));
    try {
      const result = await playAudioOnLaptop(filename);
      toast.success(`Playing ${filename} on laptop`);
      
      // Remove from playing set after a delay (estimated playback time)
      setTimeout(() => {
        setPlayingFiles(prev => {
          const newSet = new Set(prev);
          newSet.delete(filename);
          return newSet;
        });
      }, 3000); // 3 seconds default, could be improved with actual audio duration
      
    } catch (err) {
      toast.error(`Laptop playback failed: ${err.detail}`);
      setPlayingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(filename);
        return newSet;
      });
    }
  };

  const handlePlayOnESP32 = async (filename) => {
    setPlayingFiles(prev => new Set([...prev, filename]));
    try {
      const result = await playAudioOnESP32(filename);
      toast.success(`Sent ${filename} to ESP32`);
      
      setTimeout(() => {
        setPlayingFiles(prev => {
          const newSet = new Set(prev);
          newSet.delete(filename);
          return newSet;
        });
      }, 3000);
      
    } catch (err) {
      toast.error(`ESP32 playback failed: ${err.detail}`);
      setPlayingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(filename);
        return newSet;
      });
    }
  };

  if (!user) {
    return (
      <div className="audio-manager">
        <div className="card">
          <h2>Audio Manager</h2>
          <p>Please sign in to manage audio files.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="audio-manager">
      <div className="card">
        <h2>Audio Manager</h2>
        <p>Upload and manage audio files for gesture feedback</p>
        
        {/* Upload Section */}
        <div className="upload-section">
          <label htmlFor="audio-upload" className="upload-button">
            <MdUpload style={{ marginRight: '8px' }} />
            {uploading ? 'Uploading...' : 'Upload Audio File'}
          </label>
          <input
            id="audio-upload"
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          <small>Supported formats: MP3, WAV, OGG (Max 5MB)</small>
        </div>

        {/* Audio Files List */}
        <div className="audio-files-section">
          <h3>Audio Files ({audioFiles.length})</h3>
          {loading ? (
            <div className="loading">Loading audio files...</div>
          ) : audioFiles.length === 0 ? (
            <div className="no-files">No audio files uploaded yet</div>
          ) : (
            <div className="audio-files-list">
              {audioFiles.map((file) => (
                <div key={file.filename} className="audio-file-item">
                  <div className="file-info">
                    <div className="filename">{file.filename}</div>
                    <div className="file-meta">
                      Uploaded by {file.uploader} on {new Date(file.upload_time).toLocaleDateString()}
                    </div>
                  </div>
                  
                  <div className="file-actions">
                    <button
                      onClick={() => handlePlayOnLaptop(file.filename)}
                      disabled={playingFiles.has(file.filename)}
                      className="btn btn-primary"
                      title="Play on laptop"
                    >
                      <MdVolumeUp style={{ marginRight: '4px' }} />
                      {playingFiles.has(file.filename) ? 'Playing...' : 'Laptop'}
                    </button>
                    
                    <button
                      onClick={() => handlePlayOnESP32(file.filename)}
                      disabled={playingFiles.has(file.filename)}
                      className="btn btn-secondary"
                      title="Send to ESP32"
                    >
                      <MdSpeaker style={{ marginRight: '4px' }} />
                      ESP32
                    </button>
                    
                    <button
                      onClick={() => handleDelete(file.filename)}
                      className="btn btn-danger"
                      title="Delete file"
                    >
                      <MdDelete />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AudioManager;
