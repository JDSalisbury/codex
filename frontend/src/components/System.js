import React, { use, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import {
  fetchOperator,
  selectOperator,
  selectOperatorLoading,
  selectOperatorError,
} from "../store/slices/operatorSlice";
import { useAuth } from "../context/AuthContext";
import "./System.css";
import { useEscapeToMain } from "../hooks/useEscapeToMain";

const System = () => {
  useEscapeToMain();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { operatorId, logout, setId } = useAuth();
  const operator = useSelector(selectOperator);
  const loading = useSelector(selectOperatorLoading);
  const error = useSelector(selectOperatorError);

  const [selectedOption, setSelectedOption] = useState(0);
  const [showKeyGuide, setShowKeyGuide] = useState(false);

  const menuOptions = [
    { name: "SAVE_DATA", label: "SAVE DATA", action: () => handleSaveData() },
    { name: "LOAD_DATA", label: "LOAD DATA", action: () => handleLoadData() },
    { name: "OPTIONS", label: "OPTIONS", action: () => handleOptions() },
    { name: "QUIT_GAME", label: "QUIT GAME", action: () => handleQuitGame() },
  ];

  useEffect(() => {
    // Fetch operator data on mount if we have an operator ID
    if (operatorId) {
      dispatch(fetchOperator(operatorId));
    }
  }, [dispatch, operatorId]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "ArrowUp") {
        setSelectedOption((prev) =>
          prev > 0 ? prev - 1 : menuOptions.length - 1
        );
      } else if (e.key === "ArrowDown") {
        setSelectedOption((prev) =>
          prev < menuOptions.length - 1 ? prev + 1 : 0
        );
      } else if (e.key === "Enter") {
        menuOptions[selectedOption].action();
      } else if (e.key === "Escape") {
        setShowKeyGuide((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedOption]);

  useEffect(() => {
    if (!operatorId) {
      setId();
    }
  }, []);

  const handleSaveData = () => {
    console.log("Save data functionality coming soon");
    // TODO: Implement save functionality
  };

  const handleLoadData = () => {
    console.log("Load data functionality coming soon");
    // TODO: Implement load functionality
  };

  const handleOptions = () => {
    console.log("Options menu coming soon");
    // TODO: Navigate to options submenu
  };

  const handleQuitGame = () => {
    if (window.confirm("Return to main menu?")) {
      logout();
      navigate("/");
    }
  };

  // Calculate mission stats
  const calculateStats = () => {
    if (!operator)
      return { sortie: 0, successRate: "0.00", failure: 0, credits: 0 };

    const sortie = operator.wins + operator.loses;
    const successRate =
      sortie > 0 ? ((operator.wins / sortie) * 100).toFixed(2) : "0.00";

    return {
      sortie,
      successRate,
      failure: operator.loses,
      credits: operator.bits,
    };
  };

  const stats = calculateStats();

  return (
    <div className="system-container">
      <div className="system-header">
        <h1 className="system-title">SYSTEM</h1>
        <button
          className="key-guide-btn"
          onClick={() => setShowKeyGuide(!showKeyGuide)}
        >
          <span className="key-guide-icon">⌨</span> KEY GUIDE
        </button>
      </div>

      <div className="system-content">
        {/* Left Menu */}
        <div className="system-menu">
          {menuOptions.map((option, index) => (
            <button
              key={option.name}
              className={`system-menu-item ${
                index === selectedOption ? "selected" : ""
              }`}
              onClick={() => {
                setSelectedOption(index);
                option.action();
              }}
              onMouseEnter={() => setSelectedOption(index)}
            >
              {option.label}
            </button>
          ))}
        </div>

        {/* Right Panel - Operator Data */}
        <div className="operator-data-panel">
          <div className="panel-header">
            <h2>OPERATOR DATA</h2>
          </div>

          {loading ? (
            <div className="loading-state">
              <p>LOADING OPERATOR DATA...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>ERROR: {error}</p>
              <button
                onClick={() =>
                  operatorId && dispatch(fetchOperator(operatorId))
                }
              >
                RETRY
              </button>
            </div>
          ) : !operator ? (
            <div className="no-data-state">
              <div className="operator-info-grid">
                <div className="info-row">
                  <span className="info-label">OPERATOR:</span>
                  <span className="info-value">[NO DATA]</span>
                </div>
                <div className="info-row">
                  <span className="info-label">RANK:</span>
                  <span className="info-value rank-badge">--</span>
                </div>
                <div className="info-row">
                  <span className="info-label">CALL SIGN:</span>
                  <span className="info-value">---</span>
                </div>
                <div className="info-row">
                  <span className="info-label">AC NAME:</span>
                  <span className="info-value">---</span>
                </div>
              </div>

              <div className="mission-report">
                <h3>MISSION REPORT</h3>
                <div className="report-grid">
                  <div className="report-item">
                    <span className="report-label">SORTIE:</span>
                    <span className="report-value">0</span>
                  </div>
                  <div className="report-item">
                    <span className="report-label">SUCCESS:</span>
                    <span className="report-value success">0.00%</span>
                  </div>
                  <div className="report-item">
                    <span className="report-label">FAILURE:</span>
                    <span className="report-value failure">0</span>
                  </div>
                  <div className="report-item">
                    <span className="report-label">CREDIT:</span>
                    <span className="report-value credits">0c</span>
                  </div>
                </div>
              </div>

              <div className="no-data-notice">
                <p>Connect to operator viewset to load data</p>
                <p className="hint">Update TEMP_OPERATOR_ID in System.js</p>
              </div>
            </div>
          ) : (
            <div className="operator-info">
              <div className="operator-info-grid">
                <div className="info-row">
                  <span className="info-label">OPERATOR:</span>
                  <span className="info-value">{operator.id || "UNKNOWN"}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">RANK:</span>
                  <span className="info-value rank-badge">
                    {operator.rank || "F"}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">CALL SIGN:</span>
                  <span className="info-value">
                    {operator.call_sign || "000"}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">LEVEL:</span>
                  <span className="info-value">{operator.lvl || 0}</span>
                </div>
              </div>

              <div className="mission-report">
                <h3>MISSION REPORT</h3>
                <div className="report-grid">
                  <div className="report-item">
                    <span className="report-label">SORTIE:</span>
                    <span className="report-value">{stats.sortie}</span>
                  </div>
                  <div className="report-item">
                    <span className="report-label">SUCCESS:</span>
                    <span className="report-value success">
                      {stats.successRate}%
                    </span>
                  </div>
                  <div className="report-item">
                    <span className="report-label">FAILURE:</span>
                    <span className="report-value failure">
                      {stats.failure}
                    </span>
                  </div>
                  <div className="report-item">
                    <span className="report-label">CREDIT:</span>
                    <span className="report-value credits">
                      {stats.credits.toLocaleString()}c
                    </span>
                  </div>
                  <div className="report-item">
                    <span className="report-label">PREMIUM:</span>
                    <span className="report-value premium">
                      {operator.premium || 0}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="system-footer">
        <button onClick={() => navigate("/menu")} className="back-btn">
          ESC - BACK TO MENU
        </button>
      </div>

      {showKeyGuide && (
        <div className="key-guide-overlay">
          <div className="key-guide-panel">
            <h2>KEY GUIDE</h2>
            <div className="key-guide-content">
              <div className="key-item">
                <span className="key">↑/↓</span>
                <span className="desc">Navigate menu</span>
              </div>
              <div className="key-item">
                <span className="key">ENTER</span>
                <span className="desc">Select option</span>
              </div>
              <div className="key-item">
                <span className="key">ESC</span>
                <span className="desc">Toggle guide / Back</span>
              </div>
            </div>
            <button onClick={() => setShowKeyGuide(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default System;
