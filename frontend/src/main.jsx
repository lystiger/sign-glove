import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'

import App from './App'
import SensorUpload from './pages/SensorUpload'
import GestureManager from './pages/GestureManager'
<<<<<<< HEAD
import TrainingResults from './pages/TrainingResults'
=======
import Training from './pages/Training'
>>>>>>> 7063632d6c164101fff2aef1ab06162405628e73

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/sensor" element={<SensorUpload />} />
      <Route path="/gestures" element={<GestureManager />} />
<<<<<<< HEAD
      <Route path="/training" element={<TrainingResults />} />
=======
      <Route path="/training" element={<Training />} />
>>>>>>> 7063632d6c164101fff2aef1ab06162405628e73
    </Routes>
  </BrowserRouter>
)
