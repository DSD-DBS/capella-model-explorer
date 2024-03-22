// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import { WiredTemplatesList } from './components/WiredTemplatesList'
import { TemplateView } from './views/TemplateView'
import { HomeView } from './views/HomeView'


function App() {
  const [count, setCount] = useState(0)

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomeView/>} />
        {/* <Route path="/views" element={<WiredTemplatesList endpoint="http://localhost:8000/api/views" />} /> */}
        <Route path="/:templateName" element={<TemplateView endpoint="http://localhost:8000/api/views/" />} />
        <Route path="/:templateName/:objectID" element={<TemplateView endpoint="http://localhost:8000/api/views/" />} />
      </Routes>
    </Router>
  )
}

export default App
