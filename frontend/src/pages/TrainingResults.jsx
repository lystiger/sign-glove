import { useEffect, useState } from "react";
import axios from "axios";

const TrainingResults = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch training results from FastAPI
  const fetchTrainingResults = async () => {
    try {
      const res = await axios.get("http://localhost:8000/training/");
      setResults(res.data.data); // Extract `data` from response
    } catch (err) {
      console.error("Failed to fetch training results:", err);
      setError("Failed to load training results.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrainingResults();
  }, []);

  if (loading) return <div className="p-4 text-gray-500">Loading training results...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Training Results</h1>
      {results.length === 0 ? (
        <div className="text-gray-600">No training results found.</div>
      ) : (
        <div className="grid gap-4">
          {results.map((result) => (
            <div
              key={result.session_id}
              className="border border-gray-200 rounded-xl p-4 shadow-sm bg-white hover:shadow-md transition"
            >
              <p><span className="font-medium">Session ID:</span> {result.session_id}</p>
              <p><span className="font-medium">Accuracy:</span> {result.accuracy}</p>
              <p><span className="font-medium">Model Name:</span> {result.model_name || "N/A"}</p>
              <p><span className="font-medium">Created At:</span> {result.created_at || "N/A"}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TrainingResults;
