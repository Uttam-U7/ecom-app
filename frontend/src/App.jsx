import React from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import Cart from "./pages/Cart.jsx";
import Privacy from "./pages/Privacy.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/privacy" element={<Privacy />} />
      </Routes>
      <footer className="site-footer">
        <span>PayCom — a demo catalog. No real payments are made.</span>
      </footer>
    </div>
  );
}
