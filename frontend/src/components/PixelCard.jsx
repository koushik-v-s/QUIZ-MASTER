import { useRef, useEffect, useState } from 'react';

const PixelCard = ({ children, gap = 5, speed = 35, colors = '#10b981,#3b82f6,#8b5cf6', className = '' }) => {
  const containerRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    const colorArr = colors.split(',');
    let animId;
    let time = 0;

    const resize = () => {
      canvas.width = container.offsetWidth;
      canvas.height = container.offsetHeight;
    };
    resize();

    const ro = new ResizeObserver(resize);
    ro.observe(container);

    const draw = () => {
      time += 0.01;
      const { width: w, height: h } = canvas;
      ctx.clearRect(0, 0, w, h);

      const cols = Math.ceil(w / gap);
      const rows = Math.ceil(h / gap);

      for (let i = 0; i < cols; i++) {
        for (let j = 0; j < rows; j++) {
          const x = i * gap;
          const y = j * gap;
          // Only draw border pixels
          if (i > 1 && i < cols - 2 && j > 1 && j < rows - 2) continue;

          const wave = Math.sin(i * 0.15 + time * speed * 0.05) + Math.cos(j * 0.15 + time * speed * 0.03);
          const alpha = Math.max(0, Math.min(1, (wave + 2) / 4));

          if (alpha > 0.15) {
            const colorIdx = Math.floor((i + j + Math.floor(time * 2)) % colorArr.length);
            ctx.fillStyle = colorArr[colorIdx].trim();
            ctx.globalAlpha = alpha * 0.7;
            ctx.fillRect(x, y, gap - 1, gap - 1);
          }
        }
      }
      ctx.globalAlpha = 1;
      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      ro.disconnect();
    };
  }, [gap, speed, colors]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ position: 'relative', overflow: 'hidden', borderRadius: '16px' }}
    >
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />
      <div style={{ position: 'relative', zIndex: 1 }}>{children}</div>
    </div>
  );
};

export default PixelCard;
