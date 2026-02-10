import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNotifications } from '../hooks/useNotifications';
import { incidentsAPI } from '../services/api';
import { exportReportStats } from '../utils/exportUtils';
import { InteractivePieChart } from '../components/InteractivePieChart';
import {
  ChartBarIcon,
  ExclamationTriangleIcon,
  PrinterIcon,
  CheckCircleIcon,
  BeakerIcon,
  TruckIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon,
  ClockIcon,
  PresentationChartLineIcon
} from '@heroicons/react/24/outline';

const ReportsPage = () => {
  const { showSuccess } = useNotifications();
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  // Fetch all incidents for statistics
  const { data: incidentsData, isLoading, error } = useQuery({
    queryKey: ['incidents-reports'],
    queryFn: async () => {
      const response = await incidentsAPI.list({ page_size: 1000 });
      return response.data?.results || response.data || [];
    },
    staleTime: 5 * 60 * 1000,
  });

  const incidents = incidentsData || [];

  // Calculate comprehensive statistics
  const stats = useMemo(() => {
    if (!incidents.length) return null;

    const normalizeText = (text) => {
      if (!text) return 'SIN DATOS';
      return text.toString().normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase().trim();
    };

    const cerrados = incidents.filter(i => i.estado === 'cerrado').length;
    const abiertos = incidents.filter(i => i.estado !== 'cerrado' && (i.estado === 'abierto' || i.estado === 'nuevo') && !i.escalated_to_quality && !i.escalated_to_supplier).length;
    const laboratorio = incidents.filter(i => i.estado !== 'cerrado' && ((i.estado === 'calidad' || i.estado === 'reporte_visita' || i.estado === 'en_calidad') || (i.escalated_to_quality && !i.escalated_to_supplier))).length;
    const proveedor = incidents.filter(i => i.estado !== 'cerrado' && (i.estado === 'proveedor' || i.estado === 'en_proveedor' || i.escalated_to_supplier)).length;

    const clientCount = {};
    incidents.forEach(i => {
      const client = i.cliente || 'Sin cliente';
      const normalizedClient = normalizeText(client);
      clientCount[normalizedClient] = (clientCount[normalizedClient] || 0) + 1;
    });
    const topClients = Object.entries(clientCount).sort((a, b) => b[1] - a[1]).slice(0, 5);

    const categoryTree = {};
    incidents.forEach(i => {
      const catRaw = typeof i.categoria === 'string' ? i.categoria : (i.categoria?.name || 'Sin categoría');
      const cat = normalizeText(catRaw);
      const subRaw = i.subcategoria || 'General';
      if (!categoryTree[cat]) categoryTree[cat] = { total: 0, subcategories: {} };
      categoryTree[cat].total++;
      const subParts = subRaw.split(/\s+-\s+|\s*,\s*|\s*\/\s*/);
      subParts.forEach(part => {
        const cleanPart = normalizeText(part);
        if (cleanPart && cleanPart.length > 1) categoryTree[cat].subcategories[cleanPart] = (categoryTree[cat].subcategories[cleanPart] || 0) + 1;
      });
    });

    const monthlyStats = Array(12).fill(0).map(() => ({ total: 0, cerrados: 0 }));
    incidents.forEach(i => {
      const dateStr = i.fecha_deteccion || i.fecha_reporte || i.created_at;
      const date = new Date(dateStr.includes('T') ? dateStr : dateStr + 'T12:00:00');
      if (date.getFullYear() === selectedYear) {
        monthlyStats[date.getMonth()].total++;
        if (i.estado === 'cerrado') monthlyStats[date.getMonth()].cerrados++;
      }
    });

    const yearlyStats = {};
    incidents.forEach(i => {
      const dateStr = i.fecha_deteccion || i.fecha_reporte || i.created_at;
      const year = new Date(dateStr.includes('T') ? dateStr : dateStr + 'T12:00:00').getFullYear();
      if (!yearlyStats[year]) yearlyStats[year] = { total: 0, cerrados: 0 };
      yearlyStats[year].total++;
      if (i.estado === 'cerrado') yearlyStats[year].cerrados++;
    });

    const resolutionRate = incidents.length > 0 ? Math.round((cerrados / incidents.length) * 100) : 0;
    const cutoffDate = new Date('2026-01-13T00:00:00');
    const closedWithTime = incidents.filter(i => i.estado === 'cerrado' && i.closed_at && i.fecha_deteccion && new Date(i.fecha_deteccion) >= cutoffDate);
    const avgResolutionDays = closedWithTime.length > 0 ? Math.round(closedWithTime.reduce((sum, i) => sum + ((new Date(i.closed_at) - new Date(i.fecha_deteccion)) / (1000 * 60 * 60 * 24)), 0) / closedWithTime.length) : 0;

    const providerCount = {};
    incidents.forEach(i => {
      const prov = i.provider || 'Sin proveedor';
      const normalizedProv = normalizeText(prov);
      providerCount[normalizedProv] = (providerCount[normalizedProv] || 0) + 1;
    });

    return {
      total: incidents.length, abiertos, laboratorio, proveedor, cerrados, resolutionRate, avgResolutionDays,
      categoryTree, topClients, monthlyStats, yearlyStats, topProviders: Object.entries(providerCount).sort((a, b) => b[1] - a[1]).slice(0, 5)
    };
  }, [incidents, selectedYear]);

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center p-20 animate-fade-in">
      <div className="w-16 h-16 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
      <p className="mt-4 text-gray-500 font-semibold tracking-wide capitalize">Cargando tablero informativo...</p>
    </div>
  );

  const years = stats ? Object.keys(stats.yearlyStats).sort((a, b) => b - a) : [];
  const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

  return (
    <div className="w-full space-y-8 animate-fade-in pb-12 bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 min-h-screen p-6">
      {/* Encabezado del Tablero */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <PresentationChartLineIcon className="h-8 w-8" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Tablero de Control Operativo</h1>
            <p className="text-gray-500 flex items-center gap-2 mt-1">
              <span className="flex h-2 w-2 rounded-full bg-green-500"></span>
              Última actualización: {new Date().toLocaleTimeString()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 no-print">
          <button
            onClick={() => exportReportStats(stats, `tablero_${new Date().toISOString().split('T')[0]}`)}
            className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 shadow-sm transition-all text-sm"
          >
            <ArrowDownTrayIcon className="h-4 w-4" /> Exportar Datos
          </button>
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 px-6 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-bold hover:bg-gray-50 transition-all text-sm"
          >
            <PrinterIcon className="h-4 w-4" /> Imprimir
          </button>
        </div>
      </div>

      {stats && (
        <>
          {/* Tarjetas de Resumen (KPIs) - Premium Glassmorphism */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'Incidencias Abiertas', val: stats.abiertos, color: 'text-blue-600', bg: 'bg-blue-50', bgGradient: 'from-blue-50 to-indigo-50', icon: ExclamationTriangleIcon },
              { label: 'En Laboratorio', val: stats.laboratorio, color: 'text-purple-600', bg: 'bg-purple-50', bgGradient: 'from-purple-50 to-pink-50', icon: BeakerIcon },
              { label: 'Pendiente Proveedor', val: stats.proveedor, color: 'text-orange-600', bg: 'bg-orange-50', bgGradient: 'from-orange-50 to-amber-50', icon: TruckIcon },
              { label: 'Cerradas Exitosas', val: stats.cerrados, color: 'text-green-600', bg: 'bg-green-50', bgGradient: 'from-emerald-50 to-green-50', icon: CheckCircleIcon }
            ].map((stat, i) => (
              <div key={i} className="group relative bg-white/70 backdrop-blur-sm p-6 rounded-2xl border border-slate-200/60 shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all duration-300 cursor-default">
                {/* Glow effect sutil en hover */}
                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${stat.bgGradient} opacity-0 group-hover:opacity-20 transition-opacity duration-300`}></div>

                <div className="relative flex items-center justify-between mb-4">
                  <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">{stat.label}</p>
                  <div className={`p-2.5 ${stat.bg} ${stat.color} rounded-xl group-hover:scale-110 transition-transform shadow-md`}>
                    <stat.icon className="h-5 w-5" />
                  </div>
                </div>
                <h3 className={`relative text-4xl font-extrabold ${stat.color}`}>{stat.val}</h3>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Gráfico de Eficiencia y Tendencias */}
            <div className="lg:col-span-2 bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
              <div className="flex flex-col sm:flex-row justify-between items-start mb-10 gap-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 border-l-4 border-blue-600 pl-4">Eficiencia de Resolución</h3>
                  <p className="text-sm text-gray-500 mt-1 ml-5">Rendimiento histórico del sistema de postventa</p>
                </div>
                <div className="flex items-center gap-8 pr-4">
                  <div className="text-center">
                    <p className="text-[10px] font-bold text-gray-400 uppercase">Tiempo Promedio</p>
                    <p className="text-2xl font-black text-blue-600">{stats.avgResolutionDays}d</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-bold text-gray-400 uppercase">Tasa de Éxito</p>
                    <p className="text-2xl font-black text-green-600">{stats.resolutionRate}%</p>
                  </div>
                </div>
              </div>

              {/* Barra de progreso de éxito */}
              <div className="relative h-3 w-full bg-gray-100 rounded-full overflow-hidden mb-12 shadow-inner">
                <div
                  className="h-full bg-gradient-to-r from-blue-600 to-green-500 transition-all duration-1000 ease-out"
                  style={{ width: `${stats.resolutionRate}%` }}
                ></div>
              </div>

              {/* Selector de Año y Histograma */}
              <div className="space-y-6">
                <div className="flex justify-between items-center px-2">
                  <h4 className="text-sm font-bold text-gray-700">Flujo Mensual de Casos</h4>
                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(Number(e.target.value))}
                    className="text-sm bg-gray-50 border-gray-200 rounded-lg px-3 py-1.5 font-semibold text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                    {years.map(y => <option key={y} value={y}>{y}</option>)}
                  </select>
                </div>

                <div className="h-48 flex items-end justify-between gap-3 px-2 pt-6">
                  {stats.monthlyStats.map((month, i) => {
                    const max = Math.max(...stats.monthlyStats.map(m => m.total), 1);
                    const h = (month.total / max) * 100;
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center group relative">
                        <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-all bg-gray-900 text-white text-[10px] font-bold px-3 py-1 rounded-lg z-20 whitespace-nowrap shadow-xl">
                          {month.total} Casos
                        </div>
                        <div
                          className="w-full bg-blue-50 group-hover:bg-blue-600 transition-all duration-300 rounded-t-lg relative"
                          style={{ height: `${Math.max(h, 4)}%` }}
                        >
                          <div className="absolute inset-x-0 top-0 h-1 bg-blue-400 group-hover:bg-white/20 rounded-t-lg opacity-40"></div>
                        </div>
                        <span className="text-[10px] font-bold text-gray-400 mt-4 uppercase group-hover:text-blue-600 transition-colors">{months[i]}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Gráfico de Torta Interactivo con Drill-Down */}
            <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-slate-200/60 shadow-lg flex flex-col">
              <InteractivePieChart data={
                Object.entries(stats.categoryTree)
                  .sort((a, b) => b[1].total - a[1].total)
                  .map(([name, data]) => ({
                    name,
                    value: data.total,
                    color: name.includes('LLAVE') || name.includes('TUBERIA') || name.includes('ACCESORIO') ? '#3b82f6' :
                      name.includes('GARANTIA') || name.includes('RECLAMO') ? '#10b981' :
                        name.includes('CONSULTA') || name.includes('INFORMACION') ? '#f59e0b' :
                          name.includes('INSTALACION') ? '#8b5cf6' : '#6366f1',
                    subcategories: Object.entries(data.subcategories)
                      .sort((a, b) => b[1] - a[1])
                      .map(([subName, subCount], idx) => ({
                        name: subName,
                        value: subCount,
                        color: `hsl(${(idx * 30 + 220) % 360}, 70%, ${50 + idx * 5}%)`
                      }))
                  }))
              } />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Ranking de Entidades */}
            <div className="lg:col-span-2 bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
              <h3 className="text-xl font-bold text-gray-900 mb-8 border-l-4 border-indigo-600 pl-4">Ranking Operativo</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                {/* Top Clientes */}
                <div className="space-y-6">
                  <div className="flex items-center gap-2 border-b border-gray-100 pb-3 mb-4">
                    <span className="p-1.5 bg-blue-50 text-blue-600 rounded-lg"><ChartBarIcon className="h-4 w-4" /></span>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Nodos Cliente Top</p>
                  </div>
                  {stats.topClients.map(([client, count], i) => (
                    <div key={client} className="flex items-center gap-4 group">
                      <span className="text-xs font-bold text-gray-300">0{i + 1}</span>
                      <div className="flex-1">
                        <div className="flex justify-between mb-1">
                          <span className="text-xs font-bold text-gray-700 truncate max-w-[180px] capitalize">{client.toLowerCase()}</span>
                          <span className="text-xs font-extrabold text-blue-600">{count}</span>
                        </div>
                        <div className="h-1 w-full bg-gray-50 rounded-full">
                          <div className="h-full bg-blue-200 rounded-full group-hover:bg-blue-500 transition-colors" style={{ width: `${(count / stats.topClients[0][1]) * 100}%` }}></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {/* Top Proveedores */}
                <div className="space-y-6">
                  <div className="flex items-center gap-2 border-b border-gray-100 pb-3 mb-4">
                    <span className="p-1.5 bg-purple-50 text-purple-600 rounded-lg"><TruckIcon className="h-4 w-4" /></span>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Hubs de Proveedor</p>
                  </div>
                  {stats.topProviders.map(([prov, count], i) => (
                    <div key={prov} className="flex items-center gap-4 group">
                      <span className="text-xs font-bold text-gray-300">0{i + 1}</span>
                      <div className="flex-1">
                        <div className="flex justify-between mb-1">
                          <span className="text-xs font-bold text-gray-700 truncate max-w-[180px] capitalize">{prov.toLowerCase()}</span>
                          <span className="text-xs font-extrabold text-purple-600">{count}</span>
                        </div>
                        <div className="h-1 w-full bg-gray-50 rounded-full">
                          <div className="h-full bg-purple-200 rounded-full group-hover:bg-purple-500 transition-colors" style={{ width: `${(count / stats.topProviders[0][1]) * 100}%` }}></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Panel de Acción Estratégica */}
            <div className="bg-gradient-to-br from-gray-900 to-blue-900 p-8 rounded-3xl flex flex-col justify-between text-white shadow-2xl relative overflow-hidden group">
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-3xl group-hover:bg-white/10 transition-all"></div>

              <div className="relative z-10">
                <div className="p-3 bg-white/10 w-fit rounded-2xl mb-6">
                  <ClockIcon className="h-8 w-8 text-blue-300" />
                </div>
                <h3 className="text-2xl font-bold leading-tight mb-4">Registro Operativo de Fidelidad</h3>
                <p className="text-sm text-blue-100/70 leading-relaxed font-medium">Genere archivos operativos de alta fidelidad para revisiones ejecutivas y ajustes de protocolo a largo plazo.</p>
              </div>

              <div className="space-y-5 relative z-10">
                <button
                  onClick={() => exportReportStats(stats, 'registro_operativo_completo')}
                  className="w-full py-4 bg-white text-blue-900 rounded-2xl font-black uppercase tracking-wider hover:bg-blue-50 transition-all active:scale-[0.98] shadow-lg text-xs"
                >
                  EJECUTAR EXPORTACIÓN TOTAL
                </button>
                <div className="flex justify-between items-center opacity-30">
                  <div className="h-px flex-1 bg-white"></div>
                  <span className="px-4 text-[9px] uppercase font-bold tracking-[0.3em]">Sincronización Activa</span>
                  <div className="h-px flex-1 bg-white"></div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ReportsPage;