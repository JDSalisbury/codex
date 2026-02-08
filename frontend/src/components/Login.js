import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  createOperator,
  fetchOperator,
  selectOperator,
  selectOperatorLoading,
  selectOperatorError,
  clearError,
} from '../store/slices/operatorSlice';
import { useAuth } from '../context/AuthContext';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { login } = useAuth();
  const operator = useSelector(selectOperator);
  const loading = useSelector(selectOperatorLoading);
  const error = useSelector(selectOperatorError);

  const [selectedOption, setSelectedOption] = useState(0);
  const [showNewGamePrompt, setShowNewGamePrompt] = useState(false);
  const [showContinuePrompt, setShowContinuePrompt] = useState(false);
  const [callSign, setCallSign] = useState('');
  const [operatorId, setOperatorId] = useState('');
  const [formError, setFormError] = useState('');

  const menuOptions = [
    { name: 'START_NEW_GAME', label: 'START NEW GAME' },
    { name: 'CONTINUE', label: 'CONTINUE' },
  ];

  const handleKeyDown = useCallback(
    (e) => {
      if (showNewGamePrompt || showContinuePrompt) return;

      if (e.key === 'ArrowUp') {
        setSelectedOption((prev) => (prev > 0 ? prev - 1 : menuOptions.length - 1));
      } else if (e.key === 'ArrowDown') {
        setSelectedOption((prev) => (prev < menuOptions.length - 1 ? prev + 1 : 0));
      } else if (e.key === 'Enter') {
        handleSelect();
      }
    },
    [showNewGamePrompt, showContinuePrompt, selectedOption]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleSelect = () => {
    const selected = menuOptions[selectedOption];
    if (selected.name === 'START_NEW_GAME') {
      setShowNewGamePrompt(true);
      setFormError('');
      dispatch(clearError());
    } else if (selected.name === 'CONTINUE') {
      // Check if there's a stored operator ID
      const storedId = localStorage.getItem('codex_operator_id');
      if (storedId) {
        setOperatorId(storedId);
      }
      setShowContinuePrompt(true);
      setFormError('');
      dispatch(clearError());
    }
  };

  const handleCreateOperator = async (e) => {
    e.preventDefault();

    if (!callSign.trim()) {
      setFormError('Call sign cannot be empty');
      return;
    }

    if (callSign.length > 120) {
      setFormError('Call sign must be 120 characters or less');
      return;
    }

    try {
      const result = await dispatch(
        createOperator({ call_sign: callSign.trim() })
      ).unwrap();

      login(result.id);
      navigate('/menu');
    } catch (err) {
      setFormError(err || 'Failed to create operator');
    }
  };

  const handleLoadOperator = async (e) => {
    e.preventDefault();

    if (!operatorId.trim()) {
      setFormError('Operator ID cannot be empty');
      return;
    }

    try {
      const result = await dispatch(fetchOperator(operatorId.trim())).unwrap();
      login(result.id);
      navigate('/menu');
    } catch (err) {
      setFormError(err || 'Failed to load operator');
    }
  };

  const handleCancel = () => {
    setShowNewGamePrompt(false);
    setShowContinuePrompt(false);
    setCallSign('');
    setOperatorId('');
    setFormError('');
    dispatch(clearError());
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="cyber-grid"></div>
        <div className="tech-overlay"></div>
      </div>

      <div className="login-content">
        <div className="logo-section">
          <h1 className="game-title">CoDEX</h1>
          <p className="game-subtitle">CORE DEPLOYMENT EXCHANGE</p>
          <div className="title-underline"></div>
        </div>

        {!showNewGamePrompt && !showContinuePrompt ? (
          <div className="menu-section">
            {menuOptions.map((option, index) => (
              <button
                key={option.name}
                className={`login-menu-item ${index === selectedOption ? 'selected' : ''}`}
                onClick={() => {
                  setSelectedOption(index);
                  handleSelect();
                }}
                onMouseEnter={() => setSelectedOption(index)}
              >
                {option.label}
              </button>
            ))}

            <div className="menu-hint">
              <p>Use ↑↓ to navigate, ENTER to select</p>
            </div>
          </div>
        ) : null}

        {showNewGamePrompt && (
          <div className="prompt-section">
            <h2>START NEW GAME</h2>
            <form onSubmit={handleCreateOperator} className="operator-form">
              <div className="form-group">
                <label htmlFor="callSign">ENTER CALL SIGN:</label>
                <input
                  type="text"
                  id="callSign"
                  value={callSign}
                  onChange={(e) => setCallSign(e.target.value)}
                  placeholder="Your operator call sign"
                  maxLength={120}
                  autoFocus
                  disabled={loading}
                />
                <span className="char-count">{callSign.length}/120</span>
              </div>

              {(formError || error) && (
                <div className="error-message">
                  {formError || error}
                </div>
              )}

              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'CREATING...' : 'CREATE OPERATOR'}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCancel}
                  disabled={loading}
                >
                  CANCEL
                </button>
              </div>
            </form>
          </div>
        )}

        {showContinuePrompt && (
          <div className="prompt-section">
            <h2>CONTINUE</h2>
            <form onSubmit={handleLoadOperator} className="operator-form">
              <div className="form-group">
                <label htmlFor="operatorId">ENTER OPERATOR ID:</label>
                <input
                  type="text"
                  id="operatorId"
                  value={operatorId}
                  onChange={(e) => setOperatorId(e.target.value)}
                  placeholder="Your operator UUID"
                  autoFocus
                  disabled={loading}
                />
                {operatorId ? (
                  <span className="input-hint success-hint">
                    Previous operator ID found - press LOAD OPERATOR to continue
                  </span>
                ) : (
                  <span className="input-hint">
                    Enter the UUID from your previous session
                  </span>
                )}
              </div>

              {(formError || error) && (
                <div className="error-message">
                  {formError || error}
                </div>
              )}

              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'LOADING...' : 'LOAD OPERATOR'}
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCancel}
                  disabled={loading}
                >
                  CANCEL
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      <div className="login-footer">
        <p className="version-info">v0.1.0 ALPHA</p>
      </div>
    </div>
  );
};

export default Login;
