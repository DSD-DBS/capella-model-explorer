// Copyright DB InfraGO AG and contributors
// SPDX-License-Identifier: Apache-2.0

import { useState } from "react";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { API_BASE_URL, ROUTE_PREFIX } from "./APIConfig";
import "./App.css";
import { HomeView } from "./views/HomeView";
import { TemplateView } from "./views/TemplateView";

function App() {
    const [count, setCount] = useState(0);

    return (
        <Router basename={ROUTE_PREFIX}>
            <Routes>
                <Route path="/" element={<HomeView />} />
                <Route
                    path="/:templateName"
                    element={
                        <TemplateView endpoint={`${API_BASE_URL}/views/`} />
                    }
                />
                <Route
                    path="/:templateName/:objectID"
                    element={
                        <TemplateView endpoint={`${API_BASE_URL}/views/`} />
                    }
                />
            </Routes>
        </Router>
    );
}

export default App;
