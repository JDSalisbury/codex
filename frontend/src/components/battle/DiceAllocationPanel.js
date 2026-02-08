// frontend/src/components/battle/DiceAllocationPanel.js
import React, { useState, useEffect } from 'react';
import './DiceAllocationPanel.css';

const DiceAllocationPanel = ({ diceRolls = [], onAllocate, disabled = false }) => {
  const [allocations, setAllocations] = useState({});

  // Reset allocations when dice rolls change
  useEffect(() => {
    const initial = {};
    diceRolls.forEach((roll) => {
      initial[roll.core_id] = null;
    });
    setAllocations(initial);
  }, [diceRolls]);

  const handleAllocation = (coreId, pool) => {
    setAllocations((prev) => ({
      ...prev,
      [coreId]: pool,
    }));
  };

  const allAllocated = diceRolls.every((roll) => allocations[roll.core_id] !== null);

  const handleSubmit = () => {
    const allocationList = diceRolls.map((roll) => ({
      core_id: roll.core_id,
      pool: allocations[roll.core_id],
    }));
    onAllocate(allocationList);
  };

  const totalEnergy = diceRolls.reduce((sum, roll) => {
    if (allocations[roll.core_id] === 'energy') {
      return sum + roll.roll_value;
    }
    return sum;
  }, 0);

  const totalPhysical = diceRolls.reduce((sum, roll) => {
    if (allocations[roll.core_id] === 'physical') {
      return sum + roll.roll_value;
    }
    return sum;
  }, 0);

  return (
    <div className="dice-allocation-panel">
      <h3 className="panel-title">ALLOCATE DICE</h3>

      <div className="dice-list">
        {diceRolls.map((roll) => (
          <div key={roll.core_id} className="dice-row">
            <div className="dice-info">
              <span className="core-name">{roll.core_name}</span>
              <div className={`dice-value d${roll.roll_value > 4 ? 'high' : 'low'}`}>
                {roll.roll_value}
              </div>
            </div>

            <div className="allocation-buttons">
              <button
                className={`alloc-btn energy ${allocations[roll.core_id] === 'energy' ? 'selected' : ''}`}
                onClick={() => handleAllocation(roll.core_id, 'energy')}
                disabled={disabled}
              >
                ENERGY
              </button>
              <button
                className={`alloc-btn physical ${allocations[roll.core_id] === 'physical' ? 'selected' : ''}`}
                onClick={() => handleAllocation(roll.core_id, 'physical')}
                disabled={disabled}
              >
                PHYSICAL
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="allocation-preview">
        <div className="preview-item energy">
          <span>Energy:</span>
          <span className="preview-value">+{totalEnergy}</span>
        </div>
        <div className="preview-item physical">
          <span>Physical:</span>
          <span className="preview-value">+{totalPhysical}</span>
        </div>
      </div>

      <button
        className="confirm-btn"
        onClick={handleSubmit}
        disabled={disabled || !allAllocated}
      >
        {allAllocated ? 'CONFIRM ALLOCATION' : 'ASSIGN ALL DICE'}
      </button>
    </div>
  );
};

export default DiceAllocationPanel;
