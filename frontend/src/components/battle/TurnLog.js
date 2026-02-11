// frontend/src/components/battle/TurnLog.js
import React, { useRef, useEffect } from 'react';
import './TurnLog.css';

const TurnLog = ({ entries = [] }) => {
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [entries]);

  const renderMoveAction = (action) => {
    if (action.action_type === 'move') {
      // Stunned
      if (action.stunned) {
        return <span className="status-msg stunned">is stunned and can't move!</span>;
      }
      // Confused self-hit
      if (action.confused_self_hit) {
        return (
          <>
            <span className="status-msg confused">hit itself in confusion!</span>
            <span className="damage">-{action.damage_dealt} HP</span>
          </>
        );
      }
      // Status effect move (non-damage)
      if (action.effect_applied) {
        return (
          <>
            <span className="action-verb">used</span>
            <span className="move-name">{action.move_name}</span>
            {action.effect_message && (
              <span className="effect-msg">{action.effect_message.replace(action.source_core + ' ', '')}</span>
            )}
            {action.heal_amount > 0 && (
              <span className="heal-amount">+{action.heal_amount} HP</span>
            )}
            {action.stab && <span className="stab-indicator">STAB</span>}
          </>
        );
      }
      // Dodged
      if (action.dodged_by) {
        return (
          <>
            <span className="action-verb">used</span>
            <span className="move-name">{action.move_name}</span>
            <span className="action-verb">on</span>
            <span className="target">{action.target_core}</span>
            <span className="miss">DODGED! ({action.dodged_by})</span>
          </>
        );
      }
      // Normal attack
      return (
        <>
          <span className="action-verb">used</span>
          <span className="move-name">{action.move_name}</span>
          {action.accuracy_check ? (
            <>
              <span className="action-verb">on</span>
              <span className="target">{action.target_core}</span>
              <span className={`damage ${action.was_critical ? 'critical' : ''}`}>
                -{action.damage_dealt} HP
                {action.was_critical && ' CRIT!'}
                {action.stab && ' STAB'}
              </span>
            </>
          ) : (
            <span className="miss">MISSED!</span>
          )}
        </>
      );
    }

    if (action.action_type === 'switch') {
      return (
        <>
          <span className="action-verb">switched to</span>
          <span className="target">{action.new_active_core}</span>
        </>
      );
    }

    if (action.action_type === 'gain_resource') {
      return <span className="action-verb gain-resource">gained resources</span>;
    }

    return <span className="action-verb">passed</span>;
  };

  const renderEntry = (entry, index) => {
    switch (entry.type) {
      case 'turn_start':
        return (
          <div key={index} className="log-entry turn-start">
            <span className="turn-marker">TURN {entry.turn}</span>
          </div>
        );

      case 'action':
        return (
          <div key={index} className="log-entry action">
            {entry.player && entry.player.success && (
              <div className="action-line player">
                <span className="actor">{entry.player.source_core}</span>
                {renderMoveAction(entry.player)}
              </div>
            )}

            {entry.enemy && entry.enemy.success && (
              <div className="action-line enemy">
                <span className="actor">{entry.enemy.source_core}</span>
                {renderMoveAction(entry.enemy)}
              </div>
            )}
          </div>
        );

      case 'effect_tick':
        return (
          <div key={index} className="log-entry effect-tick">
            {(entry.events || []).map((evt, i) => (
              <div key={i} className={`effect-event ${evt.team}`}>
                {evt.type === 'heal' && (
                  <span className="heal-tick">
                    {evt.core_name} regenerated <span className="heal-amount">+{evt.amount} HP</span>
                  </span>
                )}
                {evt.type === 'effect_expired' && (
                  <span className="effect-expired">
                    {evt.core_name}'s {evt.effect_name} wore off
                  </span>
                )}
              </div>
            ))}
          </div>
        );

      case 'forced_switch':
        return (
          <div key={index} className={`log-entry forced-switch ${entry.team}`}>
            <span className="ko-notice">
              {entry.team === 'player' ? 'Your' : 'Enemy'} core was knocked out!
            </span>
          </div>
        );

      case 'battle_end':
        return (
          <div key={index} className={`log-entry battle-end ${entry.result}`}>
            <span className="result-text">
              {entry.result === 'win' ? 'VICTORY!' : 'DEFEAT'}
            </span>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="turn-log">
      <div className="log-header">BATTLE LOG</div>
      <div className="log-content">
        {entries.length === 0 ? (
          <div className="log-empty">Battle starting...</div>
        ) : (
          entries.map((entry, index) => renderEntry(entry, index))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
};

export default TurnLog;
