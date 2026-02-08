import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { useEscapeToMain } from "../hooks/useEscapeToMain";
import { useAuth } from "../context/AuthContext";
import {
  RARITY_PRICES,
  CORE_TRACKS,
  RARITIES,
} from "../constants/coreGeneration";
import { generateCore, updateCore, fetchCores } from "../store/slices/coresSlice";
import { fetchOperator, selectOperator } from "../store/slices/operatorSlice";
import { fetchGarageByOperator, selectGarage } from "../store/slices/garageSlice";
import { selectAllCores, selectCoresLoading } from "../store/slices/coresSlice";
import "./CyberCodex.css";

const CyberCodex = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { operatorId, setId } = useAuth();
  useEscapeToMain();

  // Redux state
  const operator = useSelector(selectOperator);
  const garage = useSelector(selectGarage);
  const cores = useSelector(selectAllCores);
  const loading = useSelector(selectCoresLoading);

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    track: "",
    rarity: "Common",
  });

  // UI state
  const [generatedCore, setGeneratedCore] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showImageInput, setShowImageInput] = useState(false);
  const [imageLink, setImageLink] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // Fetch operator, garage, and cores on mount
  useEffect(() => {
    if (operatorId) {
      // Fetch operator data
      dispatch(fetchOperator(operatorId));

      // Fetch garage and then cores
      dispatch(fetchGarageByOperator(operatorId)).then((result) => {
        if (result.payload?.id) {
          dispatch(fetchCores(result.payload.id));
        }
      });
    }
  }, [dispatch, operatorId]);

  // Ensure operatorId is set, redirect to login if not found
  useEffect(() => {
    if (!operatorId) {
      setId();
      // If still no operatorId after trying to load from storage, redirect to login
      const storedId = localStorage.getItem("codex_operator_id");
      if (!storedId) {
        navigate("/");
      }
    }
  }, [operatorId, setId, navigate]);

  // Calculate current price based on rarity
  const currentPrice = RARITY_PRICES[formData.rarity];

  // Validation checks
  const canAfford = operator?.bits >= currentPrice;
  const hasCapacity = cores.length < (garage?.bay_doors || 3);
  const isFormValid = formData.name.trim() && formData.track && formData.rarity;
  const canSubmit = isFormValid && canAfford && hasCapacity && !loading;

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setErrorMessage(""); // Clear error on input change
  };

  // Handle form submission (generate core)
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate
    if (!canAfford) {
      setErrorMessage(
        `Insufficient credits! Need ${currentPrice}c, have ${operator.bits}c`
      );
      return;
    }

    if (!hasCapacity) {
      setErrorMessage(
        `Garage at capacity! ${cores.length}/${garage.bay_doors} bays full`
      );
      return;
    }

    try {
      // Generate core via API
      const result = await dispatch(
        generateCore({
          name: formData.name,
          rarity: formData.rarity,
          track: formData.track,
          garage_id: garage.id,
        })
      ).unwrap();

      // Store generated core temporarily
      setGeneratedCore(result);

      // Show image input step
      setShowImageInput(true);

      // Refresh operator to get updated bits
      await dispatch(fetchOperator(operator.id));
    } catch (error) {
      setErrorMessage(error || "Core generation failed. Please try again.");
    }
  };

  // Handle finalizing core with image
  const handleFinalizeCore = async () => {
    if (!imageLink.trim()) {
      setErrorMessage("Please provide an image link for your core!");
      return;
    }

    try {
      // Update core with image URL
      await dispatch(
        updateCore({
          coreId: generatedCore.id,
          updates: { image_url: imageLink },
        })
      ).unwrap();

      // Update local generated core state
      setGeneratedCore((prev) => ({
        ...prev,
        image_url: imageLink,
      }));

      // Show final preview
      setShowImageInput(false);
      setShowPreview(true);
    } catch (error) {
      setErrorMessage(error || "Failed to save image. Please try again.");
    }
  };

  // Handle "Generate Another" button
  const handleGenerateAnother = () => {
    setFormData({
      name: "",
      track: "",
      rarity: "Common",
    });
    setGeneratedCore(null);
    setShowPreview(false);
    setShowImageInput(false);
    setImageLink("");
    setErrorMessage("");
  };

  // Handle "View in Garage" button
  const handleViewInGarage = () => {
    navigate("/garage");
  };

  // Calculate how many cores user can afford
  const coresAffordable = operator ? Math.floor(operator.bits / currentPrice) : 0;

  // Show loading if required data isn't available
  if (!operator || !garage) {
    return (
      <div className="cybercodex-container">
        <div className="cybercodex-header">
          <h1 className="cybercodex-title">🛠️ CYBER CODEX</h1>
          <button onClick={() => navigate("/menu")} className="back-btn">
            BACK TO MENU
          </button>
        </div>
        <div className="cybercodex-content">
          <div className="generation-form-section">
            <div style={{ textAlign: "center", color: "#ff6432", padding: "20px" }}>
              <div style={{ fontSize: "2rem", marginBottom: "10px" }}>⚙️</div>
              <div>Loading operator data...</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cybercodex-container">
      <div className="cybercodex-header">
        <h1 className="cybercodex-title">🛠️ CYBER CODEX</h1>
        <button onClick={() => navigate("/menu")} className="back-btn">
          BACK TO MENU
        </button>
      </div>

      <div className="cybercodex-content">
        {/* Status Bar */}
        <div className="status-bar">
          <div className="status-item">
            <span className="status-label">OPERATOR:</span>
            <span className="status-value">{operator.call_sign}</span>
          </div>
          <div className="status-item">
            <span className="status-label">CREDITS:</span>
            <span className={`status-value ${!canAfford ? "insufficient" : ""}`}>
              {operator.bits}c
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">CAPACITY:</span>
            <span className={`status-value ${!hasCapacity ? "at-capacity" : ""}`}>
              {cores.length} / {garage.bay_doors}
            </span>
          </div>
        </div>

        {!showPreview && !showImageInput ? (
          /* Generation Form */
          <div className="generation-form-section">
            <h2 className="section-title">CORE GENERATION</h2>
            <form onSubmit={handleSubmit} className="generation-form">
              {/* Core Name Input */}
              <div className="form-group">
                <label htmlFor="name">CORE NAME</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Enter core name..."
                  maxLength={120}
                  disabled={loading}
                  required
                />
              </div>

              {/* Rarity Dropdown */}
              <div className="form-group">
                <label htmlFor="rarity">RARITY</label>
                <select
                  id="rarity"
                  name="rarity"
                  value={formData.rarity}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                >
                  {RARITIES.map((rarity) => (
                    <option key={rarity} value={rarity}>
                      {rarity} - {RARITY_PRICES[rarity]}c
                    </option>
                  ))}
                </select>
              </div>

              {/* Core Tracks Dropdown */}
              <div className="form-group">
                <label htmlFor="track">GROWTH TRACK</label>
                <select
                  id="track"
                  name="track"
                  value={formData.track}
                  onChange={handleInputChange}
                  disabled={loading}
                  required
                >
                  <option value="">-- Select Track --</option>
                  {CORE_TRACKS.map((track) => (
                    <option key={track} value={track}>
                      {track}
                    </option>
                  ))}
                </select>
                <p className="type-help-text">
                  📈 Growth track determines leveling pattern & stat progression
                </p>
              </div>

              {/* Random Type Info */}
              <div className="random-type-info">
                <div className="random-icon">🎲</div>
                <div className="random-text">
                  <span className="random-label">MOVE TYPE:</span>
                  <span className="random-value">Randomly Assigned</span>
                </div>
              </div>

              {/* Price Display */}
              <div className="price-display">
                <div className="price-label">GENERATION COST:</div>
                <div className={`price-value ${!canAfford ? "insufficient" : ""}`}>
                  {currentPrice}c
                </div>
              </div>

              {/* Affordability Helper */}
              {canAfford && (
                <div className="affordability-text">
                  You can afford {coresAffordable} {formData.rarity} core
                  {coresAffordable !== 1 ? "s" : ""}
                </div>
              )}

              {/* Error Messages */}
              {errorMessage && (
                <div className="error-message">{errorMessage}</div>
              )}
              {!canAfford && !errorMessage && (
                <div className="error-message">
                  Insufficient credits! Need {currentPrice}c, have{" "}
                  {operator.bits}c
                </div>
              )}
              {!hasCapacity && !errorMessage && (
                <div className="error-message">
                  Garage at capacity! Decommission cores in Scrapyard to make room.
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                className="generate-btn"
                disabled={!canSubmit}
              >
                {loading ? "GENERATING..." : "🚀 GENERATE CORE"}
              </button>
            </form>
          </div>
        ) : showImageInput ? (
          /* Image Input Section */
          <div className="image-input-section">
            <h2 className="section-title">📸 ADD CORE IMAGE</h2>

            <div className="image-input-panel">
              {/* Show generated stats preview */}
              <div className="stats-preview-compact">
                <h3>Generated Stats</h3>
                <div className="compact-stats-header">
                  <div className="compact-stat">
                    <span className="compact-label">Name:</span>
                    <span className="compact-value">{generatedCore?.name}</span>
                  </div>
                  <div className="compact-stat">
                    <span className="compact-label">Rarity:</span>
                    <span className={`compact-value rarity-${generatedCore?.rarity.toLowerCase()}`}>
                      {generatedCore?.rarity}
                    </span>
                  </div>
                </div>

                {/* Core Type - Move Compatibility */}
                <div className="type-identity-display">
                  <div className="type-icon">⚡</div>
                  <div className="type-info">
                    <span className="type-label">MOVE TYPE IDENTITY:</span>
                    <span className={`type-value type-${generatedCore?.type.toLowerCase()}`}>
                      {generatedCore?.type}
                    </span>
                    <span className="type-description">
                      Determines move compatibility & combat interactions
                    </span>
                  </div>
                </div>

                {/* Tracks - Growth Pattern */}
                <div className="tracks-display">
                  <div className="tracks-icon">📈</div>
                  <div className="tracks-info">
                    <span className="tracks-label">GROWTH TRACKS:</span>
                    <span className="tracks-value">
                      {generatedCore?.upgrade_info?.tracks?.length > 0
                        ? generatedCore.upgrade_info.tracks.map(t => t.name || t).join(", ")
                        : "Standard Growth"}
                    </span>
                    <span className="tracks-description">
                      Defines leveling pattern & stat progression
                    </span>
                  </div>
                </div>

                <div className="stats-row">
                  <span>HP: {generatedCore?.battle_info.hp}</span>
                  <span>PHY: {generatedCore?.battle_info.physical}</span>
                  <span>NRG: {generatedCore?.battle_info.energy}</span>
                  <span>DEF: {generatedCore?.battle_info.defense}</span>
                  <span>SHD: {generatedCore?.battle_info.shield}</span>
                  <span>SPD: {generatedCore?.battle_info.speed}</span>
                </div>
              </div>

              {/* Image Link Input */}
              <div className="image-input-form">
                <label htmlFor="imageLink">IMAGE URL</label>
                <input
                  type="url"
                  id="imageLink"
                  value={imageLink}
                  onChange={(e) => setImageLink(e.target.value)}
                  placeholder="https://example.com/core-image.png"
                  className="image-input"
                />
                <p className="image-help-text">
                  Provide a direct link to an image for your core (PNG, JPG, GIF)
                </p>

                {/* Image Preview */}
                {imageLink && (
                  <div className="image-preview-container">
                    <p className="preview-label">Preview:</p>
                    <img
                      src={imageLink}
                      alt="Core preview"
                      className="image-preview"
                      onError={(e) => {
                        e.target.style.display = "none";
                        e.target.nextSibling.style.display = "block";
                      }}
                    />
                    <p className="image-error" style={{ display: "none" }}>
                      Failed to load image. Check the URL.
                    </p>
                  </div>
                )}
              </div>

              {/* Error Message */}
              {errorMessage && (
                <div className="error-message">{errorMessage}</div>
              )}

              {/* Action Buttons */}
              <div className="image-actions">
                <button
                  onClick={handleGenerateAnother}
                  className="secondary-btn"
                >
                  ❌ CANCEL
                </button>
                <button
                  onClick={handleFinalizeCore}
                  className="primary-btn"
                  disabled={!imageLink.trim()}
                >
                  ✅ FINALIZE CORE
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Preview Panel */
          <div className="preview-section">
            <h2 className="section-title">✅ CORE SUCCESSFULLY GENERATED!</h2>

            <div className="preview-panel">
              <div className="core-preview">
                <div className="preview-header">
                  {generatedCore.image_url ? (
                    <img
                      src={generatedCore.image_url}
                      alt={generatedCore.name}
                      className="core-image-large"
                    />
                  ) : (
                    <div className="core-icon-large">🔧</div>
                  )}
                  <div className="core-name-large">{generatedCore.name}</div>
                  <div className={`core-rarity rarity-${generatedCore.rarity.toLowerCase()}`}>
                    {generatedCore.rarity}
                  </div>
                </div>

                {/* Core Type - Move Compatibility */}
                <div className="type-identity-banner">
                  <div className="type-banner-icon">⚡</div>
                  <div className="type-banner-content">
                    <span className="type-banner-label">MOVE TYPE IDENTITY:</span>
                    <span className={`type-banner-value type-${generatedCore.type.toLowerCase()}`}>
                      {generatedCore.type}
                    </span>
                    <span className="type-banner-hint">Move compatibility & combat interactions</span>
                  </div>
                  <div className="type-banner-icon">⚡</div>
                </div>

                {/* Growth Tracks */}
                <div className="tracks-banner">
                  <div className="tracks-banner-icon">📈</div>
                  <div className="tracks-banner-content">
                    <span className="tracks-banner-label">GROWTH TRACKS:</span>
                    <span className="tracks-banner-value">
                      {generatedCore.upgrade_info?.tracks?.length > 0
                        ? generatedCore.upgrade_info.tracks.map(t => t.name || t).join(", ")
                        : "Standard Growth"}
                    </span>
                    <span className="tracks-banner-hint">Leveling pattern & stat progression</span>
                  </div>
                  <div className="tracks-banner-icon">📈</div>
                </div>

                <div className="core-details-grid">
                  <div className="detail-item">
                    <span className="detail-label">LEVEL:</span>
                    <span className="detail-value">{generatedCore.lvl}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">PRICE PAID:</span>
                    <span className="detail-value">{generatedCore.price}c</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">MOVE SLOTS:</span>
                    <span className="detail-value">{generatedCore.battle_info.equip_slots}</span>
                  </div>
                </div>

                {/* Battle Stats */}
                <div className="battle-stats-preview">
                  <h3>COMBAT STATS</h3>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-label">HP:</span>
                      <span className="stat-value">
                        {generatedCore.battle_info.hp}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">PHYSICAL:</span>
                      <span className="stat-value">
                        {generatedCore.battle_info.physical}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">ENERGY:</span>
                      <span className="stat-value">
                        {generatedCore.battle_info.energy}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">DEFENSE:</span>
                      <span className="stat-value">
                        {generatedCore.battle_info.defense}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">SHIELD:</span>
                      <span className="stat-value">
                        {generatedCore.battle_info.shield}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">SPEED:</span>
                      <span className="stat-value">
                        {generatedCore.battle_info.speed}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="preview-actions">
                <button onClick={handleGenerateAnother} className="secondary-btn">
                  🔄 GENERATE ANOTHER
                </button>
                <button onClick={handleViewInGarage} className="primary-btn">
                  🚀 VIEW IN GARAGE
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CyberCodex;
