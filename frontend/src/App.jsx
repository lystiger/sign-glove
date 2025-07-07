import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import UploadCSV from './pages/UploadCSV';
import ManageGestures from './pages/ManageGestures';
import TrainingResults from './pages/TrainingResults';
import Predict from './pages/Predict';
import LivePredict from './pages/LivePredict';
import AdminTools from './pages/AdminTools';
import UploadTrainingCSV from './pages/UploadTrainingCSV';
import PredictionHistory from './pages/PredictionHistory';

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-blue-600 text-white p-4">
          <h1 className="text-2xl font-bold">Sign Glove</h1>
          <nav className="mt-2 space-x-4">
            <Link to="/" className="hover:underline">Dashboard</Link>
            <Link to="/upload" className="hover:underline">Upload CSV</Link>
            <Link to="/training/upload" className="hover:underline"> Upload Training Data</Link>
            <Link to="/gestures" className="hover:underline">Manage Gestures</Link>
            <Link to="/training" className="hover:underline">Training Results</Link>
            <Link to="/predict" className="hover:underline">Predict</Link>
            <Link to="/predict/live" className="hover:underline">Live Predict</Link>
            <Link to="/history" className="hover:underline">Data History</Link>   
            <Link to="/admin" className="hover:underline">Admin</Link>           
          </nav>
        </header>

        <main className="p-4">
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

        <footer className="text-center text-sm text-gray-500 py-4">
          &copy; 2025 Sign Glove AI
        </footer>
      </div>
    </Router>
  );
};

export default App;
