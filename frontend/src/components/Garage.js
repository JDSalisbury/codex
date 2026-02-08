import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import {
  fetchGarageByOperator,
  selectGarageLoading,
  selectGarageError,
  selectGarageCapacity,
} from "../store/slices/garageSlice";
import {
  fetchCores,
  selectAllCores,
  selectCoresLoading,
  decommissionCore,
  fetchCoreEquippedMoves,
  fetchCoreAvailableMoves,
  selectCoreEquippedMoves,
  selectCoreAvailableMoves,
  equipMove,
  unequipMove,
} from "../store/slices/coresSlice";
import { fetchOperator, selectOperator } from "../store/slices/operatorSlice";
import { useAuth } from "../context/AuthContext";
import "./Garage.css";
import { useEscapeToMain } from "../hooks/useEscapeToMain";

const Garage = () => {
  useEscapeToMain();

  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { operatorId, setId } = useAuth();

  const operator = useSelector(selectOperator);
  const cores = useSelector(selectAllCores);
  const capacity = useSelector(selectGarageCapacity);
  const garageLoading = useSelector(selectGarageLoading);
  const coresLoading = useSelector(selectCoresLoading);
  const garageError = useSelector(selectGarageError);

  const [selectedBayIndex, setSelectedBayIndex] = useState(0);
  const [selectedCore, setSelectedCore] = useState(null);
  const [showMoveManager, setShowMoveManager] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);

  // Get moves for selected core
  const equippedMoves = useSelector((state) =>
    selectedCore ? selectCoreEquippedMoves(selectedCore.id)(state) : [],
  );
  const availableMoves = useSelector((state) =>
    selectedCore ? selectCoreAvailableMoves(selectedCore.id)(state) : [],
  );

  // Fetch operator, garage and cores on mount
  useEffect(() => {
    if (operatorId) {
      dispatch(fetchOperator(operatorId));
      dispatch(fetchGarageByOperator(operatorId)).then((result) => {
        if (result.payload?.id) {
          dispatch(fetchCores(result.payload.id));
        }
      });
    }
  }, [dispatch, operatorId]);

  useEffect(() => {
    if (!operatorId) {
      setId();
    }
  }, [operatorId, setId]);

  // Update selected core when cores or bay index changes
  useEffect(() => {
    if (cores.length > 0 && selectedBayIndex < cores.length) {
      setSelectedCore(cores[selectedBayIndex]);
    } else {
      setSelectedCore(null);
    }
  }, [cores, selectedBayIndex]);

  // Fetch moves when a core is selected
  useEffect(() => {
    if (selectedCore?.id) {
      dispatch(fetchCoreEquippedMoves(selectedCore.id));
      dispatch(fetchCoreAvailableMoves(selectedCore.id));
    }
  }, [selectedCore?.id, dispatch]);

  const handlePrevBay = () => {
    const maxIndex = Math.max(cores.length, capacity.total) - 1;
    setSelectedBayIndex((prev) => (prev > 0 ? prev - 1 : maxIndex));
  };

  const handleNextBay = () => {
    const maxIndex = Math.max(cores.length, capacity.total) - 1;
    setSelectedBayIndex((prev) => (prev < maxIndex ? prev + 1 : 0));
  };

  const handleBayClick = (index) => {
    setSelectedBayIndex(index);
  };

  const handleDecommission = async (core) => {
    const confirmDecomm = window.confirm(
      `Decommission ${core.name}?\n\nThis will move it to the Scrapyard. You can recommission it later if needed.`,
    );

    if (confirmDecomm) {
      const result = await dispatch(decommissionCore(core.id));
      if (result.meta.requestStatus === "fulfilled") {
        // Refresh cores list
        if (operatorId) {
          dispatch(fetchGarageByOperator(operatorId)).then((garageResult) => {
            if (garageResult.payload?.id) {
              dispatch(fetchCores(garageResult.payload.id));
            }
          });
        }
        // Reset selected bay if needed
        if (selectedBayIndex >= cores.length - 1 && selectedBayIndex > 0) {
          setSelectedBayIndex(selectedBayIndex - 1);
        }
        alert(
          `${core.name} has been decommissioned and moved to the Scrapyard.`,
        );
      }
    }
  };

  const handleEquipMove = async (moveId, slot) => {
    if (!selectedCore) return;

    const result = await dispatch(
      equipMove({ coreId: selectedCore.id, moveId, slot }),
    );

    if (result.meta.requestStatus === "fulfilled") {
      // Refresh both equipped and available moves
      dispatch(fetchCoreEquippedMoves(selectedCore.id));
      dispatch(fetchCoreAvailableMoves(selectedCore.id));
      setSelectedSlot(null);
    } else {
      alert(result.payload || "Failed to equip move. Please try again.");
    }
  };

  const handleUnequipMove = async (slot) => {
    if (!selectedCore) return;

    const confirmUnequip = window.confirm(
      `Unequip move from slot ${slot}?\n\nThe move will return to your available pool.`,
    );

    if (confirmUnequip) {
      const result = await dispatch(
        unequipMove({ coreId: selectedCore.id, slot }),
      );

      if (result.meta.requestStatus === "fulfilled") {
        // Refresh both equipped and available moves
        dispatch(fetchCoreEquippedMoves(selectedCore.id));
        dispatch(fetchCoreAvailableMoves(selectedCore.id));
        alert(`Move unequipped from slot ${slot}`);
      } else {
        alert(result.payload || "Failed to unequip move. Please try again.");
      }
    }
  };

  const renderBaySlots = () => {
    const totalBays = capacity.total || 3;
    const slots = [];

    for (let i = 0; i < totalBays; i++) {
      const core = cores[i];
      const isSelected = i === selectedBayIndex;
      const bayNumber = String(i + 1).padStart(2, "0");

      slots.push(
        <div
          key={i}
          className={`bay-slot ${isSelected ? "selected" : ""} ${
            core ? "occupied" : "empty"
          }`}
          onClick={() => handleBayClick(i)}
        >
          <div className="bay-header">
            <span className="bay-number">BAY {bayNumber}</span>
            <span className={`bay-status ${core ? "active" : "inactive"}`}>
              {core ? "●" : "○"}
            </span>
          </div>
          <div className="bay-content">
            {core ? (
              <>
                <div className="core-icon">🔧</div>
                <div className="core-name">{core.name}</div>
                <div className="core-level">LVL {core.lvl}</div>
                <div className="core-rarity">{core.rarity}</div>
              </>
            ) : (
              <>
                <div className="empty-icon">➕</div>
                <div className="empty-text">Empty Bay</div>
              </>
            )}
          </div>
        </div>,
      );
    }

    return slots;
  };

  const renderCarouselDots = () => {
    const totalBays = capacity.total || 3;
    const dots = [];

    for (let i = 0; i < totalBays; i++) {
      dots.push(
        <span
          key={i}
          className={`carousel-dot ${i === selectedBayIndex ? "active" : ""}`}
          onClick={() => handleBayClick(i)}
        />,
      );
    }

    return dots;
  };

  if (garageLoading || coresLoading) {
    return (
      <div className="garage-container">
        <div className="garage-header">
          <h1 className="garage-title">GARAGE COMMAND CENTER</h1>
          <button onClick={() => navigate("/menu")} className="back-btn">
            BACK TO MENU
          </button>
        </div>
        <div className="loading-state">
          <p>LOADING GARAGE DATA...</p>
        </div>
      </div>
    );
  }

  if (garageError) {
    return (
      <div className="garage-container">
        <div className="garage-header">
          <h1 className="garage-title">GARAGE COMMAND CENTER</h1>
          <button onClick={() => navigate("/menu")} className="back-btn">
            BACK TO MENU
          </button>
        </div>
        <div className="error-state">
          <p>ERROR: {garageError}</p>
          <button
            onClick={() =>
              operatorId && dispatch(fetchGarageByOperator(operatorId))
            }
          >
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="garage-container">
      <div className="garage-header">
        <h1 className="garage-title">🚀 GARAGE COMMAND CENTER</h1>
        <button onClick={() => navigate("/menu")} className="back-btn">
          BACK TO MENU
        </button>
      </div>

      <div className="profile-bar">
        <div className="profile-info">
          <span className="profile-label">OPERATOR:</span>
          <span className="profile-value">
            {operator?.call_sign || "Unknown"}
          </span>
        </div>
        <div className="profile-info">
          <span className="profile-label">CREDITS:</span>
          <span className="profile-value credits">
            {operator?.bits?.toLocaleString() || 0}
          </span>
        </div>
        <div className="profile-info">
          <span className="profile-label">CAPACITY:</span>
          <span className="profile-value">
            {cores.length} / {capacity.total}
          </span>
        </div>
      </div>

      <div className="bay-carousel">
        <button className="carousel-nav left" onClick={handlePrevBay}>
          ◀
        </button>

        <div className="bay-slots-container">{renderBaySlots()}</div>

        <button className="carousel-nav right" onClick={handleNextBay}>
          ▶
        </button>
      </div>

      <div className="carousel-dots">{renderCarouselDots()}</div>

      <div className="core-details-section">
        <h2 className="section-title">🔍 CORE DETAILS</h2>

        {selectedCore ? (
          <div className="core-details">
            <div className="core-preview">
              {selectedCore.image_url ? (
                <img
                  src={selectedCore.image_url || ""}
                  alt={selectedCore.name}
                  className="core-image-large"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src =
                      "https://via.placeholder.com/150?text=No+Image";
                  }}
                />
              ) : (
                <div className="preview-placeholder">
                  <div className="core-icon-large">🔧</div>
                  <div className="preview-label">CORE PREVIEW</div>
                </div>
              )}
            </div>

            <div className="core-info">
              {/* Move Type Identity Banner */}
              <div className="core-type-banner">
                <div className="type-banner-icon">⚡</div>
                <div className="type-banner-details">
                  <span className="type-banner-label">MOVE TYPE IDENTITY</span>
                  <span
                    className={`type-banner-value type-${
                      selectedCore.type?.toLowerCase() || "unknown"
                    }`}
                  >
                    {selectedCore.type || "Unknown"}
                  </span>
                  <span className="type-banner-hint">
                    Move compatibility & combat interactions
                  </span>
                </div>
                <div className="type-banner-icon">⚡</div>
              </div>

              {/* Growth Tracks Banner */}
              <div className="core-tracks-banner">
                <div className="tracks-banner-icon">📈</div>
                <div className="tracks-banner-details">
                  <span className="tracks-banner-label">GROWTH TRACKS</span>
                  <span className="tracks-banner-value">
                    {selectedCore.upgrade_info?.tracks?.length > 0
                      ? selectedCore.upgrade_info.tracks
                          .map((t) => t.name || t)
                          .join(", ")
                      : "Standard Growth"}
                  </span>
                  <span className="tracks-banner-hint">
                    Leveling pattern & stat progression
                  </span>
                </div>
                <div className="tracks-banner-icon">📈</div>
              </div>

              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">NAME:</span>
                  <span className="info-value">{selectedCore.name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">STATUS:</span>
                  <span className="info-value status">ACTIVE</span>
                </div>
                <div className="info-item">
                  <span className="info-label">LEVEL:</span>
                  <span className="info-value">{selectedCore.lvl}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">RARITY:</span>
                  <span
                    className={`info-value rarity-${selectedCore.rarity?.toLowerCase()}`}
                  >
                    {selectedCore.rarity}
                  </span>
                </div>
                <div className="info-item">
                  <span className="info-label">PRICE:</span>
                  <span className="info-value">{selectedCore.price}c</span>
                </div>
                <div className="info-item">
                  <span className="info-label">MOVE SLOTS:</span>
                  <span className="info-value">
                    {selectedCore.battle_info?.equip_slots || 4}
                  </span>
                </div>
              </div>

              {selectedCore?.battle_info && (
                <div className="battle-stats">
                  <h3>COMBAT STATS</h3>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-label">HP:</span>
                      <span className="stat-value">
                        {selectedCore.battle_info.hp}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">PHYSICAL:</span>
                      <span className="stat-value">
                        {selectedCore.battle_info.physical}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">ENERGY:</span>
                      <span className="stat-value">
                        {selectedCore.battle_info.energy}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">DEFENSE:</span>
                      <span className="stat-value">
                        {selectedCore.battle_info.defense}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">SHIELD:</span>
                      <span className="stat-value">
                        {selectedCore.battle_info.shield}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">SPEED:</span>
                      <span className="stat-value">
                        {selectedCore.battle_info.speed}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div className="loadout-section">
                <h3>📦 MOVE LOADOUT</h3>
                <div className="loadout-slots">
                  {[1, 2, 3, 4].map((slot) => {
                    const equippedMove = equippedMoves.find(
                      (em) => em.slot === slot,
                    );
                    return (
                      <div
                        key={slot}
                        className={`loadout-slot ${
                          equippedMove ? "equipped" : "empty"
                        }`}
                        onClick={() => setSelectedSlot(slot)}
                      >
                        <div className="slot-header">
                          <span className="slot-number">SLOT {slot}</span>
                          {equippedMove && (
                            <button
                              className="unequip-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUnequipMove(slot);
                              }}
                            >
                              ✖
                            </button>
                          )}
                        </div>
                        {equippedMove ? (
                          <div className="move-info">
                            <div className="move-name">
                              {equippedMove.move?.name || "Unknown Move"}
                            </div>
                            <div className="move-stats-mini">
                              <span className="mini-stat">
                                DMG: {equippedMove.move?.dmg || 0}
                              </span>
                              <span className="mini-stat">
                                COST: {equippedMove.move?.resource_cost || 0}
                              </span>
                            </div>
                            <div className="move-type-mini">
                              <span
                                className={`type-badge-mini type-${equippedMove.move?.type?.toLowerCase()}`}
                              >
                                {equippedMove.move?.type}
                              </span>
                              <span
                                className={`dmg-badge-mini dmg-${equippedMove.move?.dmg_type?.toLowerCase()}`}
                              >
                                {equippedMove.move?.dmg_type}
                              </span>
                            </div>
                          </div>
                        ) : (
                          <div className="empty-slot-message">
                            <div className="empty-icon">➕</div>
                            <span>Click to equip</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
                <button
                  className="manage-moves-btn"
                  onClick={() => setShowMoveManager(!showMoveManager)}
                  disabled={!selectedCore}
                >
                  {showMoveManager ? "🔽 HIDE MOVES" : "🔼 MANAGE MOVES"}
                </button>

                {showMoveManager && selectedCore && (
                  <div className="move-manager">
                    <h4>AVAILABLE MOVES ({availableMoves.length})</h4>
                    {selectedSlot && (
                      <div className="slot-selector-notice">
                        Equipping to <strong>SLOT {selectedSlot}</strong>
                      </div>
                    )}
                    {availableMoves.length === 0 ? (
                      <div className="no-moves-message">
                        <p>No moves available.</p>
                        <p className="hint">
                          Purchase moves from the Scrapyard Move Shop!
                        </p>
                      </div>
                    ) : (
                      <div className="available-moves-grid">
                        {availableMoves.map((move) => {
                          const isTypeCompatible =
                            !move.core_type_identity ||
                            move.core_type_identity === selectedCore.type;
                          const isAlreadyEquipped = equippedMoves.some(
                            (em) => em.move?.id === move.id,
                          );

                          return (
                            <div
                              key={move.id}
                              className={`available-move-card ${!isTypeCompatible ? "incompatible" : ""}`}
                            >
                              <div className="available-move-header">
                                <span className="available-move-name">
                                  {move.name}
                                  {move.availability?.source ===
                                    "core_exclusive" && (
                                    <span
                                      className="move-locked-indicator"
                                      data-tooltip="Exclusive to this Core"
                                    >
                                      🔒
                                    </span>
                                  )}
                                </span>
                                <span
                                  className={`available-move-rarity rarity-${move.rarity?.toLowerCase()}`}
                                >
                                  {move.rarity}
                                </span>
                              </div>

                              {move.core_type_identity && (
                                <div
                                  className={`type-identity-indicator ${isTypeCompatible ? "compatible" : "incompatible"}`}
                                >
                                  🔒 {move.core_type_identity} Only
                                </div>
                              )}

                              <div className="available-move-types">
                                <span
                                  className={`type-badge-small type-${move.type?.toLowerCase()}`}
                                >
                                  {move.type}
                                </span>
                                <span
                                  className={`dmg-badge-small dmg-${move.dmg_type?.toLowerCase()}`}
                                >
                                  {move.dmg_type}
                                </span>
                              </div>

                              <div className="available-move-stats">
                                <span>DMG: {move.dmg}</span>
                                <span>
                                  ACC: {(move.accuracy * 100).toFixed(0)}%
                                </span>
                                <span>COST: {move.resource_cost}</span>
                              </div>
                              <button
                                className="equip-to-slot-btn"
                                onClick={() =>
                                  selectedSlot
                                    ? handleEquipMove(move.id, selectedSlot)
                                    : setSelectedSlot(1)
                                }
                                disabled={
                                  !selectedSlot ||
                                  isAlreadyEquipped ||
                                  !isTypeCompatible
                                }
                              >
                                {isAlreadyEquipped
                                  ? "✓ EQUIPPED"
                                  : !isTypeCompatible
                                    ? `🔒 ${move.core_type_identity} ONLY`
                                    : selectedSlot
                                      ? `EQUIP TO SLOT ${selectedSlot}`
                                      : "SELECT SLOT"}
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="no-core-selected">
            <p>No core in this bay</p>
            <p className="hint">Select an occupied bay or acquire new cores</p>
          </div>
        )}

        <div className="core-action-buttons">
          <button
            className="action-btn primary"
            disabled={!selectedCore}
            onClick={() => setShowMoveManager(!showMoveManager)}
          >
            🔧 EDIT LOADOUT
          </button>
          <button className="action-btn secondary" disabled={!selectedCore}>
            🔁 SWAP UNIT
          </button>
          <button className="action-btn secondary" disabled={!selectedCore}>
            🧯 REPAIR
          </button>
          <button
            className="action-btn danger"
            disabled={!selectedCore}
            onClick={() => selectedCore && handleDecommission(selectedCore)}
          >
            🗑️ DECOMMISSION
          </button>
          <button className="action-btn deploy" disabled={!selectedCore}>
            🚀 DEPLOY
          </button>
        </div>
      </div>
    </div>
  );
};

export default Garage;
