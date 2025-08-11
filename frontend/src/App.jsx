import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
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
import AudioManager from './pages/AudioManager';
import { MdDarkMode, MdMenu, MdClose } from 'react-icons/md';
import Login from './pages/Login';
import { apiRequest } from './api';

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
  const [navOpen, setNavOpen] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Try to fetch current user
    apiRequest('get', '/auth/me')
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  const signOut = async () => {
    try {
      await apiRequest('post', '/auth/logout');
      localStorage.removeItem('access_token');
      setUser(null);
      toast.success('Signed out');
    } catch (e) {
      toast.error('Failed to sign out');
    }
  };

  const isEditor = user?.role === 'editor' || user?.role === 'admin';

  const navLinks = [
    { to: '/', label: 'Dashboard' },
    { to: '/gestures', label: 'Manage Gestures' },
    { to: '/training-results', label: 'Training Results' },
    { to: '/predict', label: 'Manual Prediction' },
    { to: '/live-predict', label: 'Live Predict' },
    // editor-only routes
    ...(isEditor ? [
      { to: '/upload-csv', label: 'Upload CSV' },
      { to: '/upload-training-csv', label: 'Upload Training CSV' },
      { to: '/admin', label: 'Admin Tools' },
      { to: '/audio-manager', label: 'Audio Manager' },
    ] : []),
  ];

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="main-header">
          <div className="header-row header-top">
            <div className="header-title">Sign Glove</div>
            <div className="header-actions">
              {user ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ fontSize: 14 }}>Signed in as {user.email} ({user.role})</span>
                  <button className="btn btn-secondary" onClick={signOut}>Sign Out</button>
                </div>
              ) : (
                <Link to="/login" className="btn btn-secondary">Sign In</Link>
              )}
              {/* Hamburger menu for mobile */}
              <button
                className="header-hamburger"
                aria-label={navOpen ? 'Close menu' : 'Open menu'}
                onClick={() => setNavOpen(o => !o)}
              >
                {navOpen ? <MdClose size={28} /> : <MdMenu size={28} />}
              </button>
              <button
                className="btn btn-secondary header-darkmode-btn"
                aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
                onClick={() => setDark(d => !d)}
                style={{ display: 'flex', alignItems: 'center' }}
              >
                <MdDarkMode style={{ fontSize: 22, marginRight: 6 }} />
                {dark ? 'Light' : 'Dark'} Mode
              </button>
            </div>
          </div>
          {/* Nav links: show row on desktop, vertical menu on mobile if open */}
          <nav className={`header-nav${navOpen ? ' nav-open' : ''}`}>
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className="hover:underline"
                onClick={() => setNavOpen(false)}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </header>

        <main className="p-4" style={{ position: 'relative', zIndex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload-csv" element={isEditor ? <UploadCSV /> : <Dashboard />} />
            <Route path="/upload-training-csv" element={isEditor ? <UploadTrainingCSV /> : <Dashboard />} />
            <Route path="/gestures" element={<ManageGestures />} />
            <Route path="/training-results" element={<TrainingResults />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/live-predict" element={<LivePredict />} />
            <Route path="/history" element={<PredictionHistory />} />
            <Route path="/admin" element={isEditor ? <AdminTools /> : <Dashboard />} />
            <Route path="/audio-manager" element={isEditor ? <AudioManager /> : <Dashboard />} />
            <Route path="/login" element={<Login onLogin={setUser} />} />
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
