import React, { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./MainMenu.css";

const menuItems = [
  { name: "MISSION", path: "/mission", description: "Start a new mission." },
  { name: "MAIL", path: "/mail", description: "Check your messages." },
  { name: "ARENA", path: "/arena", description: "Enter the combat arena." },
  {
    name: "GARAGE",
    path: "/garage",
    description: "Access your cores and upgrades.",
  },
  {
    name: "CYBER_CODEX",
    path: "/cybercodex",
    description: "View the CyberCodex.",
  },
  {
    name: "SCRAPYARD",
    path: "/scrapyard",
    description: "Manage your s[crap].",
  },
  { name: "SYSTEM", path: "/system", description: "Adjust system settings." },
  // { name: "LOGOUT", path: "/", description: "Return to login screen." },
];

const MainMenu = () => {
  const navigate = useNavigate();
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [showKeyGuide, setShowKeyGuide] = useState(false);
  const [menuItemDescription, setMenuItemDescription] =
    useState("Welcome to CoDEX");

  const handleMenuClick = (path) => {
    navigate(path);
  };

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "ArrowUp") {
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : menuItems.length - 1
        );
      } else if (e.key === "ArrowDown") {
        setSelectedIndex((prev) =>
          prev < menuItems.length - 1 ? prev + 1 : 0
        );
      } else if (e.key === "Enter") {
        setSelectedIndex((current) => {
          navigate(menuItems[current].path);
          return current;
        });
      } else if (e.key === "Escape") {
        setShowKeyGuide((prev) => !prev);
      }
    },
    [navigate]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    setMenuItemDescription(menuItems[selectedIndex].description);
  }, [selectedIndex]);

  return (
    <div className="main-menu">
      <div className="background-overlay"></div>

      <div className="menu-header">
        <h1 className="menu-title">MAIN MENU</h1>
        <button
          className="key-guide-btn"
          onClick={() => setShowKeyGuide(!showKeyGuide)}
        >
          <span className="start-text">START</span> KEY GUIDE
        </button>
      </div>

      <div className="menu-content">
        <div className="menu-items">
          {menuItems.map((item, index) => (
            <button
              key={item.name}
              className={`menu-item ${
                index === selectedIndex ? "selected" : ""
              }`}
              onClick={() => handleMenuClick(item.path)}
              onMouseEnter={() => setSelectedIndex(index)}
              onMouseOver={() => setMenuItemDescription(item.description)}
              onFocus={() => setMenuItemDescription(item.description)}
              onSelect={() => setMenuItemDescription(item.description)}
            >
              {item.name}
            </button>
          ))}
        </div>

        <div className="background-graphic">
          <div className="cyber-circle"></div>
          <div className="tech-lines"></div>
        </div>
      </div>

      <div className="menu-footer">
        <p className="footer-text">{menuItemDescription}</p>
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
                <span className="desc">Select</span>
              </div>
              <div className="key-item">
                <span className="key">ESC</span>
                <span className="desc">Toggle guide</span>
              </div>
            </div>
            <button onClick={() => setShowKeyGuide(false)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainMenu;
