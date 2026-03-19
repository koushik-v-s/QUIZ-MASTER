const LightRays = ({ color = '#10b981', opacity = 0.15, className = '' }) => {
  return (
    <div className={className} style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none', zIndex: 0 }}>
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: '-50%',
            left: `${15 + i * 15}%`,
            width: '2px',
            height: '200%',
            background: `linear-gradient(to bottom, transparent, ${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}, transparent)`,
            transform: `rotate(${-15 + i * 7}deg)`,
            animation: `lightRayFloat ${3 + i * 0.5}s ease-in-out infinite alternate`,
            opacity: 0.5 + (i % 3) * 0.2,
          }}
        />
      ))}
      <style>{`
        @keyframes lightRayFloat {
          0% { transform: translateX(-10px) rotate(-15deg); opacity: 0.3; }
          100% { transform: translateX(10px) rotate(-10deg); opacity: 0.7; }
        }
      `}</style>
    </div>
  );
};

export default LightRays;
