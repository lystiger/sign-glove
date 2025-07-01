import React, { useEffect, useState } from 'react';
import axios from 'axios';

const TrainingResult = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/training')
      .then(res => setResults(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-2">Training Results</h2>
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
              <td className="border px-2 py-1">{r.accuracy}</td>
              <td className="border px-2 py-1">{new Date(r.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TrainingResult;
