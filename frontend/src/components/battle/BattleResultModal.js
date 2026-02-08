// frontend/src/components/battle/BattleResultModal.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './BattleResultModal.css';

const BattleResultModal = ({ result, rewards, npcName, onClose }) => {
  const navigate = useNavigate();
  const isWin = result === 'win';

  const handleReturn = () => {
    onClose();
    navigate('/arena');
  };

  return (
    <div className="result-modal-overlay">
      <div className={`result-modal ${isWin ? 'win' : 'lose'}`}>
        <div className="result-header">
          <h1 className="result-title">
            {isWin ? 'VICTORY' : 'DEFEAT'}
          </h1>
          <p className="result-subtitle">
            {isWin
              ? `You defeated ${npcName}!`
              : `${npcName} was too strong...`}
          </p>
        </div>

        {isWin && rewards && (
          <div className="rewards-section">
            <h2>REWARDS</h2>
            <div className="rewards-list">
              {rewards.bits > 0 && (
                <div className="reward-item">
                  <span className="reward-icon">$</span>
                  <span className="reward-value">{rewards.bits}</span>
                  <span className="reward-label">BITS</span>
                </div>
              )}
              {rewards.exp > 0 && (
                <div className="reward-item">
                  <span className="reward-icon">*</span>
                  <span className="reward-value">{rewards.exp}</span>
                  <span className="reward-label">EXP</span>
                </div>
              )}
            </div>
          </div>
        )}

        {!isWin && (
          <div className="defeat-message">
            <p>Don't give up! Train your cores and try again.</p>
          </div>
        )}

        <div className="result-actions">
          <button className="result-btn primary" onClick={handleReturn}>
            RETURN TO ARENA
          </button>
        </div>
      </div>
    </div>
  );
};

export default BattleResultModal;
