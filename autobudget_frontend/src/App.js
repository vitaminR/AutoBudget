import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Bills from "./pages/Bills";
import Snowball from "./pages/Snowball.jsx";
import Forecast from "./pages/Forecast";
import Awards from "./pages/Awards.jsx";

function App() {
  return (
    <BrowserRouter>
      <nav className="navbar navbar-expand navbar-light bg-light">
        <div className="container">
          <NavLink className="navbar-brand" to="/">
            AutoBudget
          </NavLink>
          <div className="navbar-nav">
            <NavLink className="nav-link" to="/">
              Home
            </NavLink>
            <NavLink className="nav-link" to="/bills">
              Bills
            </NavLink>
            <NavLink className="nav-link" to="/debts">
              Debts
            </NavLink>
            <NavLink className="nav-link" to="/forecast">
              Forecast
            </NavLink>
            <NavLink className="nav-link" to="/awards">
              Awards
            </NavLink>
          </div>
        </div>
      </nav>
      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bills" element={<Bills />} />
          <Route path="/debts" element={<Snowball />} />
          <Route path="/forecast" element={<Forecast />} />
          <Route path="/awards" element={<Awards />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
