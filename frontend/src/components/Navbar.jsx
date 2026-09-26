import React from "react";
import { Link, NavLink } from "react-router-dom";
import { useCart } from "../context/CartContext.jsx";

export default function Navbar() {
  const { count } = useCart();

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        <span className="brand-mark">P-C</span>
        <span className="brand-name">PayCom</span>
      </Link>

      <nav className="nav-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
          Catalog
        </NavLink>
        <NavLink to="/cart" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
          Cart
          {count > 0 && <span className="cart-badge">{count}</span>}
        </NavLink>
        <NavLink to="/privacy" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
          Privacy
        </NavLink>
      </nav>
    </header>
  );
}
