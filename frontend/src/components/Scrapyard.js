import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import {
  fetchDecommissionedCores,
  recommissionCore,
  selectDecommissionedCores,
  selectScrapyardLoading,
  selectScrapyardError,
} from "../store/slices/scrapyardSlice";
import {
  fetchGarageByOperator,
  selectGarageCapacity,
} from "../store/slices/garageSlice";
import { fetchOperator, selectOperator } from "../store/slices/operatorSlice";
import { fetchCores, selectAllCores } from "../store/slices/coresSlice";
import {
  fetchMoveShop,
  purchaseMove,
  selectAllMoves,
  selectMovesLoading,
  selectMovesError,
} from "../store/slices/movesSlice";
import { useAuth } from "../context/AuthContext";
import { useEscapeToMain } from "../hooks/useEscapeToMain";
import "./Scrapyard.css";

const Scrapyard = () => {
  useEscapeToMain();

  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { operatorId, setId } = useAuth();

  const operator = useSelector(selectOperator);
  const decommissionedCores = useSelector(selectDecommissionedCores);
  const capacity = useSelector(selectGarageCapacity);
  const loading = useSelector(selectScrapyardLoading);
  const error = useSelector(selectScrapyardError);
  const moves = useSelector(selectAllMoves);
  const movesLoading = useSelector(selectMovesLoading);
  const movesError = useSelector(selectMovesError);
  const cores = useSelector(selectAllCores);

  const [activeSection, setActiveSection] = useState("shop");
  const [selectedCore, setSelectedCore] = useState(null);
  const [selectedMove, setSelectedMove] = useState(null);
  const [rarityFilter, setRarityFilter] = useState(null);
  const [typeFilter, setTypeFilter] = useState(null);
  const [showCoreSelector, setShowCoreSelector] = useState(false);

  // Fetch operator, garage and decommissioned cores on mount
  useEffect(() => {
    if (operatorId) {
      dispatch(fetchOperator(operatorId));
      dispatch(fetchGarageByOperator(operatorId)).then((result) => {
        if (result.payload?.id) {
          dispatch(fetchCores(result.payload.id));
        }
      });
      dispatch(fetchDecommissionedCores());
    }
  }, [dispatch, operatorId]);

  useEffect(() => {
    if (!operatorId) {
      setId();
    }
  }, [operatorId, setId]);

  // Fetch moves when Move Shop tab is active
  useEffect(() => {
    if (activeSection === "shop") {
      dispatch(fetchMoveShop());
    }
  }, [activeSection, dispatch]);

  const handleRecommission = async (core) => {
    if (capacity.available <= 0) {
      alert("Garage is at full capacity! Cannot recommission core.");
      return;
    }

    const confirmRecomm = window.confirm(
      `Recommission ${
        core.name || "this Core"
      }?\n\nThis will restore it to your active Garage roster.`,
    );

    if (confirmRecomm) {
      const result = await dispatch(recommissionCore(core.id));
      if (result.meta.requestStatus === "fulfilled") {
        // Refresh garage to update capacity
        if (operatorId) {
          dispatch(fetchGarageByOperator(operatorId)).then((garageResult) => {
            if (garageResult.payload?.id) {
              dispatch(fetchCores(garageResult.payload.id));
            }
          });
        }
        // Refresh decommissioned cores list
        dispatch(fetchDecommissionedCores());
        setSelectedCore(null);
        alert(`${core.name || "Core"} has been recommissioned!`);
      }
    }
  };

  const handlePurchaseMove = async (move, coreId) => {
    const core = cores.find((c) => c.id === coreId);
    if (!core) {
      alert("Core not found!");
      return;
    }

    const price = move.price || 100;
    if (operator.bits < price) {
      alert(`Insufficient credits! Need ${price}, have ${operator.bits}`);
      return;
    }

    const confirmPurchase = window.confirm(
      `Purchase "${move.name}" for ${core.name}?\n\nCost: ${price} credits\nRemaining: ${
        operator.bits - price
      } credits`,
    );

    if (confirmPurchase) {
      const result = await dispatch(
        purchaseMove({ coreId: core.id, moveId: move.id }),
      );
      if (result.meta.requestStatus === "fulfilled") {
        // Refresh operator to update bits
        if (operatorId) {
          dispatch(fetchGarageByOperator(operatorId));
        }
        setShowCoreSelector(false);
        setSelectedMove(null);
        alert(result.payload?.message || `${core.name} learned ${move.name}!`);
      } else {
        alert(
          result.payload ||
            result.error?.message ||
            "Purchase failed. Please try again.",
        );
      }
    }
  };

  const renderDecommissionedCores = () => {
    if (loading) {
      return (
        <div className="loading-state">
          <p>LOADING SCRAPYARD DATA...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="error-state">
          <p>ERROR: {error}</p>
          <button onClick={() => dispatch(fetchDecommissionedCores())}>
            RETRY
          </button>
        </div>
      );
    }

    if (!decommissionedCores || decommissionedCores.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-icon">🗑️</div>
          <h3>Scrapyard Empty</h3>
          <p>No decommissioned Cores found.</p>
          <p className="hint">
            Decommission Cores from your Garage to move them here.
          </p>
        </div>
      );
    }

    return (
      <div className="decomm-cores-section">
        <div className="decomm-header">
          <h2>🗑️ DECOMMISSIONED CORES</h2>
          <div className="decomm-stats">
            <span className="stat-label">TOTAL SCRAPPED:</span>
            <span className="stat-value">{decommissionedCores.length}</span>
          </div>
          <div className="decomm-stats">
            <span className="stat-label">GARAGE CAPACITY:</span>
            <span
              className={`stat-value ${
                capacity.available <= 0 ? "at-limit" : ""
              }`}
            >
              {capacity.used} / {capacity.total}
            </span>
          </div>
        </div>

        <div className="cores-grid">
          {decommissionedCores.map((core) => (
            <div
              key={core.id}
              className={`core-card ${
                selectedCore?.id === core.id ? "selected" : ""
              }`}
              onClick={() =>
                setSelectedCore(selectedCore?.id === core.id ? null : core)
              }
            >
              <div className="core-card-header">
                <span className="core-name">{core.name || "Unknown Core"}</span>
                <span
                  className={`core-rarity rarity-${core.rarity?.toLowerCase()}`}
                >
                  {core.rarity || "Common"}
                </span>
              </div>

              <div className="core-card-image">
                {core.image_url ? (
                  <img
                    src={core.image_url}
                    alt={core.name}
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src =
                        "https://via.placeholder.com/150?text=No+Image";
                    }}
                  />
                ) : (
                  <div className="placeholder-icon">🔧</div>
                )}
              </div>

              <div className="core-card-details">
                <div className="detail-row">
                  <span className="label">LEVEL:</span>
                  <span className="value">{core.lvl || 1}</span>
                </div>
                <div className="detail-row">
                  <span className="label">TYPE:</span>
                  <span className="value">{core.type || "Unknown"}</span>
                </div>

                {core.battle_info && (
                  <>
                    <div className="detail-row">
                      <span className="label">HP:</span>
                      <span className="value">{core.battle_info.hp}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">PWR:</span>
                      <span className="value">
                        {core.battle_info.physical} / {core.battle_info.energy}
                      </span>
                    </div>
                  </>
                )}
              </div>

              <button
                className={`recommission-btn ${
                  capacity.available <= 0 ? "disabled" : ""
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleRecommission(core);
                }}
                disabled={capacity.available <= 0}
              >
                {capacity.available > 0 ? "♻️ RECOMMISSION" : "⚠️ GARAGE FULL"}
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderMoveShop = () => {
    if (movesLoading) {
      return (
        <div className="loading-state">
          <p>LOADING MOVE SHOP...</p>
        </div>
      );
    }

    if (movesError) {
      return (
        <div className="error-state">
          <p>ERROR: {movesError}</p>
          <button onClick={() => dispatch(fetchMoveShop())}>RETRY</button>
        </div>
      );
    }

    // Filter moves based on selected filters
    const filteredMoves = moves.filter((move) => {
      if (rarityFilter && move.rarity !== rarityFilter) return false;
      if (typeFilter && move.type !== typeFilter) return false;
      return true;
    });

    // Get unique rarities and types for filters
    const rarities = [...new Set(moves.map((m) => m.rarity))].sort();
    const types = [...new Set(moves.map((m) => m.type))].sort();

    return (
      <div className="move-shop-section">
        <div className="shop-header">
          <h2>🛒 MOVE SHOP</h2>
          <p className="shop-subtitle">
            Purchase and unlock new moves for your Cores
          </p>
        </div>

        <div className="shop-filters">
          <div className="filter-group">
            <label>Rarity:</label>
            <select
              value={rarityFilter || ""}
              onChange={(e) => setRarityFilter(e.target.value || null)}
            >
              <option value="">All Rarities</option>
              {rarities.map((rarity) => (
                <option key={rarity} value={rarity}>
                  {rarity}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Type:</label>
            <select
              value={typeFilter || ""}
              onChange={(e) => setTypeFilter(e.target.value || null)}
            >
              <option value="">All Types</option>
              {types.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-stats">
            <span>
              Showing {filteredMoves.length} of {moves.length} moves
            </span>
          </div>
        </div>

        {filteredMoves.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No Moves Found</h3>
            <p>Try adjusting your filters.</p>
          </div>
        ) : (
          <div className="moves-grid">
            {filteredMoves.map((move) => (
              <div
                key={move.id}
                className={`move-card ${
                  selectedMove?.id === move.id ? "selected" : ""
                }`}
                onClick={() =>
                  setSelectedMove(selectedMove?.id === move.id ? null : move)
                }
              >
                <div className="move-card-header">
                  <span className="move-name">{move.name}</span>
                  <span
                    className={`move-rarity rarity-${move.rarity?.toLowerCase()}`}
                  >
                    {move.rarity}
                  </span>
                </div>

                {move.core_type_identity && (
                  <div className="type-identity-badge">
                    🔒 {move.core_type_identity} Only
                  </div>
                )}

                <div className="move-card-type">
                  <span
                    className={`type-badge type-${move.type?.toLowerCase()}`}
                  >
                    {move.type}
                  </span>
                  <span
                    className={`dmg-badge dmg-${move.dmg_type?.toLowerCase()}`}
                  >
                    {move.dmg_type}
                  </span>
                </div>

                <div className="move-description">
                  <p>{move.description}</p>
                </div>

                <div className="move-stats">
                  <div className="stat-row">
                    <span className="label">DAMAGE:</span>
                    <span className="value">{move.dmg || 0}</span>
                  </div>
                  <div className="stat-row">
                    <span className="label">ACCURACY:</span>
                    <span className="value">
                      {((move.accuracy || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="stat-row">
                    <span className="label">COST:</span>
                    <span className="value">{move.resource_cost || 0}</span>
                  </div>
                </div>

                <div className="move-price">
                  <span className="price-label">PRICE:</span>
                  <span className="price-value">
                    {move.price || 100} credits
                  </span>
                </div>

                <button
                  className="purchase-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedMove(move);
                    setShowCoreSelector(true);
                  }}
                  disabled={operator?.bits < (move.price || 100)}
                >
                  {operator?.bits < (move.price || 100)
                    ? "⚠️ INSUFFICIENT CREDITS"
                    : "💳 PURCHASE"}
                </button>
              </div>
            ))}
          </div>
        )}

        {showCoreSelector && selectedMove && (
          <div
            className="modal-overlay"
            onClick={() => setShowCoreSelector(false)}
          >
            <div
              className="core-selector-modal"
              onClick={(e) => e.stopPropagation()}
            >
              <h3>Select Core to Learn {selectedMove.name}</h3>
              {selectedMove.core_type_identity && (
                <p className="type-restriction-notice">
                  🔒 Only {selectedMove.core_type_identity} Cores can learn this
                  move
                </p>
              )}
              <div className="cores-list">
                {cores.filter(
                  (c) =>
                    !c.decommed &&
                    (!selectedMove.core_type_identity ||
                      c.type === selectedMove.core_type_identity),
                ).length === 0 ? (
                  <div className="empty-state">
                    <p>
                      {selectedMove.core_type_identity
                        ? `No ${selectedMove.core_type_identity} Cores found in Garage.`
                        : "No active Cores found in Garage."}
                    </p>
                  </div>
                ) : (
                  cores
                    .filter(
                      (c) =>
                        !c.decommed &&
                        (!selectedMove.core_type_identity ||
                          c.type === selectedMove.core_type_identity),
                    )
                    .map((core) => (
                      <div
                        key={core.id}
                        className="core-option"
                        onClick={() =>
                          handlePurchaseMove(selectedMove, core.id)
                        }
                      >
                        <span className="core-name">{core.name}</span>
                        <span
                          className={`core-rarity rarity-${core.rarity?.toLowerCase()}`}
                        >
                          {core.rarity}
                        </span>
                        <span
                          className={`core-type type-${core.type?.toLowerCase()}`}
                        >
                          {core.type}
                        </span>
                      </div>
                    ))
                )}
              </div>
              <button
                className="cancel-btn"
                onClick={() => setShowCoreSelector(false)}
              >
                CANCEL
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderContent = () => {
    switch (activeSection) {
      case "decomm":
        return renderDecommissionedCores();
      case "shop":
        return renderMoveShop();
      default:
        return renderDecommissionedCores();
    }
  };

  return (
    <div className="scrapyard-container">
      <div className="scrapyard-header">
        <h1 className="scrapyard-title">♻️ SCRAPYARD</h1>
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
      </div>

      <div className="section-tabs">
        <button
          className={`tab-btn ${activeSection === "shop" ? "active" : ""}`}
          onClick={() => setActiveSection("shop")}
        >
          🛒 MOVE SHOP
        </button>
        <button
          className={`tab-btn ${activeSection === "decomm" ? "active" : ""}`}
          onClick={() => setActiveSection("decomm")}
        >
          🗑️ DECOMMISSIONED CORES
        </button>
      </div>

      <div className="section-content">{renderContent()}</div>
    </div>
  );
};

export default Scrapyard;
