import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { visitReportsAPI } from '../services/api';
import { 
  PencilSquareIcon, 
  CheckCircleIcon, 
  ArrowLeftIcon, 
  DocumentArrowDownIcon,
  ExclamationCircleIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const VisitReportPreview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPDF = async () => {
      try {
        setLoading(true);
        const res = await visitReportsAPI.generatePDF(id!, { final: false });
        const blob = new Blob([res.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        setPdfUrl(url);
      } catch (err) {
        console.error("Error loading PDF:", err);
        setError("No se pudo cargar la previsualización del PDF.");
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchPDF();
    
    return () => {
      if (pdfUrl) window.URL.revokeObjectURL(pdfUrl);
    };
  }, [id]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
        <div className="relative w-24 h-24 mb-8">
          <div className="absolute inset-0 border-4 border-cyan-500/20 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-cyan-500 rounded-full border-t-transparent animate-spin"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <SparklesIcon className="w-10 h-10 text-cyan-400 animate-pulse" />
          </div>
        </div>
        <h2 className="text-xl font-black text-white uppercase tracking-tighter mb-2">Generando Vista Previa</h2>
        <p className="text-slate-400 text-sm font-bold uppercase tracking-widest animate-pulse">Preparando documento profesional...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
        <ExclamationCircleIcon className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-black text-white uppercase mb-2">{error}</h2>
        <button onClick={() => navigate(-1)} className="mt-4 px-6 py-2 bg-slate-800 text-white rounded-xl font-black uppercase text-xs tracking-widest">
          Volver al formulario
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-slate-900 flex flex-col z-[100] animate-in fade-in duration-500 overflow-hidden">
      {/* Header Compacto */}
      <div className="p-4 bg-slate-950 border-b border-white/10 flex items-center justify-between shadow-2xl">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/visit-reports')} className="p-2 hover:bg-white/5 rounded-lg text-slate-400 transition-colors">
            <ArrowLeftIcon className="w-5 h-5"/>
          </button>
          <div>
            <h1 className="text-sm font-black text-white uppercase tracking-tight">Revisión de Reporte</h1>
            <p className="text-[10px] text-cyan-500 font-bold uppercase tracking-widest">Vista previa del documento</p>
          </div>
        </div>
        <a 
          href={pdfUrl!} 
          download={`Reporte_Visita_${id}.pdf`}
          className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-slate-300 transition-all"
        >
          <DocumentArrowDownIcon className="w-5 h-5"/>
        </a>
      </div>

      {/* Visor de PDF */}
      <div className="flex-1 bg-slate-800 relative overflow-hidden flex flex-col">
        {pdfUrl ? (
          <object
            data={pdfUrl}
            type="application/pdf"
            className="w-full h-full border-none"
          >
            {/* Fallback Profesional para móviles que bloquean el embebido */}
            <div className="flex flex-col items-center justify-center h-full p-8 text-center bg-slate-900">
              <div className="p-8 bg-slate-800 rounded-3xl border border-white/10 shadow-2xl flex flex-col items-center gap-6 max-w-sm">
                <div className="p-4 bg-cyan-500/10 rounded-2xl">
                  <DocumentArrowDownIcon className="w-12 h-12 text-cyan-500" />
                </div>
                <h3 className="text-white font-black uppercase tracking-tighter text-lg">Reporte Generado</h3>
                <p className="text-slate-400 text-xs font-bold leading-relaxed">
                  El documento está listo para revisión. Presiona el botón para visualizarlo en pantalla completa y verificar los datos antes de firmar.
                </p>
                <a 
                  href={pdfUrl} 
                  target="_blank" 
                  rel="noreferrer"
                  className="w-full py-4 bg-cyan-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-cyan-900/40 active:scale-95 transition-all"
                >
                  Ver Documento Completo
                </a>
              </div>
            </div>
          </object>
        ) : (
          <div className="flex items-center justify-center h-full text-slate-500 font-bold uppercase tracking-widest text-xs">
            No hay ninguna vista previa disponible
          </div>
        )}
      </div>

      {/* BARRA FLOTANTE STICKY (Glassmorphism) */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-md z-[110]">
        <motion.div 
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="bg-slate-900/80 backdrop-blur-xl border border-white/20 p-4 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex items-center justify-between gap-4"
        >
          <button 
            onClick={() => navigate('/visit-reports')}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all active:scale-95 border border-white/5"
          >
            <ArrowLeftIcon className="w-4 h-4 text-slate-400"/>
            Volver
          </button>
          
          <button 
            onClick={() => {
              // Navegar al listado pero abrir el modal de firma inmediatamente
              // o navegar a una ruta de firma directa
              navigate(`/visit-reports?sign=${id}`);
            }}
            className="flex-1 flex items-center justify-center gap-2 py-3.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl text-xs font-black uppercase tracking-widest transition-all shadow-lg shadow-blue-900/40 active:scale-95"
          >
            <CheckCircleIcon className="w-4 h-4"/>
            Firmar
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default VisitReportPreview;
