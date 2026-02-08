// frontend/src/components/Battle.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';

import battleWebSocket from '../services/battleWebSocket';
import {
  setConnected,
  setBattleState,
  setTurnStart,
  setDiceAllocated,
  setSelectedMove,
  setActionResult,
  setActionRejected,
  setForcedSwitch,
  setBattleEnd,
  setError,
  resetBattle,
  selectBattleStatus,
  selectBattlePhase,
  selectPlayerTeam,
  selectEnemyTeam,
  selectCurrentTurn,
  selectPendingDiceRolls,
  selectTurnLog,
  selectBattleResult,
  selectBattleRewards,
  selectSelectedMove,
  selectConnected,
  selectActivePlayerCore,
  selectActiveEnemyCore,
  selectNpcName,
  selectLastPlayerAction,
  selectLastEnemyAction,
} from '../store/slices/battleSlice';

import CoreDisplay from './battle/CoreDisplay';
import MoveSelector from './battle/MoveSelector';
import FighterHUD from './battle/FighterHUD';
import DiceAllocationPanel from './battle/DiceAllocationPanel';
import TurnLog from './battle/TurnLog';
import BattleResultModal from './battle/BattleResultModal';

import './Battle.css';

const Battle = () => {
  const { battleId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const status = useSelector(selectBattleStatus);
  const phase = useSelector(selectBattlePhase);
  const playerTeam = useSelector(selectPlayerTeam);
  const enemyTeam = useSelector(selectEnemyTeam);
  const currentTurn = useSelector(selectCurrentTurn);
  const pendingDiceRolls = useSelector(selectPendingDiceRolls);
  const turnLog = useSelector(selectTurnLog);
  const result = useSelector(selectBattleResult);
  const rewards = useSelector(selectBattleRewards);
  const selectedMove = useSelector(selectSelectedMove);
  const connected = useSelector(selectConnected);
  const activePlayerCore = useSelector(selectActivePlayerCore);
  const activeEnemyCore = useSelector(selectActiveEnemyCore);
  const npcName = useSelector(selectNpcName);
  const lastPlayerAction = useSelector(selectLastPlayerAction);
  const lastEnemyAction = useSelector(selectLastEnemyAction);

  const [showSwitchModal, setShowSwitchModal] = useState(false);
  const [playerAnimation, setPlayerAnimation] = useState(null);
  const [enemyAnimation, setEnemyAnimation] = useState(null);

  // Trigger animations based on action results
  useEffect(() => {
    if (lastPlayerAction && lastPlayerAction.action_type === 'move' && lastPlayerAction.success) {
      // Player attacked enemy
      if (lastPlayerAction.accuracy_check) {
        // Hit - shake the enemy
        setEnemyAnimation(lastPlayerAction.was_critical ? 'crit' : 'hit');
      } else {
        // Miss - enemy dodges
        setEnemyAnimation(Math.random() > 0.5 ? 'miss-left' : 'miss-right');
      }
      // Clear animation after it plays
      setTimeout(() => setEnemyAnimation(null), 500);
    }
  }, [lastPlayerAction]);

  useEffect(() => {
    if (lastEnemyAction && lastEnemyAction.action_type === 'move' && lastEnemyAction.success) {
      // Enemy attacked player
      if (lastEnemyAction.accuracy_check) {
        // Hit - shake the player
        setPlayerAnimation(lastEnemyAction.was_critical ? 'crit' : 'hit');
      } else {
        // Miss - player dodges
        setPlayerAnimation(Math.random() > 0.5 ? 'miss-left' : 'miss-right');
      }
      // Clear animation after it plays
      setTimeout(() => setPlayerAnimation(null), 500);
    }
  }, [lastEnemyAction]);

  // Connect to WebSocket on mount
  useEffect(() => {
    if (battleId) {
      const actions = {
        setConnected,
        setBattleState,
        setTurnStart,
        setDiceAllocated,
        setActionResult,
        setActionRejected,
        setForcedSwitch,
        setBattleEnd,
        setError,
      };

      battleWebSocket.connect(battleId, dispatch, actions);
    }

    return () => {
      battleWebSocket.disconnect();
      dispatch(resetBattle());
    };
  }, [battleId, dispatch]);

  // Handle move selection and execution
  const handleMoveSelect = (move) => {
    dispatch(setSelectedMove(move));
    battleWebSocket.sendAction('move', { move_id: move.id });
  };

  // Handle switch
  const handleSwitch = () => {
    setShowSwitchModal(true);
  };

  const handleSwitchConfirm = (coreIndex) => {
    battleWebSocket.sendAction('switch', { new_core_index: coreIndex });
    setShowSwitchModal(false);
  };

  // Handle pass
  const handlePass = () => {
    battleWebSocket.sendAction('pass', {});
  };

  // Handle dice allocation
  const handleDiceAllocate = (allocations) => {
    battleWebSocket.sendDiceAllocation(allocations);
  };

  // Handle result modal close
  const handleResultClose = () => {
    dispatch(resetBattle());
  };

  // Render loading state
  if (!connected && status !== 'ended') {
    return (
      <div className="battle-container loading">
        <div className="loading-message">
          <h2>CONNECTING TO BATTLE...</h2>
          <div className="loading-spinner" />
        </div>
      </div>
    );
  }

  return (
    <div className="battle-container">
      {/* Main Layout: Battle Area + Sidebar */}
      <div className="battle-layout">
        {/* Left: Main Battle Area */}
        <div className="battle-main">
          {/* Battle Header */}
          <div className="battle-header">
            <div className="header-left">
              <div className="turn-indicator">TURN {currentTurn}</div>
              <div className="phase-indicator">{phase.toUpperCase().replace('_', ' ')}</div>
            </div>
            <div className="header-center">
              {/* Team Status Bar */}
              <div className="team-status-bar">
                <div className="team-cores player-team-cores">
                  {playerTeam?.cores?.map((core, idx) => (
                    <div
                      key={core.id}
                      className={`core-indicator ${core.is_knocked_out ? 'ko' : ''} ${idx === playerTeam.active_core_index ? 'active' : ''}`}
                    >
                      <span className="core-mini-name">{core.name.substring(0, 3)}</span>
                      <div className="core-mini-hp">
                        <div
                          className="core-mini-hp-fill"
                          style={{ width: `${(core.current_hp / core.max_hp) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <div className="vs-indicator">VS</div>
                <div className="team-cores enemy-team-cores">
                  {enemyTeam?.cores?.map((core, idx) => (
                    <div
                      key={core.id}
                      className={`core-indicator enemy ${core.is_knocked_out ? 'ko' : ''} ${idx === enemyTeam.active_core_index ? 'active' : ''}`}
                    >
                      <span className="core-mini-name">{core.name.substring(0, 3)}</span>
                      <div className="core-mini-hp">
                        <div
                          className="core-mini-hp-fill"
                          style={{ width: `${(core.current_hp / core.max_hp) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <button className="forfeit-btn" onClick={() => navigate('/arena')}>
              FORFEIT
            </button>
          </div>

          {/* Battle Arena */}
          <div className="battle-arena">
            {/* Fighter HUDs - Fighting game style */}
            <FighterHUD
              core={activePlayerCore}
              energyPool={playerTeam?.energy_pool || 0}
              physicalPool={playerTeam?.physical_pool || 0}
              isEnemy={false}
            />
            <FighterHUD
              core={activeEnemyCore}
              energyPool={enemyTeam?.energy_pool || 0}
              physicalPool={enemyTeam?.physical_pool || 0}
              isEnemy={true}
            />

            {/* Core Sprites - Larger and centered */}
            <div className="arena-cores">
              <div className="player-core-area">
                <CoreDisplay
                  core={activePlayerCore}
                  isActive
                  animation={playerAnimation}
                />
              </div>
              <div className="enemy-core-area">
                <CoreDisplay
                  core={activeEnemyCore}
                  isEnemy
                  isActive
                  animation={enemyAnimation}
                />
              </div>
            </div>

            {/* Action Panel - Bottom center */}
            <div className="action-panel">
              {phase === 'dice_roll' && pendingDiceRolls.length > 0 && (
                <DiceAllocationPanel
                  diceRolls={pendingDiceRolls}
                  onAllocate={handleDiceAllocate}
                />
              )}

              {phase === 'action_select' && (
                <MoveSelector
                  moves={activePlayerCore?.equipped_moves || []}
                  energyPool={playerTeam?.energy_pool || 0}
                  physicalPool={playerTeam?.physical_pool || 0}
                  selectedMove={selectedMove}
                  onMoveSelect={handleMoveSelect}
                  onSwitch={handleSwitch}
                  onPass={handlePass}
                />
              )}

              {phase === 'resolution' && (
                <div className="resolution-panel">
                  <div className="resolution-message">Resolving actions...</div>
                </div>
              )}

              {phase === 'waiting' && (
                <div className="waiting-panel">
                  <div className="waiting-message">Waiting...</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: Battle Log Sidebar */}
        <div className="battle-sidebar">
          <TurnLog entries={turnLog} />
        </div>
      </div>

      {/* Switch Modal */}
      {showSwitchModal && (
        <div className="switch-modal-overlay" onClick={() => setShowSwitchModal(false)}>
          <div className="switch-modal" onClick={(e) => e.stopPropagation()}>
            <h3>SWITCH CORE</h3>
            <div className="switch-options">
              {playerTeam?.cores?.map((core, idx) => (
                <button
                  key={core.id}
                  className={`switch-option ${core.is_knocked_out ? 'ko' : ''} ${idx === playerTeam.active_core_index ? 'current' : ''}`}
                  onClick={() => handleSwitchConfirm(idx)}
                  disabled={core.is_knocked_out || idx === playerTeam.active_core_index}
                >
                  <span className="switch-core-name">{core.name}</span>
                  <span className="switch-core-hp">
                    {core.current_hp}/{core.max_hp} HP
                  </span>
                </button>
              ))}
            </div>
            <button className="cancel-btn" onClick={() => setShowSwitchModal(false)}>
              CANCEL
            </button>
          </div>
        </div>
      )}

      {/* Result Modal */}
      {result && (
        <BattleResultModal
          result={result}
          rewards={rewards}
          npcName={npcName}
          onClose={handleResultClose}
        />
      )}
    </div>
  );
};

export default Battle;
