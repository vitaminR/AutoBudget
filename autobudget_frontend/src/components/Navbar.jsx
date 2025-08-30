import React from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
      <div className="container">
        <NavLink className="navbar-brand" to="/">
          AutoBudget
        </NavLink>
        <div className="navbar-nav">
          <NavLink className="nav-link" to="/" end>
            Dashboard
          </NavLink>
          <NavLink className="nav-link" to="/bills">
            Bills
          </NavLink>
          <NavLink className="nav-link" to="/debt">
            Debt
          </NavLink>
          <NavLink className="nav-link" to="/arena">
            Budget Arena
          </NavLink>
          <NavLink className="nav-link" to="/paychecks">
            Paychecks
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;