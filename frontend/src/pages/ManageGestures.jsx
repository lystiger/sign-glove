import React, { useEffect, useState } from 'react';
import { getGestures, createGesture, deleteGesture, updateGesture } from '../api';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import './styling/Gestures.css';
import { MdSave, MdEdit, MdDeleteForever } from 'react-icons/md';

const ManageGestures = () => {
  const [gestures, setGestures] = useState([]);
  const [editSession, setEditSession] = useState(null);
  const [editedLabel, setEditedLabel] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [setConfirmDeleteId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [showCheckmark, setShowCheckmark] = useState(false);

  // New gesture form state
  const [newGesture, setNewGesture] = useState({
    session_id: '',
    gesture_label: '',
    sensor_values: '',
    source: 'manual',
  });

  const fetchGestures = async () => {
    setLoading(true);
    try {
      const res = await getGestures();
      setGestures(res.data);
    } catch (err) {
      toast.error(`Failed to fetch gestures: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGestures();
  }, []);

  const handleDelete = async (session_id) => {
    setActionLoading(true);
    try {
      await deleteGesture(session_id);
      setGestures((prev) => prev.filter((g) => g.session_id !== session_id));
      toast.success('Gesture deleted!');
    } catch (err) {
      toast.error(`Delete failed: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleEdit = (session_id, label) => {
    setEditSession(session_id);
    setEditedLabel(label);
  };

  const handleUpdate = async () => {
    setActionLoading(true);
    try {
      await updateGesture(editSession, editedLabel);
      setEditSession(null);
      fetchGestures();
      toast.success('Gesture updated!');
    } catch (err) {
      toast.error(`Update failed: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleNewGestureSubmit = async () => {
    const { session_id, gesture_label, sensor_values, source } = newGesture;
    const values = sensor_values
      .split(',')
      .map((v) => parseFloat(v.trim()))
      .filter((v) => !isNaN(v));
    if (values.length !== 11) {
      toast.error('Sensor values must be 11 numbers, comma-separated.');
      return;
    }
    setActionLoading(true);
    try {
      await createGesture({
        session_id,
        label: gesture_label,
        sensor_values: values,
        source,
      });
      setNewGesture({ session_id: '', gesture_label: '', sensor_values: '', source: 'manual' });
      fetchGestures();
      toast.success('Gesture created!');
      setShowCheckmark(true);
      setTimeout(() => setShowCheckmark(false), 1200);
    } catch (err) {
      toast.error(`Failed to create gesture: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="manage-container" role="main" aria-label="Manage Gestures Page">
      <div className="card fade-in" style={{ marginBottom: '2rem' }}>
        <h2 className="manage-title">Manage Gestures</h2>
        <label htmlFor="search-input" className="visually-hidden">Search by label or session ID</label>
        <input
          id="search-input"
          type="text"
          placeholder="Search by label or session ID"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
          aria-label="Search gestures by label or session ID"
        />
      </div>
      <div className="card fade-in" style={{ marginBottom: '2rem' }}>
        <form className="gesture-form" aria-label="Add New Gesture" onSubmit={e => { e.preventDefault(); handleNewGestureSubmit(); }}>
          <h3 className="form-title">Add New Gesture</h3>
          {loading ? (
            <Skeleton height={32} count={4} style={{ marginBottom: 8 }} />
          ) : (
            <>
              <label htmlFor="session-id-input">Session ID</label>
              <input
                id="session-id-input"
                className="form-input"
                placeholder="Session ID"
                value={newGesture.session_id}
                onChange={(e) => setNewGesture({ ...newGesture, session_id: e.target.value })}
                disabled={actionLoading}
                aria-required="true"
              />
              <label htmlFor="gesture-label-input">Gesture Label</label>
              <input
                id="gesture-label-input"
                className="form-input"
                placeholder="Gesture Label"
                value={newGesture.gesture_label}
                onChange={(e) => setNewGesture({ ...newGesture, gesture_label: e.target.value })}
                disabled={actionLoading}
                aria-required="true"
              />
              <label htmlFor="sensor-values-input">Sensor Values (comma-separated, 11 values)</label>
              <input
                id="sensor-values-input"
                className="form-input"
                placeholder="Sensor Values (comma-separated, 11 values)"
                value={newGesture.sensor_values}
                onChange={(e) => setNewGesture({ ...newGesture, sensor_values: e.target.value })}
                disabled={actionLoading}
                aria-required="true"
              />
              <label htmlFor="source-input">Source (optional, e.g., manual)</label>
              <input
                id="source-input"
                className="form-input"
                placeholder="Source (optional, e.g., manual)"
                value={newGesture.source}
                onChange={(e) => setNewGesture({ ...newGesture, source: e.target.value })}
                disabled={actionLoading}
              />
              <button
                className="btn btn-primary"
                type="submit"
                disabled={actionLoading}
                aria-busy={actionLoading}
                aria-label="Submit new gesture"
              >
                {actionLoading ? 'Submitting...' : 'Submit'}
              </button>
              {showCheckmark && (
                <span className="checkmark-success" aria-label="Success" style={{ marginLeft: 12, verticalAlign: 'middle' }}></span>
              )}
            </>
          )}
        </form>
      </div>
      <div className="card fade-in">
        <h3>Gesture List</h3>
        {loading ? (
          <Skeleton count={5} height={40} style={{ marginBottom: 8 }} />
        ) : (
          <ul className="gesture-list" aria-label="Gesture List">
            {gestures.map((g, index) => (
              <li key={g.session_id || index} className="gesture-item" tabIndex={0} aria-label={`Gesture for session ${g.session_id}`}>
                <div>
                  <span className="session-id">Session: {g.session_id}</span>
                  <div className="label-line">
                    <span>Label:</span>
                    {editSession === g.session_id ? (
                      <input
                        aria-label="Edit gesture label"
                        value={editedLabel}
                        onChange={(e) => setEditedLabel(e.target.value)}
                        className="edit-input"
                        disabled={actionLoading}
                      />
                    ) : (
                      <span className="label">{g.gesture_label}</span>
                    )}
                  </div>
                </div>
                <div className="action-buttons" role="group" aria-label="Gesture actions" style={{ display: 'flex', gap: '0.75rem' }}>
                  {editSession === g.session_id ? (
                    <button
                      onClick={handleUpdate}
                      className="btn btn-primary"
                      disabled={actionLoading}
                      aria-busy={actionLoading}
                      aria-label="Save gesture label"
                    >
                      <MdSave style={{ verticalAlign: 'middle', marginRight: 4 }} />
                      {actionLoading ? 'Saving...' : 'Save'}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEdit(g.session_id, g.gesture_label)}
                      className="btn btn-secondary"
                      disabled={actionLoading}
                      aria-label={`Edit gesture for session ${g.session_id}`}
                    >
                      <MdEdit style={{ verticalAlign: 'middle', marginRight: 4 }} />
                      Edit
                    </button>
                  )}
                  <button
                    onClick={() => setConfirmDeleteId(g.session_id)}
                    className="btn btn-danger"
                    disabled={actionLoading}
                    aria-label={`Delete gesture for session ${g.session_id}`}
                  >
                    <MdDeleteForever style={{ verticalAlign: 'middle', marginRight: 4 }} />
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default ManageGestures;