import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AnalyzePage from "./pages/AnalyzePage";

function NavBar() {
  const location = useLocation();
  const currentPath = location.pathname;

  // Style for each button
  const buttonStyle = (path) => ({
    backgroundColor: currentPath === path ? "#2563eb" : "#ffffff", // blue if active, white if not
    color: currentPath === path ? "#ffffff" : "#1d4ed8",
    padding: "8px 16px",
    borderRadius: "6px",
    fontWeight: "bold",
    textDecoration: "none",
    boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
    transition: "background-color 0.2s",
  });

  return (
    <nav
      style={{
        backgroundColor: "#1d4ed8",
        padding: "16px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        color: "white",
      }}
    >
      <h1 style={{ fontSize: "20px", fontWeight: "bold" }}>🕵️ Phishing Detector</h1>
      <div style={{ display: "flex", gap: "8px" }}>
        <Link to="/" style={buttonStyle("/")}>
          Home
        </Link>
        <Link to="/analyze" style={buttonStyle("/analyze")}>
          Custom Scan
        </Link>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
      </Routes>
    </Router>
  );
}

export default App;