import { useRef, useEffect } from 'react';

const LiquidEther = ({ 
  color1 = '#10b981', 
  color2 = '#3b82f6', 
  color3 = '#7c3aed', 
  color4 = '#06b6d4', 
  speed = 0.002 
}) => {
  const canvasRef = useRef(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animId;
    let t = 0;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const handleMouseMove = (e) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    window.addEventListener('mousemove', handleMouseMove);

    const draw = () => {
      t += speed;
      const { width: w, height: h } = canvas;
      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;

      ctx.clearRect(0, 0, w, h);

      // Background blobs that gently drift
      const blobs = [
        { x: w * (0.3 + 0.2 * Math.sin(t * 0.7)), y: h * (0.3 + 0.2 * Math.cos(t * 0.5)), r: w * 0.25, color: color1 },
        { x: w * (0.7 + 0.2 * Math.cos(t * 0.6)), y: h * (0.6 + 0.2 * Math.sin(t * 0.8)), r: w * 0.22, color: color2 },
        { x: w * (0.5 + 0.15 * Math.sin(t * 1.1)), y: h * (0.7 + 0.15 * Math.cos(t * 0.9)), r: w * 0.2, color: color3 },
        { x: w * (0.6 + 0.18 * Math.cos(t * 0.9)), y: h * (0.3 + 0.2 * Math.sin(t * 0.7)), r: w * 0.18, color: color4 },
      ];

      // Mouse-following blob — large, prominent
      blobs.push({
        x: mx,
        y: my,
        r: w * 0.18,
        color: color1,
      });
      blobs.push({
        x: mx + 50 * Math.sin(t * 2),
        y: my + 50 * Math.cos(t * 2),
        r: w * 0.12,
        color: color3,
      });

      blobs.forEach(b => {
        const grad = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
        grad.addColorStop(0, b.color + '66');
        grad.addColorStop(0.4, b.color + '33');
        grad.addColorStop(0.7, b.color + '11');
        grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [color1, color2, color3, color4, speed]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        zIndex: 0,
        filter: 'blur(80px) saturate(1.8)',
        opacity: 0.7,
      }}
    />
  );
};

export default LiquidEther;
