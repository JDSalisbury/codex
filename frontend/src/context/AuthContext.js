import { createContext, useContext, useState } from "react";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [operatorId, setOperatorId] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const setId = () => {
    const opId = localStorage.getItem("codex_operator_id");
    setOperatorId(opId);
  };

  const login = (opId) => {
    setOperatorId(opId);
    setIsAuthenticated(true);
    localStorage.setItem("codex_operator_id", opId);
  };

  const logout = () => {
    setOperatorId(null);
    setIsAuthenticated(false);
    // localStorage.removeItem("codex_operator_id");
  };

  const getStoredOperatorId = () => {
    return localStorage.getItem("codex_operator_id");
  };

  const value = {
    operatorId,
    isAuthenticated,
    login,
    logout,
    getStoredOperatorId,
    setId,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
