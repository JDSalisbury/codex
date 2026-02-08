// frontend/src/components/battle/ResourcePools.js
import React from 'react';
import './ResourcePools.css';

const ResourcePools = ({ energyPool = 0, physicalPool = 0, isEnemy = false }) => {
  const maxDisplay = 50; // Visual cap for the bar

  return (
    <div className={`resource-pools ${isEnemy ? 'enemy' : 'player'}`}>
      <div className="pool energy-pool">
        <div className="pool-label">
          <span className="pool-icon">E</span>
          <span className="pool-name">ENERGY</span>
        </div>
        <div className="pool-bar-container">
          <div
            className="pool-bar-fill energy"
            style={{ width: `${Math.min(100, (energyPool / maxDisplay) * 100)}%` }}
          />
        </div>
        <span className="pool-value">{energyPool}</span>
      </div>

      <div className="pool physical-pool">
        <div className="pool-label">
          <span className="pool-icon">P</span>
          <span className="pool-name">PHYSICAL</span>
        </div>
        <div className="pool-bar-container">
          <div
            className="pool-bar-fill physical"
            style={{ width: `${Math.min(100, (physicalPool / maxDisplay) * 100)}%` }}
          />
        </div>
        <span className="pool-value">{physicalPool}</span>
      </div>
    </div>
  );
};

export default ResourcePools;
