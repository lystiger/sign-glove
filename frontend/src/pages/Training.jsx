import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Training() {
  const [results, setResults] = useState([])

  const fetchTrainingResults = async () => {
    const res = await axios.get('http://localhost:8000/training')
    setResults(res.data)
  }

  useEffect(() => {
    fetchTrainingResults()
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Training Results</h1>
      <ul className="space-y-2">
        {results.map((r, i) => (
          <li key={i} className="border p-2 rounded">
            <div>Session: {r.session_id}</div>
            <div>Accuracy: {r.accuracy}%</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
