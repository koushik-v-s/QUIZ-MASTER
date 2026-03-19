const BorderGlow = ({ children, color = '#10b981', className = '' }) => {
  return (
    <div
      className={className}
      style={{
        position: 'relative',
        borderRadius: '16px',
        overflow: 'hidden',
      }}
    >
      {/* Rotating glow border */}
      <div
        style={{
          position: 'absolute',
          inset: '-2px',
          borderRadius: '18px',
          background: `conic-gradient(from var(--border-angle, 0deg), transparent 40%, ${color}88, ${color}, ${color}88, transparent 60%)`,
          animation: 'borderGlowSpin 4s linear infinite',
          zIndex: 0,
        }}
      />

      {/* Inner content */}
      <div
        style={{
          position: 'relative',
          borderRadius: '16px',
          background: '#0d0d0d',
          zIndex: 1,
        }}
      >
        {children}
      </div>

      <style>{`
        @property --border-angle {
          syntax: '<angle>';
          initial-value: 0deg;
          inherits: false;
        }
        @keyframes borderGlowSpin {
          to { --border-angle: 360deg; }
        }
      `}</style>
    </div>
  );
};

export default BorderGlow;
