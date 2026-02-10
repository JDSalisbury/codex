// frontend/src/components/battle/TurnLog.js
import React, { useRef, useEffect } from 'react';
import './TurnLog.css';

const TurnLog = ({ entries = [] }) => {
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [entries]);

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
                {entry.player.action_type === 'move' ? (
                  <>
                    <span className="action-verb">used</span>
                    <span className="move-name">{entry.player.move_name}</span>
                    {entry.player.accuracy_check ? (
                      <>
                        <span className="action-verb">on</span>
                        <span className="target">{entry.player.target_core}</span>
                        <span className={`damage ${entry.player.was_critical ? 'critical' : ''}`}>
                          -{entry.player.damage_dealt} HP
                          {entry.player.was_critical && ' CRIT!'}
                        </span>
                      </>
                    ) : (
                      <span className="miss">MISSED!</span>
                    )}
                  </>
                ) : entry.player.action_type === 'switch' ? (
                  <>
                    <span className="action-verb">switched to</span>
                    <span className="target">{entry.player.new_active_core}</span>
                  </>
                ) : entry.player.action_type === 'gain_resource' ? (
                  <span className="action-verb gain-resource">gained resources</span>
                ) : (
                  <span className="action-verb">passed</span>
                )}
              </div>
            )}

            {entry.enemy && entry.enemy.success && (
              <div className="action-line enemy">
                <span className="actor">{entry.enemy.source_core}</span>
                {entry.enemy.action_type === 'move' ? (
                  <>
                    <span className="action-verb">used</span>
                    <span className="move-name">{entry.enemy.move_name}</span>
                    {entry.enemy.accuracy_check ? (
                      <>
                        <span className="action-verb">on</span>
                        <span className="target">{entry.enemy.target_core}</span>
                        <span className={`damage ${entry.enemy.was_critical ? 'critical' : ''}`}>
                          -{entry.enemy.damage_dealt} HP
                          {entry.enemy.was_critical && ' CRIT!'}
                        </span>
                      </>
                    ) : (
                      <span className="miss">MISSED!</span>
                    )}
                  </>
                ) : entry.enemy.action_type === 'switch' ? (
                  <>
                    <span className="action-verb">switched to</span>
                    <span className="target">{entry.enemy.new_active_core}</span>
                  </>
                ) : entry.enemy.action_type === 'gain_resource' ? (
                  <span className="action-verb gain-resource">gained resources</span>
                ) : (
                  <span className="action-verb">passed</span>
                )}
              </div>
            )}
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
