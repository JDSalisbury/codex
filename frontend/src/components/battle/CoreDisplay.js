// frontend/src/components/battle/CoreDisplay.js
import { useState, useEffect, useRef } from 'react';
import './CoreDisplay.css';

const CoreDisplay = ({ core, isEnemy = false, isActive = false, animation = null }) => {
  const [mouseOffset, setMouseOffset] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const spriteRef = useRef(null);

  // Track mouse position and calculate offset from sprite center
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!spriteRef.current) return;

      const rect = spriteRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Calculate offset from center (normalized to -1 to 1 range)
      const offsetX = (e.clientX - centerX) / (window.innerWidth / 2);
      const offsetY = (e.clientY - centerY) / (window.innerHeight / 2);

      // Clamp values
      setMouseOffset({
        x: Math.max(-1, Math.min(1, offsetX)),
        y: Math.max(-1, Math.min(1, offsetY)),
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  if (!core) return null;

  const hpPercent = Math.max(0, (core.current_hp / core.max_hp) * 100);
  const isKnockedOut = core.is_knocked_out || core.current_hp <= 0;

  const getHpBarColor = (percent) => {
    if (percent > 50) return 'hp-high';
    if (percent > 25) return 'hp-medium';
    return 'hp-low';
  };

  // Build animation class
  const animationClass = animation ? `anim-${animation}` : '';

  // Calculate transform based on mouse position
  // Subtle follow effect, stronger on hover
  const followStrength = isHovered ? 12 : 4;
  const scaleBoost = isHovered ? 1.05 : 1;
  const translateX = mouseOffset.x * followStrength;
  const translateY = mouseOffset.y * (followStrength * 0.5); // Less vertical movement
  const rotateY = mouseOffset.x * (isHovered ? 8 : 3);
  const rotateX = 8 - (mouseOffset.y * (isHovered ? 5 : 2)); // Base tilt + mouse influence

  const spriteStyle = animation ? {} : {
    transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateX(${translateX}px) translateY(${translateY}px) scale(${scaleBoost})`,
  };

  return (
    <div className={`core-display ${isEnemy ? 'enemy' : 'player'} ${isActive ? 'active' : ''} ${isKnockedOut ? 'knocked-out' : ''}`}>
      {/* Core sprite standing like a Pokemon */}
      <div className="core-3d-stage" ref={spriteRef}>
        <div
          className={`core-sprite-standing ${animationClass} ${isHovered ? 'hovered' : ''}`}
          style={spriteStyle}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          {core.image_url ? (
            <img
              src={core.image_url}
              alt={core.name}
              className="core-sprite"
            />
          ) : (
            <div className="core-sprite-placeholder">
              {core.name.charAt(0)}
            </div>
          )}
          {isKnockedOut && <div className="ko-overlay">K.O.</div>}
        </div>
        {/* Ground shadow underneath */}
        <div className={`core-ground-shadow ${animationClass}`}></div>
      </div>

      <div className="core-info">
        <div className="core-name-row">
          <span className="core-name">{core.name}</span>
          <span className={`core-rarity rarity-${core.rarity?.toLowerCase()}`}>
            Lv.{core.lvl}
          </span>
        </div>

        <div className="hp-bar-container">
          <div className="hp-bar-background">
            <div
              className={`hp-bar-fill ${getHpBarColor(hpPercent)}`}
              style={{ width: `${hpPercent}%` }}
            />
          </div>
          <span className="hp-text">
            {core.current_hp} / {core.max_hp}
          </span>
        </div>

        {core.type && (
          <div className="core-type-badge">{core.type}</div>
        )}
      </div>
    </div>
  );
};

export default CoreDisplay;
