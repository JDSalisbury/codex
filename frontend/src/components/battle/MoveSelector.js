// frontend/src/components/battle/MoveSelector.js
import React from "react";
import "./MoveSelector.css";

const MoveSelector = ({
  moves = [],
  energyPool = 0,
  physicalPool = 0,
  selectedMove,
  onMoveSelect,
  onSwitch,
  onPass,
  onGainResource,
  disabled = false,
}) => {
  const canAffordMove = (move) => {
    if (move.dmg_type === "ENERGY") {
      return energyPool >= move.resource_cost;
    }
    return physicalPool >= move.resource_cost;
  };

  const handleMoveClick = (move) => {
    if (disabled || !canAffordMove(move)) return;
    onMoveSelect(move);
  };

  // Create a slot-based array to avoid duplicates
  const movesBySlot = [null, null, null, null];
  moves.forEach((move) => {
    const slotIndex = (move.slot || 1) - 1; // Convert 1-based slot to 0-based index
    if (slotIndex >= 0 && slotIndex < 4 && !movesBySlot[slotIndex]) {
      movesBySlot[slotIndex] = move;
    }
  });

  // Fill remaining slots with unassigned moves
  let unassignedIndex = 0;
  moves.forEach((move) => {
    if (!movesBySlot.includes(move)) {
      while (unassignedIndex < 4 && movesBySlot[unassignedIndex] !== null) {
        unassignedIndex++;
      }
      if (unassignedIndex < 4) {
        movesBySlot[unassignedIndex] = move;
      }
    }
  });

  return (
    <div className="move-selector">
      <div className="moves-grid-selector">
        {[0, 1, 2, 3].map((slotIndex) => {
          const move = movesBySlot[slotIndex];
          if (!move) {
            return (
              <div key={slotIndex} className="move-slot empty">
                <span className="empty-slot">---</span>
              </div>
            );
          }

          const affordable = canAffordMove(move);
          const isSelected = selectedMove?.id === move.id;

          return (
            <button
              key={`slot-${slotIndex}-${move.id}`}
              className={`move-slot ${move.dmg_type.toLowerCase()} ${affordable ? "" : "unaffordable"} ${isSelected ? "selected" : ""}`}
              onClick={() => handleMoveClick(move)}
              disabled={disabled || !affordable}
            >
              <div className="move-name">{move.name}</div>
              <div className="move-details">
                <span className={`move-type ${move.dmg_type.toLowerCase()}`}>
                  {move.dmg_type === "ENERGY" ? "ENG" : "PHY"}
                </span>
                <span className="move-damage">DMG: {move.dmg}</span>
                <span className="move-cost">Cost: {move.resource_cost}</span>
              </div>
              <div className="move-accuracy">
                ACC: {Math.round(move.accuracy * 100)}%
              </div>
            </button>
          );
        })}
      </div>

      <div className="action-buttons">
        <button
          className="action-btn gain-resource-btn"
          onClick={onGainResource}
          disabled={disabled}
        >
          GAIN RESOURCE
        </button>
        <button
          className="action-btn switch-btn"
          onClick={onSwitch}
          disabled={disabled}
        >
          SWITCH
        </button>
        <button
          className="action-btn pass-btn"
          onClick={onPass}
          disabled={disabled}
        >
          PASS
        </button>
      </div>
    </div>
  );
};

export default MoveSelector;
