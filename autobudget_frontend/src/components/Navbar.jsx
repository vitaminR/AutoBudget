import React from "react";
import { NavLink } from "react-router-dom";

const Navbar = () => (
  <nav className="navbar navbar-expand navbar-light bg-light">
    <div className="container">
      <NavLink className="navbar-brand" to="/">
        AutoBudget
      </NavLink>
      <div className="navbar-nav">
        <NavLink className="nav-link" to="/">
          Dashboard
        </NavLink>
        <NavLink className="nav-link" to="/bills">
          Bills
        </NavLink>
      </div>
    </div>
  </nav>
);

export default Navbar;
