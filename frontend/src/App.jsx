import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import { WiredTemplatesList } from './components/WiredTemplatesList'
import { TemplateView } from './components/TemplateView'
import { InstanceView } from './components/InstanceView'


function App() {
  const [count, setCount] = useState(0)

  return (
    <Router>
      <Routes>
        <Route path="/templates" element={<WiredTemplatesList endpoint="http://localhost:8000/api/templates" />} />
        <Route path="/templates/:templateName" element={<TemplateView endpoint="http://localhost:8000/api/templates/" />} />
        <Route path="/templates/:templateName/:objectID" element={<TemplateView endpoint="http://localhost:8000/api/templates/" />} />
      </Routes>
    </Router>
  )
}

export default App
