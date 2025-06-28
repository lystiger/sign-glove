import { useEffect, useState } from 'react'
import axios from 'axios'

export default function GestureManager() {
  const [gestures, setGestures] = useState([])

  const fetchGestures = async () => {
    const res = await axios.get('http://localhost:8000/gestures')
    setGestures(res.data)
  }

  useEffect(() => {
    fetchGestures()
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Gestures</h1>
      <ul className="space-y-2">
        {gestures.map((g) => (
          <li key={g.name} className="border p-2 rounded">
            <strong>{g.name}</strong>: {g.description}
          </li>
        ))}
      </ul>
    </div>
  )
}
