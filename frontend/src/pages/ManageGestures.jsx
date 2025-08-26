import React, { useEffect, useState } from 'react';
import { getGestures, createGesture, deleteGesture, updateGesture, convertGestureToDualHand, checkConversionStatus, playAudioOnLaptop } from '../api';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import './styling/Gestures.css';
import { MdSave, MdEdit, MdDeleteForever, MdSwapHoriz, MdVolumeUp } from 'react-icons/md';
import AudioManager from '../components/AudioManager';

const ManageGestures = ({ user }) => {
  const [gestures, setGestures] = useState([]);
  const [editSession, setEditSession] = useState(null);
  const [editedLabel, setEditedLabel] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [showCheckmark, setShowCheckmark] = useState(false);
  const [convertingGestures, setConvertingGestures] = useState(new Set());
  const [conversionStatus, setConversionStatus] = useState({});
  const [debugMode, setDebugMode] = useState(false);
  const [activeTab, setActiveTab] = useState('gestures');
  const [testingAudio, setTestingAudio] = useState(new Set());

  // New gesture form state
  const [newGesture, setNewGesture] = useState({
    session_id: '',
    gesture_label: '',
    sensor_values: '',
    source: 'manual',
  });

  const fetchGestures = async () => {
    if (!user) {
      setGestures([]);
      return;
    }
    
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
  }, [user]); // Re-fetch when user changes

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
    setEditedLabel(label || ''); // Ensure label is never undefined
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

  const handleConvertToDualHand = async (session_id) => {
    setConvertingGestures(prev => new Set([...prev, session_id]));
    try {
      const result = await convertGestureToDualHand(session_id);
      toast.success(`Gesture converted to dual-hand! New session: ${result.data.new_session_id}`);
      fetchGestures(); // Refresh to show new dual-hand gesture
      // Update conversion status
      setConversionStatus(prev => ({
        ...prev,
        [session_id]: { hasDualHand: true, dualHandSessionId: result.data.new_session_id }
      }));
    } catch (err) {
      if (err.status === 409) {
        toast.warning('Dual-hand version already exists!');
      } else {
        toast.error(`Conversion failed: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
      }
    } finally {
      setConvertingGestures(prev => {
        const newSet = new Set(prev);
        newSet.delete(session_id);
        return newSet;
      });
    }
  };

  const checkGestureConversionStatus = async (session_id) => {
    try {
      const result = await checkConversionStatus(session_id);
      setConversionStatus(prev => ({
        ...prev,
        [session_id]: {
          hasDualHand: result.data.has_dual_hand_version,
          dualHandSessionId: result.data.dual_hand_session_id
        }
      }));
    } catch (err) {
      // Silently handle errors for status checks
      console.warn('Failed to check conversion status:', err);
    }
  };

  // Check conversion status for all gestures when they load
  useEffect(() => {
    if (gestures.length > 0) {
      gestures.forEach(gesture => {
        const values = gesture.sensor_values || gesture.values || [];
        if (values && values.length === 11) {
          checkGestureConversionStatus(gesture.session_id);
        }
      });
    }
  }, [gestures]);

  const isSingleHandGesture = (gesture) => {
    // Check both possible field names for sensor data
    const values = gesture.sensor_values || gesture.values || [];
    return values && values.length === 11;
  };

  const isDualHandGesture = (gesture) => {
    // Check both possible field names for sensor data
    const values = gesture.sensor_values || gesture.values || [];
    return values && values.length === 22;
  };

  // Debug function to log gesture structure
  const logGestureStructure = (gesture) => {
    console.log('Gesture structure:', {
      session_id: gesture.session_id,
      label: gesture.gesture_label,
      sensor_values: gesture.sensor_values,
      values: gesture.values,
      sensor_values_length: gesture.sensor_values?.length,
      values_length: gesture.values?.length,
      all_keys: Object.keys(gesture)
    });
  };

  const handleTestAudio = async (gestureLabel) => {
    setTestingAudio(prev => new Set([...prev, gestureLabel]));
    try {
      // Create a simple TTS for the gesture label and play on laptop
      const utterance = new SpeechSynthesisUtterance(gestureLabel);
      utterance.rate = 0.8;
      utterance.volume = 0.8;
      speechSynthesis.speak(utterance);
      
      toast.success(`Playing "${gestureLabel}" on laptop`);
      
      // Remove from testing set after speech
      utterance.onend = () => {
        setTestingAudio(prev => {
          const newSet = new Set(prev);
          newSet.delete(gestureLabel);
          return newSet;
        });
      };
      
    } catch (err) {
      toast.error(`Audio test failed: ${err.message}`);
      setTestingAudio(prev => {
        const newSet = new Set(prev);
        newSet.delete(gestureLabel);
        return newSet;
      });
    }
  };

  return (
    <div className="manage-container" role="main" aria-label="Manage Gestures Page">
      {!user ? (
        <div className="card fade-in" style={{ marginBottom: '2rem' }}>
          <h2 className="manage-title">Manage Gestures</h2>
          <p>Please sign in to manage gestures and access the application features.</p>
          <a href="/login" className="btn btn-primary">Sign In</a>
        </div>
      ) : (
        <>
          <div className="card fade-in" style={{ marginBottom: '2rem' }}>
            <h2 className="manage-title">Manage Gestures & Audio</h2>
            
            {/* Tab Navigation */}
            <div className="tab-navigation" style={{ marginBottom: '1rem' }}>
              <button
                onClick={() => setActiveTab('gestures')}
                className={`tab-button ${activeTab === 'gestures' ? 'active' : ''}`}
              >
                Gestures
              </button>
              <button
                onClick={() => setActiveTab('audio')}
                className={`tab-button ${activeTab === 'audio' ? 'active' : ''}`}
              >
                Audio Manager
              </button>
            </div>

            {activeTab === 'gestures' && (
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                <label htmlFor="search-input" className="visually-hidden">Search by label or session ID</label>
                <input
                  id="search-input"
                  type="text"
                  placeholder="Search by label or session ID"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                  aria-label="Search gestures by label or session ID"
                  style={{ flex: 1 }}
                />
                <button
                  onClick={() => setDebugMode(!debugMode)}
                  className={`btn ${debugMode ? 'btn-warning' : 'btn-outline-secondary'}`}
                  style={{ fontSize: '0.8em' }}
                >
                  {debugMode ? '🐛 Debug ON' : '🔍 Debug OFF'}
                </button>
              </div>
            )}
          </div>
          
          {/* Gestures Tab Content */}
          {activeTab === 'gestures' && (
            <>
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
                  <li key={`${g.session_id}-${index}`} className="gesture-item" tabIndex={0} aria-label={`Gesture for session ${g.session_id}`}>
                    <div>
                      <span className="session-id">Session: {g.session_id}</span>
                      <div className="label-line">
                        <span>Label:</span>
                        {editSession === g.session_id ? (
                          <input
                            aria-label="Edit gesture label"
                            value={editedLabel || ''}
                            onChange={(e) => setEditedLabel(e.target.value)}
                            className="edit-input"
                            disabled={actionLoading}
                          />
                        ) : (
                          <span className="label">{g.gesture_label}</span>
                        )}
                      </div>
                      <div className="gesture-info">
                        <span className={`gesture-type ${isSingleHandGesture(g) ? 'single-hand' : isDualHandGesture(g) ? 'dual-hand' : 'unknown'}`}>
                          {(() => {
                            const values = g.sensor_values || g.values || [];
                            const count = values.length;
                            logGestureStructure(g); // Debug log
                            
                            if (count === 11) return '🖐️ Single Hand (11 values)';
                            if (count === 22) return '🙌 Dual Hand (22 values)';
                            return `❓ Unknown (${count} values) - Debug: sensor_values=${g.sensor_values?.length}, values=${g.values?.length}`;
                          })()} 
                        </span>
                        {isSingleHandGesture(g) && conversionStatus[g.session_id]?.hasDualHand && (
                          <span className="conversion-info" style={{ marginLeft: '10px', fontSize: '0.8em', color: '#28a745' }}>
                            ✓ Dual-hand version exists: {conversionStatus[g.session_id]?.dualHandSessionId}
                          </span>
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
                        onClick={() => handleTestAudio(g.gesture_label)}
                        className="btn btn-success"
                        disabled={testingAudio.has(g.gesture_label)}
                        aria-label={`Test audio for ${g.gesture_label}`}
                        title="Test audio playback on laptop"
                      >
                        <MdVolumeUp style={{ verticalAlign: 'middle', marginRight: 4 }} />
                        {testingAudio.has(g.gesture_label) ? 'Playing...' : 'Test Audio'}
                      </button>
                      {(debugMode || (isSingleHandGesture(g) && !conversionStatus[g.session_id]?.hasDualHand)) && (
                        <button
                          onClick={() => handleConvertToDualHand(g.session_id)}
                          className="btn btn-info"
                          disabled={actionLoading || convertingGestures.has(g.session_id)}
                          aria-label={`Convert gesture ${g.session_id} to dual-hand`}
                          title={debugMode ? `Debug: isSingle=${isSingleHandGesture(g)}, hasConversion=${!!conversionStatus[g.session_id]?.hasDualHand}` : ''}
                        >
                          <MdSwapHoriz style={{ verticalAlign: 'middle', marginRight: 4 }} />
                          {convertingGestures.has(g.session_id) ? 'Converting...' : 'To Dual-Hand'}
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(g.session_id)}
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
            </>
          )}
          
          {/* Audio Tab Content */}
          {activeTab === 'audio' && (
            <AudioManager user={user} />
          )}
        </>
      )}
    </div>
  );
};

export default ManageGestures;