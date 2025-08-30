import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Bills from "./pages/Bills";
import Debt from "./pages/Debt.jsx";
import BudgetArena from "./pages/BudgetArena.jsx";
import Paychecks from "./pages/Paychecks.jsx";
import Forecast from "./pages/Forecast";
import Awards from "./pages/Awards.jsx";
import Navbar from "./components/Navbar";

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bills" element={<Bills />} />
          <Route path="/debt" element={<Debt />} />
          <Route path="/arena" element={<BudgetArena />} />
          <Route path="/forecast" element={<Forecast />} />
          <Route path="/awards" element={<Awards />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
