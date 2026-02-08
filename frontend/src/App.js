import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Login from "./components/Login";
import MainMenu from "./components/MainMenu";
import Garage from "./components/Garage";
import Mission from "./components/Mission";
import Mail from "./components/Mail";
import Arena from "./components/Arena";
import Battle from "./components/Battle";
import System from "./components/System";
import Scrapyard from "./components/Scrapyard";
import CyberCodex from "./components/CyberCodex";
import "./App.css";

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/menu" element={<MainMenu />} />
            <Route path="/garage" element={<Garage />} />
            <Route path="/cybercodex" element={<CyberCodex />} />
            <Route path="/mission" element={<Mission />} />
            <Route path="/mail" element={<Mail />} />
            <Route path="/arena" element={<Arena />} />
            <Route path="/battle/:battleId" element={<Battle />} />
            <Route path="/scrapyard" element={<Scrapyard />} />
            <Route path="/system" element={<System />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
