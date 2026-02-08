import React from "react";
import { useNavigate } from "react-router-dom";
import "./PageTemplate.css";
import { useEscapeToMain } from "../hooks/useEscapeToMain";

const Mission = () => {
  const navigate = useNavigate();
  useEscapeToMain();

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>MISSION</h1>
        <button onClick={() => navigate("/menu")} className="back-btn">
          BACK TO MENU
        </button>
      </div>
      <div className="page-content">
        <p className="coming-soon">Mission system coming soon...</p>
        <p className="description">
          Accept contracts, complete objectives, and earn rewards.
        </p>
      </div>
    </div>
  );
};

export default Mission;
