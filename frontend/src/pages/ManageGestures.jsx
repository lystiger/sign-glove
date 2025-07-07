import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './styling/Gestures.css';

const ManageGestures = () => {
  const [gestures, setGestures] = useState([]);
  const [editSession, setEditSession] = useState(null);
  const [editedLabel, setEditedLabel] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [setConfirmDeleteId] = useState(null);

  // New gesture form state
  const [newGesture, setNewGesture] = useState({
    session_id: '',
    gesture_label: '',
    sensor_values: '',
    source: 'manual',
  });

  const fetchGestures = async () => {
    try {
      const res = await axios.get('http://localhost:8080/gestures');
      setGestures(res.data.data);
    } catch (err) {
      console.error('Fetch error:', err);
    }
  };

  useEffect(() => {
    fetchGestures();
  }, []);

  const handleDelete = async (session_id) => {
    try {
      await axios.delete(`http://localhost:8080/gestures/${session_id}`);
      setGestures((prev) => prev.filter((g) => g.session_id !== session_id));
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleEdit = (session_id, label) => {
    setEditSession(session_id);
    setEditedLabel(label);
  };

  const handleUpdate = async () => {
    try {
      await axios.put(`http://localhost:8080/gestures/${editSession}?label=${editedLabel}`);
      setEditSession(null);
      fetchGestures();
    } catch (err) {
      console.error('Update failed:', err);
    }
  };

  const handleNewGestureSubmit = async () => {
    const { session_id, gesture_label, sensor_values, source } = newGesture;

    // Parse and validate sensor values
    const values = sensor_values
      .split(',')
      .map((v) => parseFloat(v.trim()))
      .filter((v) => !isNaN(v));

    if (values.length !== 11) {
      alert('Sensor values must be 11 numbers, comma-separated.');
      return;
    }

    try {
      await axios.post('http://localhost:8000/gestures/', {
        session_id,
        label: gesture_label,
        sensor_values: values,
        source,
      });
      setNewGesture({ session_id: '', gesture_label: '', sensor_values: '', source: 'manual' });
      fetchGestures();
    } catch (err) {
      console.error('Create failed:', err);
      alert('Failed to create gesture');
    }
  };

  return (
    <div className="manage-container">
  <h2 className="manage-title">Manage Gestures</h2>

  <input
    type="text"
    placeholder="Search by label or session ID"
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
    className="search-input"
  />

      {/* ➕ New Gesture Form */}
      <div className="gesture-form">
  <h3 className="form-title">Add New Gesture</h3>
  <input
    className="form-input"
    placeholder="Session ID"
    value={newGesture.session_id}
    onChange={(e) => setNewGesture({ ...newGesture, session_id: e.target.value })}
  />
  <input
    className="form-input"
    placeholder="Gesture Label"
    value={newGesture.gesture_label}
    onChange={(e) => setNewGesture({ ...newGesture, gesture_label: e.target.value })}
  />
  <input
    className="form-input"
    placeholder="Sensor Values (comma-separated, 11 values)"
    value={newGesture.sensor_values}
    onChange={(e) => setNewGesture({ ...newGesture, sensor_values: e.target.value })}
  />
  <input
    className="form-input"
    placeholder="Source (optional, e.g., manual)"
    value={newGesture.source}
    onChange={(e) => setNewGesture({ ...newGesture, source: e.target.value })}
  />
  <button className="btn btn-green" onClick={handleNewGestureSubmit}>
    Submit
  </button>
</div>

      {/* 🔧 Gesture List */}
      <ul className="gesture-list">
  {gestures.map((g, index) => (
    <li key={g.session_id || index} className="gesture-item">
      <div>
        <span className="session-id">Session: {g.session_id}</span>
        <div className="label-line">
          Label:
          {editSession === g.session_id ? (
            <input
              value={editedLabel}
              onChange={(e) => setEditedLabel(e.target.value)}
              className="edit-input"
            />
          ) : (
            <span className="label">{g.gesture_label}</span>
          )}
        </div>
      </div>
      <div className="action-buttons">
        {editSession === g.session_id ? (
          <button onClick={handleUpdate} className="btn btn-blue">Save</button>
        ) : (
          <button onClick={() => handleEdit(g.session_id, g.gesture_label)} className="btn btn-yellow">Edit</button>
        )}
        <button onClick={() => setConfirmDeleteId(g.session_id)} className="btn btn-red">
          Delete
        </button>
      </div>
    </li>
  ))}
</ul>
    </div>
  );
};

export default ManageGestures;
