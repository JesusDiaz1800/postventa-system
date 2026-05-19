import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  ClipboardDocumentCheckIcon,
  PlusCircleIcon,
  CalendarDaysIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { dashboardAPI } from '../services/api';

const QuickActions = () => {
  const navigate = useNavigate();
  const [metrics, setMetrics] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    dashboardAPI.getMetrics()
      .then(res => {
        if (res.data?.success) {
          setMetrics(res.data.data);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-1 flex flex-col font-sans relative selection:bg-blue-500/30 overflow-hidden min-h-full">

      {/* Futuristic Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[20%] w-[50%] h-[50%] bg-blue-600/20 blur-[100px] rounded-full mix-blend-screen opacity-60 animate-pulse" />
        <div className="absolute bottom-[-10%] right-[10%] w-[50%] h-[50%] bg-cyan-500/20 blur-[100px] rounded-full mix-blend-screen opacity-60" />
        
        {/* Tech Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_40%,#000_10%,transparent_100%)]" />
      </div>

      <div className="flex-1 relative z-10 flex flex-col items-center justify-center p-8 max-w-7xl mx-auto w-full h-full">

        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center w-full max-w-3xl mb-16"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 mb-8 backdrop-blur-md">
            <SparklesIcon className="w-5 h-5 animate-pulse" />
            <span className="text-xs font-black tracking-[0.2em] uppercase">Sertec System Unificado</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-black text-white tracking-tight mb-6 leading-tight">
            Gestión Rápida de <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 drop-shadow-[0_0_25px_rgba(59,130,246,0.4)]">
              Reportes de Visita
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed">
            Plataforma exclusiva para el control ágil y sincronización directa con SAP Service Layer de reportes en terreno.
          </p>

        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl">
          
          {/* Card: Programar Visita (Left) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            whileHover={{ y: -5, scale: 1.02 }}
            onClick={() => navigate('/schedule-visit')}
            className="group cursor-pointer relative p-8 rounded-3xl bg-gradient-to-b from-[#0f172a]/90 to-[#030014]/90 border border-white/5 hover:border-emerald-500/30 shadow-2xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10 flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-6 text-emerald-400 group-hover:bg-emerald-500 group-hover:text-white transition-colors duration-300 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                <CalendarDaysIcon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Programar Visita</h3>
              <p className="text-sm text-slate-400">Asigna visitas a técnicos precargando cliente y obra desde SAP Service Layer.</p>
            </div>
          </motion.div>

          {/* Card: Ver Historial (Middle) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            whileHover={{ y: -5, scale: 1.02 }}
            onClick={() => navigate('/visit-reports')}
            className="group cursor-pointer relative p-8 rounded-3xl bg-gradient-to-b from-[#0f172a]/90 to-[#030014]/90 border border-white/5 hover:border-blue-500/30 shadow-2xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-blue-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10 flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6 text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-colors duration-300 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
                <ClipboardDocumentCheckIcon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Gestionar Visitas</h3>
              <p className="text-sm text-slate-400">Consulta y administra todos los reportes de visita en terreno realizados.</p>
            </div>
          </motion.div>

          {/* Card: Crear Reporte (Right) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            whileHover={{ y: -5, scale: 1.02 }}
            onClick={() => navigate('/visit-report-form')}
            className="group cursor-pointer relative p-8 rounded-3xl bg-gradient-to-b from-[#0f172a]/90 to-[#030014]/90 border border-white/5 hover:border-cyan-500/30 shadow-2xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="relative z-10 flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 flex items-center justify-center mb-6 text-cyan-400 group-hover:bg-cyan-500 group-hover:text-white transition-colors duration-300 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                <PlusCircleIcon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Nuevo Reporte</h3>
              <p className="text-sm text-slate-400">Genera un reporte de visita y sincroniza la llamada en SAP al instante.</p>
            </div>
          </motion.div>

        </div>

      </div>

    </div>
  );
};

export default QuickActions;
