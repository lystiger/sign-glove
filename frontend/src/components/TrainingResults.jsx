import React, { useEffect, useState } from 'react';
import axios from 'axios';

const TrainingResult = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const res = await axios.get('http://localhost:8000/training');
      setResults(res.data.data);
    } catch (err) {
      setError("Failed to fetch training results");
    } finally {
      setLoading(false);
    }
  };

  const handleRunTraining = async () => {
    try {
      const res = await axios.post('http://localhost:8000/training/run');
      alert(`Training complete! Accuracy: ${(res.data.data.accuracy * 100).toFixed(2)}%`);
      fetchResults(); // Refresh results
    } catch (err) {
      console.error(err);
      alert("Training failed");
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Training Results</h2>

      <button
        onClick={handleRunTraining}
        className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Run Training
      </button>

      <table className="table-auto w-full text-left border-collapse border border-gray-300">
        <thead>
          <tr>
            <th className="border px-2 py-1">Session</th>
            <th className="border px-2 py-1">Accuracy</th>
            <th className="border px-2 py-1">Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r) => (
            <tr key={r._id}>
              <td className="border px-2 py-1">{r.session_id}</td>
              <td className="border px-2 py-1">{(r.accuracy * 100).toFixed(2)}%</td>
              <td className="border px-2 py-1">{new Date(r.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TrainingResult;
