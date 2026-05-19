import React, { useRef, useEffect, useState, useCallback } from 'react';
import ReactDOM from 'react-dom';

interface SignatureCanvasProps {
  onSave: (dataUrl: string) => void;
  onClose: () => void;
  title?: string;
  signerName?: string;
}

const SignatureCanvas: React.FC<SignatureCanvasProps> = ({
  onSave,
  onClose,
  title = 'Firma de Conformidad',
  signerName = 'Representante',
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isDrawing = useRef(false);
  const lastPos = useRef<{ x: number; y: number } | null>(null);
  const [hasStrokes, setHasStrokes] = useState(false);

  const getPos = (e: MouseEvent | Touch, canvas: HTMLCanvasElement) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clientX = 'clientX' in e ? e.clientX : (e as Touch).clientX;
    const clientY = 'clientY' in e ? e.clientY : (e as Touch).clientY;
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY,
    };
  };

  const draw = useCallback((x: number, y: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx || !lastPos.current) return;
    ctx.beginPath();
    ctx.moveTo(lastPos.current.x, lastPos.current.y);
    ctx.lineTo(x, y);
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.stroke();
    lastPos.current = { x, y };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Fill white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw guiding line
    ctx.setLineDash([5, 8]);
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(40, canvas.height - 60);
    ctx.lineTo(canvas.width - 40, canvas.height - 60);
    ctx.stroke();
    ctx.setLineDash([]);

    const onMouseDown = (e: MouseEvent) => {
      isDrawing.current = true;
      lastPos.current = getPos(e, canvas);
    };
    const onMouseMove = (e: MouseEvent) => {
      if (!isDrawing.current) return;
      const pos = getPos(e, canvas);
      draw(pos.x, pos.y);
      setHasStrokes(true);
    };
    const onMouseUp = () => { isDrawing.current = false; lastPos.current = null; };

    const onTouchStart = (e: TouchEvent) => {
      e.preventDefault();
      isDrawing.current = true;
      lastPos.current = getPos(e.touches[0], canvas);
    };
    const onTouchMove = (e: TouchEvent) => {
      e.preventDefault();
      if (!isDrawing.current) return;
      const pos = getPos(e.touches[0], canvas);
      draw(pos.x, pos.y);
      setHasStrokes(true);
    };
    const onTouchEnd = () => { isDrawing.current = false; lastPos.current = null; };

    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseUp);
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });
    canvas.addEventListener('touchend', onTouchEnd);

    return () => {
      canvas.removeEventListener('mousedown', onMouseDown);
      canvas.removeEventListener('mousemove', onMouseMove);
      canvas.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('mouseleave', onMouseUp);
      canvas.removeEventListener('touchstart', onTouchStart);
      canvas.removeEventListener('touchmove', onTouchMove);
      canvas.removeEventListener('touchend', onTouchEnd);
    };
  }, [draw]);

  const handleClear = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.setLineDash([5, 8]);
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(40, canvas.height - 60);
    ctx.lineTo(canvas.width - 40, canvas.height - 60);
    ctx.stroke();
    ctx.setLineDash([]);
    setHasStrokes(false);
  };

  const handleSave = () => {
    const canvas = canvasRef.current;
    if (!canvas || !hasStrokes) return;
    onSave(canvas.toDataURL('image/png'));
    onClose();
  };

  return ReactDOM.createPortal(
    <div className="fixed inset-0 z-[9999] flex flex-col bg-slate-950 animate-in fade-in zoom-in duration-300">
      {/* Header */}
      <div className="p-6 bg-slate-900 border-b border-white/10 flex justify-between items-center shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="bg-cyan-600 p-2.5 rounded-xl">
            <span className="text-white text-xl">✎</span>
          </div>
          <div>
            <h3 className="text-white font-black uppercase tracking-[0.3em] text-sm md:text-base">{title}</h3>
            <p className="text-[10px] md:text-xs text-slate-400 mt-0.5 font-bold uppercase tracking-widest opacity-70">Área de Captura Biométrica</p>
          </div>
        </div>
        <button 
          onClick={onClose} 
          className="px-6 py-2.5 bg-slate-800 hover:bg-red-500/20 hover:text-red-400 rounded-xl transition-all text-slate-300 text-[10px] font-black uppercase tracking-widest border border-white/5"
        >
          Cancelar Firma
        </button>
      </div>

      {/* Main Area */}
      <div className="flex-1 p-4 md:p-10 flex flex-col gap-8 bg-slate-950 overflow-hidden">
        {/* Canvas Area */}
        <div className="flex-1 relative rounded-[2.5rem] overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)] border-4 border-slate-800 bg-white group cursor-crosshair">
          <canvas
            ref={canvasRef}
            width={1200}
            height={600}
            className="w-full h-full block touch-none"
            style={{ touchAction: 'none' }}
          />
          {!hasStrokes && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
              <div className="text-center">
                <div className="w-24 h-24 border-2 border-slate-300 rounded-full mx-auto mb-6 animate-pulse flex items-center justify-center">
                  <span className="text-4xl text-slate-400">✎</span>
                </div>
                <p className="text-slate-400 text-sm font-black uppercase tracking-[0.5em] select-none">
                  FIRM AR AQUÍ
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-8 pb-4">
          <div className="text-center md:text-left bg-white/5 px-8 py-4 rounded-3xl border border-white/5">
            <p className="text-[9px] text-slate-500 font-black uppercase tracking-widest mb-1">Nombre del Firmante</p>
            <p className="text-sm font-black text-cyan-400 uppercase tracking-[0.2em]">{signerName}</p>
          </div>

          <div className="flex gap-4 w-full md:w-auto">
            <button
              onClick={handleClear}
              className="px-10 py-5 bg-slate-900 hover:bg-slate-800 rounded-2xl text-slate-400 text-[10px] font-black uppercase tracking-[0.2em] transition-all border border-white/5"
            >
              Limpiar Área
            </button>
            <button
              onClick={handleSave}
              disabled={!hasStrokes}
              className="flex-1 md:flex-none px-16 py-5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-30 disabled:cursor-not-allowed rounded-2xl text-white font-black uppercase tracking-[0.25em] text-[10px] shadow-2xl shadow-cyan-900/40 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
            >
              ✓ Confirmar Firma
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default SignatureCanvas;
