import { useEffect, useState } from 'react';
import axios from 'axios';

export default function TrainingResults() {
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrainingResults = async () => {
      try {
        const res = await axios.get('http://localhost:8000/training/');
        setResults(res.data);
      } catch (err) {
        console.error("Failed to fetch training results:", err);
        setError("Failed to load training results. Please try again later.");
      }
    };

    fetchTrainingResults();
  }, []);

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Model Training Results</h1>

      {error && <p className="text-red-500 mb-4">{error}</p>}

      {results.length === 0 && !error ? (
        <p className="text-gray-500">No training sessions found.</p>
      ) : (
        <ul className="space-y-4">
          {results.map((r, i) => (
            <li
              key={i}
              className="bg-white border rounded-lg p-4 shadow-sm hover:shadow transition"
            >
              <div className="text-sm text-gray-500">Session ID</div>
              <div className="text-lg font-mono mb-2">{r.session_id}</div>
              <div className="text-sm text-gray-500">Accuracy</div>
              <div className="text-xl font-semibold text-green-600">
                {r.accuracy}%
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
