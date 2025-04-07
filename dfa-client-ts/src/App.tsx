import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import GraphEditorPage from './pages/GraphEditorPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<GraphEditorPage />} />
      </Routes>
    </Router>
  )
}

export default App
