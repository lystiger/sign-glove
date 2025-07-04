import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import UploadCSV from './components/UploadCSV';
import ManageGestures from './components/ManageGestures';
import TrainingResults from './components/TrainingResults';
import Predict from './components/Predict';
import LivePredict from './components/LivePredict';
import AdminTools from './components/AdminTools';

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-blue-600 text-white p-4">
          <h1 className="text-2xl font-bold">Sign Glove</h1>
          <nav className="mt-2 space-x-4">
            <Link to="/" className="hover:underline">Dashboard</Link>
            <Link to="/upload" className="hover:underline">Upload CSV</Link>
            <Link to="/gestures" className="hover:underline">Manage Gestures</Link>
            <Link to="/training" className="hover:underline">Training Results</Link>
            <Link to="/predict" className="hover:underline">Predict</Link>
            <Link to="/predict/live" className="hover:underline">Live Predict</Link>
            <Link to="/admin" className="hover:underline">Admin</Link>
          </nav>
        </header>

        <main className="p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadCSV />} />
            <Route path="/gestures" element={<ManageGestures />} />
            <Route path="/training" element={<TrainingResults />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/predict/live" element={<LivePredict />} />
            <Route path="/admin" element={<AdminTools />} />
          </Routes>
        </main>

        <footer className="text-center text-sm text-gray-500 py-4">
          &copy; 2025 Sign Glove AI
        </footer>
      </div>
    </Router>
  );
};

export default App;
