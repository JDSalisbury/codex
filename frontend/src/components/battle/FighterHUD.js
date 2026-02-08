// frontend/src/components/battle/FighterHUD.js
import './FighterHUD.css';

const FighterHUD = ({
  core,
  energyPool = 0,
  physicalPool = 0,
  maxEnergy = 20,
  maxPhysical = 20,
  isEnemy = false,
}) => {
  if (!core) return null;

  const hpPercent = Math.max(0, (core.current_hp / core.max_hp) * 100);
  const energyPercent = Math.max(0, Math.min(100, (energyPool / maxEnergy) * 100));
  const physicalPercent = Math.max(0, Math.min(100, (physicalPool / maxPhysical) * 100));

  const getHpColor = (percent) => {
    if (percent > 50) return 'hp-high';
    if (percent > 25) return 'hp-medium';
    return 'hp-low';
  };

  return (
    <div className={`fighter-hud ${isEnemy ? 'enemy' : 'player'}`}>
      {/* HP Bar with Name */}
      <div className="hud-hp-section">
        <div className="hud-hp-bar">
          <div
            className={`hud-hp-fill ${getHpColor(hpPercent)}`}
            style={{ width: `${hpPercent}%` }}
          />
          <div className="hud-hp-text">
            {core.current_hp} / {core.max_hp}
          </div>
        </div>
        <div className="hud-name">{core.name}</div>
      </div>

      {/* Resource Bars */}
      <div className="hud-resource-bars">
        <div className="hud-resource energy">
          <div
            className="hud-resource-fill"
            style={{ width: `${energyPercent}%` }}
          />
          <span className="hud-resource-value">{energyPool}</span>
        </div>
        <div className="hud-resource physical">
          <div
            className="hud-resource-fill"
            style={{ width: `${physicalPercent}%` }}
          />
          <span className="hud-resource-value">{physicalPool}</span>
        </div>
      </div>

      {/* Core Info Badge */}
      <div className="hud-core-info">
        <span className={`hud-rarity rarity-${core.rarity?.toLowerCase()}`}>
          {core.rarity}
        </span>
        <span className="hud-level">Lv.{core.lvl}</span>
        {core.type && (
          <span className="hud-type">{core.type}</span>
        )}
      </div>
    </div>
  );
};

export default FighterHUD;
