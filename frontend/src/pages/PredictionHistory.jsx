import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';
import { apiRequest } from '../api';
import { ToastContainer } from 'react-toastify';

const PredictionHistory = ({ user }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchHistory = async () => {
    if (!user) {
      setHistory([]);
      return;
    }
    
    setLoading(true);
    try {
      const res = await apiRequest('get', '/predict/predictions');
      setHistory(res);
    } catch (err) {
      toast.error(`Failed to fetch prediction history: ${err.detail}${err.traceId ? ` (trace: ${err.traceId})` : ''}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [user]); // Re-fetch when user changes

  return (
    <div role="main" aria-label="Prediction History Page">
      <h2 id="prediction-history-title" tabIndex={0}>Prediction History</h2>
      {!user ? (
        <div>
          <p>Please sign in to view prediction history.</p>
          <a href="/login" className="btn btn-primary">Sign In</a>
        </div>
      ) : (
        <>
          {loading ? (
            <ul aria-busy="true" aria-live="polite">
              {Array.from({ length: 5 }).map((_, i) => (
                <li key={i}><Skeleton width={300} /></li>
              ))}
            </ul>
          ) : (
            <ul aria-label="Prediction history list">
              {history.map((h) => (
                <li key={h._id}>{h.timestamp} - {h.prediction}</li>
              ))}
            </ul>
          )}
        </>
      )}
      <ToastContainer aria-live="polite" />
    </div>
  );
};

export default PredictionHistory;
