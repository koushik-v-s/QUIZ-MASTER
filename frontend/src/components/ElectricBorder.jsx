import { useRef, useEffect, useState } from 'react';

const ElectricBorder = ({ children, color = '#3b82f6', className = '' }) => {
  const borderRef = useRef(null);
  const [angle, setAngle] = useState(0);

  useEffect(() => {
    let animId;
    const animate = () => {
      setAngle(prev => (prev + 2) % 360);
      animId = requestAnimationFrame(animate);
    };
    animId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animId);
  }, []);

  return (
    <div
      ref={borderRef}
      className={className}
      style={{
        position: 'relative',
        borderRadius: '16px',
        padding: '2px',
        background: `conic-gradient(from ${angle}deg, transparent 0%, ${color} 10%, transparent 20%, transparent 40%, ${color}88 50%, transparent 60%, transparent 80%, ${color}44 90%, transparent 100%)`,
        overflow: 'hidden',
      }}
    >
      {/* Inner content */}
      <div
        style={{
          position: 'relative',
          borderRadius: '14px',
          background: '#0d0d0d',
          overflow: 'hidden',
        }}
      >
        {children}
      </div>

      {/* Glow effect */}
      <div
        style={{
          position: 'absolute',
          inset: '-4px',
          borderRadius: '20px',
          background: `conic-gradient(from ${angle}deg, transparent 0%, ${color}33 10%, transparent 20%, transparent 40%, ${color}22 50%, transparent 60%, transparent 80%, ${color}11 90%, transparent 100%)`,
          filter: 'blur(8px)',
          zIndex: -1,
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};

export default ElectricBorder;
