import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

import App from './App'
import SensorUpload from './pages/SensorUpload'
import GestureManager from './pages/GestureManager'
import TrainingResults from './pages/TrainingResults'

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/sensor" element={<SensorUpload />} />
      <Route path="/gestures" element={<GestureManager />} />
      <Route path="/training" element={<TrainingResults />} />
    </Routes>
  </BrowserRouter>
)
