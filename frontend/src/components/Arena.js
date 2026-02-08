import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import {
  fetchArenaNPCs,
  fetchNPCDetail,
  fetchArenaProgress,
  challengeNPC,
  selectArenaNPCs,
  selectSelectedNPC,
  selectArenaProgress,
  selectCurrentRank,
  selectChallengeResult,
  selectArenaLoading,
  selectArenaDetailLoading,
  selectChallengeLoading,
  clearSelectedNPC,
  clearChallengeResult,
  setCurrentRank,
} from "../store/slices/arenaSlice";
import { startBattle, selectBattleLoading } from "../store/slices/battleSlice";
import { fetchOperator, selectOperator } from "../store/slices/operatorSlice";
import { useAuth } from "../context/AuthContext";
import { useEscapeToMain } from "../hooks/useEscapeToMain";
import "./Arena.css";

const RANKS = ["E", "D", "C", "B", "A", "S"];
const RANK_ORDER = { E: 0, D: 1, C: 2, B: 3, A: 4, S: 5 };

const Arena = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { operatorId, setId } = useAuth();
  useEscapeToMain();

  const operator = useSelector(selectOperator);
  const npcs = useSelector(selectArenaNPCs);
  const selectedNPC = useSelector(selectSelectedNPC);
  const progress = useSelector(selectArenaProgress);
  const currentRank = useSelector(selectCurrentRank);
  const challengeResult = useSelector(selectChallengeResult);
  const loading = useSelector(selectArenaLoading);
  const detailLoading = useSelector(selectArenaDetailLoading);
  const challengeLoading = useSelector(selectChallengeLoading);
  const battleLoading = useSelector(selectBattleLoading);

  const [showDetailModal, setShowDetailModal] = useState(false);

  // Initialize operator ID from localStorage if needed
  useEffect(() => {
    if (!operatorId) {
      setId();
    }
  }, [operatorId, setId]);

  // Fetch operator and progress on mount
  useEffect(() => {
    if (operatorId) {
      dispatch(fetchOperator(operatorId));
      dispatch(fetchArenaProgress(operatorId));
    }
  }, [dispatch, operatorId]);

  // Fetch NPCs when rank changes or on initial load
  useEffect(() => {
    if (operatorId && currentRank) {
      dispatch(fetchArenaNPCs({ rank: currentRank, operatorId }));
    }
  }, [dispatch, operatorId, currentRank]);

  const isRankUnlocked = (rank) => {
    if (!progress) return rank === "E";
    return RANK_ORDER[rank] <= RANK_ORDER[progress.current_rank];
  };

  const handleRankClick = (rank) => {
    if (isRankUnlocked(rank)) {
      dispatch(setCurrentRank(rank));
    }
  };

  const handleNPCClick = (npc) => {
    if (npc.is_locked) return;
    dispatch(fetchNPCDetail({ npcId: npc.id, operatorId }));
    setShowDetailModal(true);
  };

  const handleCloseModal = () => {
    setShowDetailModal(false);
    dispatch(clearSelectedNPC());
    dispatch(clearChallengeResult());
  };

  const handleChallenge = (outcome) => {
    if (!selectedNPC || !operatorId) return;
    dispatch(
      challengeNPC({
        npcId: selectedNPC.id,
        operatorId,
        outcome,
      }),
    ).then(() => {
      // Refresh NPCs after challenge to update defeated status
      dispatch(fetchArenaNPCs({ rank: currentRank, operatorId }));
    });
  };

  const handleStartBattle = () => {
    if (!selectedNPC || !operatorId) return;
    dispatch(startBattle({ npcId: selectedNPC.id, operatorId }))
      .unwrap()
      .then((response) => {
        navigate(`/battle/${response.battle_id}`);
      })
      .catch((error) => {
        console.error('Failed to start battle:', error);
      });
  };

  const renderDifficultyStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span key={i} className={`star ${i <= rating ? "filled" : "empty"}`}>
          {i <= rating ? "\u2605" : "\u2606"}
        </span>,
      );
    }
    return <div className="difficulty-stars">{stars}</div>;
  };

  const renderCorePreview = (cores) => {
    if (!cores || cores.length === 0) return null;
    return (
      <div className="ops-core-preview">
        {cores.map((core, index) => (
          <div key={core.id} className="core-preview-item">
            <span className="core-preview-name">{core.name}</span>
            <span
              className={`core-preview-rarity rarity-${core.rarity.toLowerCase()}`}
            >
              Lv.{core.lvl}
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="arena-container">
      {/* Header */}
      <div className="arena-header">
        <h1 className="arena-title">ARENA</h1>
        <button onClick={() => navigate("/menu")} className="back-btn">
          BACK TO MENU
        </button>
      </div>

      {/* Stats Bar */}
      <div className="stats-bar">
        <div className="stat-item">
          <span className="stat-label">OPERATOR</span>
          <span className="stat-value">
            {operator?.call_sign || "LOADING..."}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">RANK</span>
          <span className="stat-value rank-value">
            {progress?.current_rank || "E"}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">WINS</span>
          <span className="stat-value wins">{progress?.arena_wins || 0}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">LOSSES</span>
          <span className="stat-value losses">
            {progress?.arena_losses || 0}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">STREAK</span>
          <span className="stat-value streak">
            {progress?.current_win_streak || 0}
          </span>
        </div>
      </div>

      {/* Rank Tabs */}
      <div className="rank-tabs">
        {RANKS.map((rank) => {
          const unlocked = isRankUnlocked(rank);
          return (
            <button
              key={rank}
              className={`rank-tab ${currentRank === rank ? "active" : ""} ${!unlocked ? "locked" : ""}`}
              onClick={() => handleRankClick(rank)}
              disabled={!unlocked}
            >
              {rank} RANK {!unlocked && "\uD83D\uDD12"}
            </button>
          );
        })}
      </div>

      {/* NPC Grid */}
      <div className="npc-grid-container">
        {loading ? (
          <div className="loading-message">LOADING OPPONENTS...</div>
        ) : npcs.length === 0 ? (
          <div className="empty-message">
            NO OPPONENTS AVAILABLE IN THIS RANK
          </div>
        ) : (
          <div className="npc-grid">
            {npcs.map((npc) => (
              <div
                key={npc.id}
                className={`npc-card ${npc.is_defeated ? "defeated" : ""} ${npc.is_locked ? "locked" : ""} ${npc.is_gate_boss ? "gate-boss" : ""}`}
                onClick={() => handleNPCClick(npc)}
              >
                <div className="npc-floor">#{npc.floor}</div>
                <div className="npc-portrait">
                  {npc.portrait_url ? (
                    <img src={npc.portrait_url} alt={npc.call_sign} />
                  ) : (
                    <div className="portrait-placeholder">
                      {npc.call_sign.charAt(0)}
                    </div>
                  )}
                  {npc.is_gate_boss && (
                    <div className="gate-boss-badge">BOSS</div>
                  )}
                  {npc.is_defeated && (
                    <div className="defeated-overlay">DEFEATED</div>
                  )}
                </div>
                <div className="npc-info">
                  <div className="npc-callsign">{npc.call_sign}</div>
                  <div className="npc-title">{npc.title}</div>
                  {renderDifficultyStars(npc.difficulty_rating)}
                  {renderCorePreview(npc.cores)}
                  <div className="npc-reward">
                    <span className="reward-bits">{npc.reward_bits} BITS</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={handleCloseModal}>
              &times;
            </button>

            {detailLoading ? (
              <div className="modal-loading">LOADING...</div>
            ) : selectedNPC ? (
              <>
                <div className="modal-header">
                  <div className="modal-portrait">
                    {selectedNPC.portrait_url ? (
                      <img
                        src={selectedNPC.portrait_url}
                        alt={selectedNPC.call_sign}
                      />
                    ) : (
                      <div className="portrait-placeholder large">
                        {selectedNPC.call_sign.charAt(0)}
                      </div>
                    )}
                  </div>
                  <div className="modal-title-section">
                    <h2 className="modal-callsign">{selectedNPC.call_sign}</h2>
                    <div className="modal-title">{selectedNPC.title}</div>
                    <div className="modal-rank">
                      {selectedNPC.arena_rank}-RANK #{selectedNPC.floor}
                    </div>
                    {renderDifficultyStars(selectedNPC.difficulty_rating)}
                    {selectedNPC.is_gate_boss && (
                      <div className="gate-boss-info">
                        GATE BOSS - Unlocks {selectedNPC.unlocks_rank}-RANK
                      </div>
                    )}
                  </div>
                </div>

                <div className="modal-bio">
                  <p>{selectedNPC.bio}</p>
                </div>

                <div className="modal-cores">
                  <h3>CORE ROSTER</h3>
                  <div className="cores-list">
                    {selectedNPC.cores?.map((core) => (
                      <div key={core.id} className="core-detail-card">
                        <div className="core-header">
                          <span className="core-name">{core.name}</span>
                          <span
                            className={`core-rarity rarity-${core.rarity.toLowerCase()}`}
                          >
                            {core.rarity} Lv.{core.lvl}
                          </span>
                        </div>
                        <div className="core-type">{core.core_type}</div>
                        <div className="core-stats">
                          <span>HP: {core.hp}</span>
                          <span>PHY: {core.physical}</span>
                          <span>ENG: {core.energy}</span>
                          <span>DEF: {core.defense}</span>
                          <span>SHD: {core.shield}</span>
                          <span>SPD: {core.speed}</span>
                        </div>
                        {core.equipped_moves &&
                          core.equipped_moves.length > 0 && (
                            <div className="core-moves">
                              {core.equipped_moves.map((em) => (
                                <div key={em.id} className="equipped-move">
                                  <span className="move-name">
                                    {em.move.name}
                                  </span>
                                  <span
                                    className={`move-type ${em.move.dmg_type.toLowerCase()}`}
                                  >
                                    {em.move.dmg_type}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="modal-rewards">
                  <h3>REWARDS</h3>
                  <div className="rewards-info">
                    <span className="reward-item">
                      {selectedNPC.reward_bits} BITS
                    </span>
                    <span className="reward-item">
                      {selectedNPC.reward_exp} EXP
                    </span>
                  </div>
                </div>

                {/* Challenge Result */}
                {challengeResult && (
                  <div
                    className={`challenge-result ${challengeResult.outcome}`}
                  >
                    <p>{challengeResult.message}</p>
                  </div>
                )}

                {/* Challenge Buttons */}
                <div className="modal-actions">
                  {selectedNPC.is_defeated ? (
                    <div className="already-defeated">OPPONENT DEFEATED</div>
                  ) : (
                    <>
                      <button
                        className="challenge-btn battle"
                        onClick={handleStartBattle}
                        disabled={battleLoading || challengeLoading}
                      >
                        {battleLoading ? "STARTING..." : "BATTLE"}
                      </button>
                      <div className="simulate-buttons">
                        <button
                          className="challenge-btn simulate-win"
                          onClick={() => handleChallenge("win")}
                          disabled={challengeLoading || battleLoading}
                        >
                          {challengeLoading ? "..." : "SIM WIN"}
                        </button>
                        <button
                          className="challenge-btn simulate-lose"
                          onClick={() => handleChallenge("lose")}
                          disabled={challengeLoading || battleLoading}
                        >
                          {challengeLoading ? "..." : "SIM LOSE"}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </>
            ) : (
              <div className="modal-error">Error loading opponent data</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Arena;
