import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ManageGestures = () => {
  const [gestures, setGestures] = useState([]);
  const [editSession, setEditSession] = useState(null);
  const [editedLabel, setEditedLabel] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  // New gesture form state
  const [newGesture, setNewGesture] = useState({
    session_id: '',
    gesture_label: '',
    sensor_values: '',
    source: 'manual',
  });

  const fetchGestures = async () => {
    try {
      const res = await axios.get('http://localhost:8000/gestures');
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
      await axios.delete(`http://localhost:8000/gestures/${session_id}`);
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
      await axios.put(`http://localhost:8000/gestures/${editSession}?label=${editedLabel}`);
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
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-bold mb-4">Manage Gestures</h2>
      <input
        type="text"
        placeholder="Search by label or session ID"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="border px-3 py-2 rounded mb-4 w-full"
        />

      {/* ➕ New Gesture Form */}
      <div className="mb-6 border border-gray-200 p-4 rounded bg-gray-50">
        <h3 className="font-semibold mb-2">Add New Gesture</h3>
        <input
          className="border px-2 py-1 mr-2 mb-2 w-full"
          placeholder="Session ID"
          value={newGesture.session_id}
          onChange={(e) => setNewGesture({ ...newGesture, session_id: e.target.value })}
        />
        <input
          className="border px-2 py-1 mr-2 mb-2 w-full"
          placeholder="Gesture Label"
          value={newGesture.gesture_label}
          onChange={(e) => setNewGesture({ ...newGesture, gesture_label: e.target.value })}
        />
        <input
          className="border px-2 py-1 mr-2 mb-2 w-full"
          placeholder="Sensor Values (comma-separated, 11 values)"
          value={newGesture.sensor_values}
          onChange={(e) => setNewGesture({ ...newGesture, sensor_values: e.target.value })}
        />
        <input
          className="border px-2 py-1 mr-2 mb-2 w-full"
          placeholder="Source (optional, e.g., manual)"
          value={newGesture.source}
          onChange={(e) => setNewGesture({ ...newGesture, source: e.target.value })}
        />
        <button
          className="bg-green-600 text-white px-4 py-1 rounded"
          onClick={handleNewGestureSubmit}
        >
          Submit
        </button>
      </div>

      {/* 🔧 Gesture List */}
      <ul className="divide-y">
      {gestures.filter((g) => {
            const term = searchTerm.toLowerCase();
            return (
                g.gesture_label.toLowerCase().includes(term) ||
                g.session_id.toLowerCase().includes(term)
        );
    }).map((g) => (
          <li key={g.session_id} className="py-2 flex items-center justify-between">
            <div>
              <span className="font-mono text-sm text-gray-700">Session: {g.session_id}</span>
              <div className="text-gray-600 text-sm">
                Label: {editSession === g.session_id ? (
                  <input
                    value={editedLabel}
                    onChange={(e) => setEditedLabel(e.target.value)}
                    className="ml-2 border rounded px-2 py-1 text-sm"
                  />
                ) : (
                  <span className="ml-2">{g.gesture_label}</span>
                )}
              </div>
            </div>
            <div className="flex space-x-2">
              {editSession === g.session_id ? (
                <button onClick={handleUpdate} className="bg-blue-500 text-white px-2 py-1 text-sm rounded">
                  Save
                </button>
              ) : (
                <button
                  onClick={() => handleEdit(g.session_id, g.gesture_label)}
                  className="bg-yellow-500 text-white px-2 py-1 text-sm rounded"
                >
                  Edit
                </button>
              )}
                <button
                  onClick={() => setConfirmDeleteId(g.session_id)}
                  className="bg-red-600 text-white px-2 py-1 text-sm rounded"
                >
                  Delete
                </button>
            </div>
          </li>
        ))}
      </ul>
      {confirmDeleteId && (
  <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
    <div className="bg-white rounded shadow p-6 max-w-sm text-center">
      <p className="mb-4">Are you sure you want to delete gesture <strong>{confirmDeleteId}</strong>?</p>
      <div className="flex justify-center gap-4">
        <button
          onClick={() => {
            handleDelete(confirmDeleteId);
            setConfirmDeleteId(null);
          }}
          className="bg-red-600 text-white px-4 py-1 rounded"
        >
          Yes, Delete
        </button>
        <button
          onClick={() => setConfirmDeleteId(null)}
          className="bg-gray-300 px-4 py-1 rounded"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
)}
    </div>
  );
};

export default ManageGestures;
