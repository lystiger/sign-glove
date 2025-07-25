import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Dashboard from './pages/Dashboard';
import UploadCSV from './pages/UploadCSV';
import ManageGestures from './pages/ManageGestures';
import TrainingResults from './pages/TrainingResults';
import Predict from './pages/Predict';
import LivePredict from './pages/LivePredict';
import AdminTools from './pages/AdminTools';
import UploadTrainingCSV from './pages/UploadTrainingCSV';
import PredictionHistory from './pages/PredictionHistory';
import { MdDarkMode } from 'react-icons/md';

function useDarkMode() {
  const [dark, setDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.body.classList.contains('dark');
    }
    return false;
  });
  useEffect(() => {
    if (dark) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [dark]);
  return [dark, setDark];
}

const App = () => {
  const [dark, setDark] = useDarkMode();

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-blue-600 text-white p-4" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <h1 className="text-2xl font-bold" style={{ marginRight: 32, whiteSpace: 'nowrap' }}>Sign Glove</h1>
            <nav style={{ display: 'flex', gap: '1.5rem', flex: 1, justifyContent: 'center' }}>
              <Link to="/" className="hover:underline">Dashboard</Link>
              <Link to="/gestures" className="hover:underline">Manage Gestures</Link>
              <Link to="/training-results" className="hover:underline">Training Results</Link>
              <Link to="/predict" className="hover:underline">Manual Prediction</Link>
              <Link to="/live-predict" className="hover:underline">Live Predict</Link>
              <Link to="/upload-csv" className="hover:underline">Upload CSV</Link>
              <Link to="/upload-training-csv" className="hover:underline">Upload Training CSV</Link>
              <Link to="/admin" className="hover:underline">Admin Tools</Link>
            </nav>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', marginLeft: 32 }}>
            <button
              className="btn btn-secondary"
              aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
              onClick={() => setDark(d => !d)}
              style={{ display: 'flex', alignItems: 'center' }}
            >
              <MdDarkMode style={{ fontSize: 22, marginRight: 6 }} />
              {dark ? 'Light' : 'Dark'} Mode
            </button>
          </div>
        </header>

        <main className="p-4" style={{ position: 'relative', zIndex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadCSV />} />
            <Route path="/training/upload" element={<UploadTrainingCSV />} />
            <Route path="/gestures" element={<ManageGestures />} />
            <Route path="/training" element={<TrainingResults />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/predict/live" element={<LivePredict />} />
            <Route path="/history" element={<PredictionHistory />} />
            <Route path="/admin" element={<AdminTools />} />
          </Routes>
        </main>

        <ToastContainer />

        <footer className="text-center text-sm text-gray-500 py-4">
          &copy; 2025 Sign Glove AI
        </footer>
      </div>
    </Router>
  );
};

export default App;
