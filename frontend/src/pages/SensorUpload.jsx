import axios from 'axios'
import { useState } from 'react'

export default function SensorUpload() {
  const [formData, setFormData] = useState({
    values: [],
    gesture: '',
    device_id: 'glove-1',
  })

  const handleUpload = async () => {
    try {
      const res = await axios.post('http://localhost:8000/sensor-data', formData)
      alert('Uploaded!')
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Upload Sensor Data</h1>
      <textarea
        className="border p-2 w-full h-40 my-2"
        placeholder="Enter 11 comma-separated values"
        onChange={(e) => {
          const raw = e.target.value.split(',').map(Number)
          setFormData({ ...formData, values: raw })
        }}
      />
      <input
        className="border p-2 w-full mb-2"
        placeholder="Gesture name"
        onChange={(e) => setFormData({ ...formData, gesture: e.target.value })}
      />
      <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={handleUpload}>
        Upload
      </button>
    </div>
  )
}
