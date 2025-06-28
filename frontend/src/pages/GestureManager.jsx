import { useEffect, useState } from 'react'
import axios from 'axios'

export default function GestureManager() {
  const [gestures, setGestures] = useState([])

  const fetchGestures = async () => {
    try {
      const res = await axios.get('http://localhost:8000/gestures/')
      setGestures(res.data.data) // ✅ Use .data.data to extract gesture list
    } catch (err) {
      console.error('Failed to fetch gestures:', err)
    }
  }

  useEffect(() => {
    fetchGestures()
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Gestures</h1>
      <ul className="space-y-2">
        {gestures.map((g) => (
          <li key={g.session_id} className="border p-2 rounded">
            <strong>{g.gesture_label || 'No label'}</strong> (Session: {g.session_id})
          </li>
        ))}
      </ul>
    </div>
  )
}
