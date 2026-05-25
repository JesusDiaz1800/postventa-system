import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { visitReportsAPI } from '../services/api';
import {
  ChartBarIcon,
  ArrowPathIcon,
  UserIcon,
  BuildingOfficeIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  MapPinIcon,
  FunnelIcon,
  CalendarIcon,
  XMarkIcon,
  DocumentCheckIcon,
  EnvelopeOpenIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';

export const Dashboard = () => {
  // 1. Fetch ALL reports in a single query for zero-latency interactive slicing
  const { data: rawReports, isLoading, refetch, isRefetching } = useQuery<any[]>({
    queryKey: ['dashboard-all-reports'],
    queryFn: () => visitReportsAPI.list({ page_size: 1000 }).then(res => res.data.results || []),
  });

  // 2. Interactive slicing & filtering states
  const [selectedTech, setSelectedTech] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [selectedCity, setSelectedCity] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  // Helper to clear all active slices
  const handleClearFilters = () => {
    setSelectedTech(null);
    setSelectedProject(null);
    setSelectedCity(null);
    setSelectedStatus(null);
    setStartDate('');
    setEndDate('');
  };

  // 3. Base filtered dataset (filtered by Date, Tech, Project, City/Commune - NOT by status)
  // This is used to compute the correct global KPI tiles counts (Interactive Slicing Style)
  const baseFilteredReports = useMemo(() => {
    if (!rawReports) return [];
    return rawReports.filter((r: any) => {
      // Technician Filter
      if (selectedTech && r.technician !== selectedTech) return false;

      // Project Filter
      if (selectedProject && r.project_name !== selectedProject) return false;

      // City / Commune Filter
      if (selectedCity && r.commune !== selectedCity && r.city !== selectedCity) return false;

      // Date Range Filters
      if (r.visit_date) {
        const vDate = new Date(r.visit_date).getTime();
        if (startDate && vDate < new Date(startDate).getTime()) return false;
        if (endDate && vDate > new Date(endDate).getTime()) return false;
      } else if (startDate || endDate) {
        return false;
      }

      return true;
    });
  }, [rawReports, selectedTech, selectedProject, selectedCity, startDate, endDate]);

  // 3.5 Final filtered dataset applying the KPI Status filter
  // This dataset is used to feed the charts, geographical lists, projects list, and live activity stream
  const filteredReports = useMemo(() => {
    if (!selectedStatus) return baseFilteredReports;
    return baseFilteredReports.filter((r: any) => {
      if (selectedStatus === 'closed') {
        return r.status === 'closed' || r.status === 'sent';
      }
      return r.status === selectedStatus;
    });
  }, [baseFilteredReports, selectedStatus]);

  // 4. Compute KPIs dynamically based on date/tech/project filters but NOT the KPI Status filter itself
  const kpis = useMemo(() => {
    const total = baseFilteredReports.length;
    const pending = baseFilteredReports.filter(r => r.status === 'draft').length;
    const signed = baseFilteredReports.filter(r => r.status === 'approved').length;
    const closed = baseFilteredReports.filter(r => r.status === 'closed' || r.status === 'sent').length;

    return { total, pending, signed, closed };
  }, [baseFilteredReports]);

  // 5. Compute distributions dynamically based on current slice
  const distributions = useMemo(() => {
    const techMap: Record<string, number> = {};
    const cityMap: Record<string, number> = {};
    const projectMap: Record<string, number> = {};
    const trendsMap: Record<string, number> = {};

    filteredReports.forEach((r: any) => {
      // Tech productivity
      if (r.technician) {
        techMap[r.technician] = (techMap[r.technician] || 0) + 1;
      }

      // Geo Distribution
      const geo = r.commune || r.city || 'SANTIAGO';
      cityMap[geo] = (cityMap[geo] || 0) + 1;

      // Top Projects
      if (r.project_name) {
        projectMap[r.project_name] = (projectMap[r.project_name] || 0) + 1;
      }

      // Trends (Format date to DD/MM)
      if (r.visit_date) {
        const dateStr = new Date(r.visit_date).toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit' });
        trendsMap[dateStr] = (trendsMap[dateStr] || 0) + 1;
      }
    });

    // Format for charts
    const byTech = Object.entries(techMap)
      .map(([name, count]) => ({ name: name.split(' ')[0], fullName: name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6);

    const byCity = Object.entries(cityMap)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    const byProject = Object.entries(projectMap)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 6);

    const trends = Object.entries(trendsMap)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => {
        const [dayA, monthA] = a.date.split('/');
        const [dayB, monthB] = b.date.split('/');
        return new Date(2026, parseInt(monthA) - 1, parseInt(dayA)).getTime() - new Date(2026, parseInt(monthB) - 1, parseInt(dayB)).getTime();
      });

    return { byTech, byCity, byProject, trends };
  }, [filteredReports]);

  // Recent activity stream (show up to 50 entries scrollable under selection)
  const recentActivity = useMemo(() => {
    return filteredReports.slice(0, 50);
  }, [filteredReports]);

  // Active filters list for chips visualization
  const activeFilters = useMemo(() => {
    const list = [];
    if (selectedTech) list.push({ label: `Técnico: ${selectedTech}`, type: 'tech' });
    if (selectedProject) list.push({ label: `Obra: ${selectedProject}`, type: 'project' });
    if (selectedCity) list.push({ label: `Comuna: ${selectedCity}`, type: 'city' });
    if (selectedStatus) {
      let statusLabel = '';
      if (selectedStatus === 'draft') statusLabel = 'Pendientes';
      else if (selectedStatus === 'approved') statusLabel = 'Firmadas';
      else if (selectedStatus === 'closed') statusLabel = 'Cerradas';
      list.push({ label: `Estado: ${statusLabel}`, type: 'status' });
    }
    if (startDate) list.push({ label: `Desde: ${startDate}`, type: 'startDate' });
    if (endDate) list.push({ label: `Hasta: ${endDate}`, type: 'endDate' });
    return list;
  }, [selectedTech, selectedProject, selectedCity, selectedStatus, startDate, endDate]);

  if (isLoading) {
    return (
      <div className="h-full w-full bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 animate-fade-in">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-blue-500/10 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
          </div>
          <p className="text-xs font-black text-slate-500 uppercase tracking-widest animate-pulse">Cargando Panel de Control Sertec...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-transparent h-full w-full text-slate-800 p-4 lg:p-5 flex flex-col gap-4 lg:overflow-hidden overflow-y-auto select-none animate-in fade-in duration-500">
      
      {/* HEADER BAR */}
      <div className="bg-white/60 backdrop-blur-md px-5 py-3 lg:py-3.5 rounded-[2rem] border border-white/60 shadow-lg flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 shrink-0 hover:shadow-xl transition-all duration-300">
        <div className="flex items-center gap-4">
          <div className="bg-gradient-to-tr from-blue-600 to-indigo-600 p-2.5 rounded-2xl shadow-lg shadow-blue-200/50">
            <ChartBarIcon className="h-6 w-6 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl lg:text-2xl font-black text-slate-900 tracking-tight leading-none flex items-center gap-2">
              Panel de Control <span className="text-blue-600">Sertec</span>
              <SparklesIcon className="w-5 h-5 text-cyan-500" />
            </h1>
            <p className="text-[9px] lg:text-[10px] font-bold text-slate-400 uppercase tracking-[0.25em] mt-1">
              Indicadores Técnicos y Métricas en Tiempo Real
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto">
          {/* Quick Date Inputs */}
          <div className="flex items-center gap-2 bg-slate-50/80 border border-slate-200/60 rounded-2xl p-1.5 shadow-inner">
            <CalendarIcon className="w-4 h-4 text-slate-400 ml-1.5" />
            <input 
              type="date" 
              value={startDate}
              onChange={e => setStartDate(e.target.value)}
              className="bg-transparent border-none text-[10px] font-bold text-slate-650 focus:ring-0 outline-none p-0 w-24"
              placeholder="Desde"
            />
            <span className="text-slate-300 text-xs font-bold">/</span>
            <input 
              type="date" 
              value={endDate}
              onChange={e => setEndDate(e.target.value)}
              className="bg-transparent border-none text-[10px] font-bold text-slate-650 focus:ring-0 outline-none p-0 w-24"
              placeholder="Hasta"
            />
          </div>

          <button 
            onClick={() => refetch()} 
            disabled={isRefetching}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 hover:bg-black text-white rounded-2xl text-xs font-black uppercase tracking-widest hover:scale-[1.02] active:scale-[0.98] transition-all shadow-md shrink-0"
          >
            <ArrowPathIcon className={`w-3.5 h-3.5 ${isRefetching ? 'animate-spin' : ''}`} />
            Sincronizar
          </button>
        </div>
      </div>

      {/* FILTER NOTIFICATIONS BAR */}
      {activeFilters.length > 0 && (
        <div className="bg-blue-50/80 backdrop-blur-sm border border-blue-100 rounded-2xl px-4 py-2 flex flex-wrap items-center justify-between gap-4 animate-fadeIn shadow-sm shrink-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[9px] font-black text-blue-800 uppercase tracking-widest flex items-center gap-1.5">
              <FunnelIcon className="w-3.5 h-3.5 text-blue-600" />
              Slices Activos ({activeFilters.length}):
            </span>
            {activeFilters.map(filter => (
              <span 
                key={filter.label} 
                className="inline-flex items-center gap-1 bg-white border border-blue-200/60 px-2.5 py-0.5 rounded-full text-[9px] font-bold text-blue-700 shadow-sm"
              >
                {filter.label}
                <button 
                  onClick={() => {
                    if (filter.type === 'tech') setSelectedTech(null);
                    if (filter.type === 'project') setSelectedProject(null);
                    if (filter.type === 'city') setSelectedCity(null);
                    if (filter.type === 'status') setSelectedStatus(null);
                    if (filter.type === 'startDate') setStartDate('');
                    if (filter.type === 'endDate') setEndDate('');
                  }}
                  className="hover:text-rose-500 rounded-full transition-all"
                >
                  <XMarkIcon className="w-2.5 h-2.5" />
                </button>
              </span>
            ))}
          </div>

          <button 
            onClick={handleClearFilters}
            className="text-[9px] font-black text-rose-600 hover:text-rose-700 bg-white border border-rose-100 px-3 py-1.5 rounded-xl uppercase tracking-wider hover:bg-rose-50 transition-all shadow-sm flex items-center gap-1 shrink-0"
          >
            <XMarkIcon className="w-3.5 h-3.5" />
            Restablecer
          </button>
        </div>
      )}

      {/* KPI TILES */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 shrink-0">
        <KPITile 
          title="TOTAL VISITAS" 
          value={kpis.total} 
          subtitle="En el periodo filtrado" 
          icon={<ChartBarIcon className="w-5 h-5" />} 
          isActive={selectedStatus === null}
          onClick={() => setSelectedStatus(null)}
          theme="blue"
        />
        <KPITile 
          title="VISITAS PENDIENTES" 
          value={kpis.pending} 
          subtitle="Planificadas en borrador" 
          icon={<ClockIcon className="w-5 h-5" />} 
          isActive={selectedStatus === 'draft'}
          onClick={() => setSelectedStatus(prev => prev === 'draft' ? null : 'draft')}
          theme="amber"
        />
        <KPITile 
          title="VISITAS FIRMADAS" 
          value={kpis.signed} 
          subtitle="Aprobadas por el cliente" 
          icon={<DocumentCheckIcon className="w-5 h-5" />} 
          isActive={selectedStatus === 'approved'}
          onClick={() => setSelectedStatus(prev => prev === 'approved' ? null : 'approved')}
          theme="emerald"
        />
        <KPITile 
          title="VISITAS CERRADAS" 
          value={kpis.closed} 
          subtitle="Sincronizadas y enviadas" 
          icon={<EnvelopeOpenIcon className="w-5 h-5" />} 
          isActive={selectedStatus === 'closed'}
          onClick={() => setSelectedStatus(prev => prev === 'closed' ? null : 'closed')}
          theme="violet"
        />
      </div>

      {/* INSIGHTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1 min-h-0 lg:overflow-hidden">
        
        {/* LEFT COLUMN: VISUALIZATIONS */}
        <div className="lg:col-span-8 flex flex-col gap-4 h-full min-h-0 lg:overflow-hidden">
          
          {/* AREA CHART - VISITS FLUX */}
          <VisualCard title="Fluctuación y Tendencia de Visitas" className="flex-1 min-h-0">
            <div className="flex-1 min-h-0 w-full mt-2 relative">
              {distributions.trends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={distributions.trends} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorVisits" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25}/>
                        <stop offset="95%" stopColor="#2563eb" stopOpacity={0.01}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" strokeOpacity={0.4} />
                    <XAxis dataKey="date" tick={{fontSize: 9, fill: '#64748b', fontWeight: 600}} axisLine={{stroke: '#e2e8f0'}} tickLine={false} />
                    <YAxis tick={{fontSize: 9, fill: '#64748b', fontWeight: 600}} axisLine={false} tickLine={false} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="count" name="Visitas" stroke="#2563eb" strokeWidth={2.5} fillOpacity={1} fill="url(#colorVisits)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs font-bold text-slate-400 italic">
                  Sin datos de tendencia en el periodo
                </div>
              )}
            </div>
          </VisualCard>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-[210px] shrink-0 min-h-0">
            
            {/* BAR CHART - TECHNICIANS */}
            <VisualCard title="Productividad de Técnicos">
              <div className="flex-1 min-h-0 w-full mt-2 relative">
                {distributions.byTech.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distributions.byTech} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                      <XAxis dataKey="name" tick={{fontSize: 8, fontWeight: 700, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <YAxis tick={{fontSize: 8, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <Tooltip content={<CustomTooltip />} cursor={{fill: 'rgba(59, 130, 246, 0.03)', radius: 8}} />
                      <Bar dataKey="count" name="Visitas" fill="#3b82f6" radius={[6, 6, 0, 0]}>
                        {distributions.byTech.map((entry, index) => {
                          const isSelected = selectedTech === entry.fullName;
                          const hasSelection = selectedTech !== null;
                          return (
                            <Cell 
                              key={`cell-${index}`} 
                              cursor="pointer"
                              fill={isSelected ? '#1d4ed8' : hasSelection ? '#cbd5e1' : '#3b82f6'}
                              onClick={() => setSelectedTech(prev => prev === entry.fullName ? null : entry.fullName)}
                              className="transition-all duration-300 hover:opacity-85"
                            />
                          );
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-xs font-bold text-slate-400 italic">
                    Sin registros de técnicos
                  </div>
                )}
              </div>
            </VisualCard>

            {/* INTERACTIVE GEOGRAPHY LIST */}
            <VisualCard title="Distribución Geográfica">
              <div className="flex flex-col gap-2 mt-1 flex-1 overflow-y-auto pr-1 dashboard-scrollbar">
                {distributions.byCity.length > 0 ? (
                  distributions.byCity.map((c) => {
                    const isSelected = selectedCity === c.name;
                    const hasSelection = selectedCity !== null;
                    return (
                      <div 
                        key={c.name}
                        onClick={() => setSelectedCity(prev => prev === c.name ? null : c.name)}
                        className={`p-2 px-3 rounded-2xl cursor-pointer transition-all border flex flex-col gap-1.5 ${
                          isSelected 
                            ? 'bg-blue-50/80 border-blue-200/80 shadow-md translate-x-1' 
                            : hasSelection
                              ? 'bg-white/30 border-transparent opacity-50 hover:opacity-100 hover:bg-white hover:border-slate-200/60'
                              : 'bg-white/70 border-slate-100/30 hover:bg-white hover:border-slate-200/60 hover:shadow-md'
                        }`}
                      >
                        <div className="flex justify-between items-center text-[10px] font-bold">
                          <span className={`uppercase flex items-center gap-1.5 ${isSelected ? 'text-blue-700 font-extrabold' : 'text-slate-650'}`}>
                            <MapPinIcon className={`w-3.5 h-3.5 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                            {c.name}
                          </span>
                          <span className={isSelected ? 'text-blue-750 font-black' : 'text-slate-800 font-black'}>{c.count}</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-500 bg-gradient-to-r ${isSelected ? 'from-blue-600 to-indigo-600' : 'from-blue-550 to-indigo-550'}`} 
                            style={{ width: `${(c.count / (distributions.byCity[0]?.count || 1)) * 100}%` }} 
                          />
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="h-full flex items-center justify-center text-xs font-bold text-slate-400 italic">
                    Sin registros geográficos
                  </div>
                )}
              </div>
            </VisualCard>

          </div>
        </div>

        {/* RIGHT COLUMN: LISTS & ACTIVITIES */}
        <div className="lg:col-span-4 flex flex-col gap-4 h-full min-h-0 lg:overflow-hidden">
          
          {/* TOP OBRAS / PROJECTS */}
          <VisualCard title="Obras y Proyectos" className="h-[210px] shrink-0">
            <div className="flex flex-col gap-1.5 mt-1 flex-1 overflow-y-auto pr-1 dashboard-scrollbar">
              {distributions.byProject.length > 0 ? (
                distributions.byProject.map((p) => {
                  const isSelected = selectedProject === p.name;
                  const hasSelection = selectedProject !== null;
                  return (
                    <div 
                      key={p.name}
                      onClick={() => setSelectedProject(prev => prev === p.name ? null : p.name)}
                      className={`flex items-center justify-between p-2.5 px-3.5 rounded-2xl cursor-pointer transition-all border ${
                        isSelected 
                          ? 'bg-blue-50/80 border-blue-200/80 shadow-md translate-x-1' 
                          : hasSelection
                            ? 'bg-white/30 border-transparent opacity-50 hover:opacity-100 hover:bg-white hover:border-slate-200/60'
                            : 'bg-white/60 hover:bg-white border-slate-100/30 hover:border-slate-200/60 hover:shadow-md'
                      }`}
                    >
                      <div className="flex flex-col min-w-0">
                        <span className={`text-[10px] font-black uppercase truncate ${isSelected ? 'text-blue-700' : 'text-slate-800'}`}>
                          {p.name}
                        </span>
                        <span className="text-[8px] text-slate-400 font-bold uppercase tracking-wider">Reportes</span>
                      </div>
                      <span className={`text-[9px] font-black px-2.5 py-0.5 rounded-full border transition-all ${
                        isSelected ? 'bg-blue-200/85 text-blue-800 border-blue-300' : 'bg-slate-100 border-slate-200/30 text-slate-655'
                      }`}>{p.count}</span>
                    </div>
                  );
                })
              ) : (
                <div className="h-full flex items-center justify-center text-xs font-bold text-slate-400 italic">
                  Sin proyectos registrados en el filtro
                </div>
              )}
            </div>
          </VisualCard>

          {/* DETALLES DE VISITAS BAJO SELECCIÓN PANEL */}
          <VisualCard 
            title={`Visitas bajo Selección (${recentActivity.length})`}
            subtitle={filteredReports.length > 50 ? `50 de ${filteredReports.length}` : `Todas`}
            className="flex-1 min-h-0"
          >
            <div className="flex flex-col gap-2.5 mt-1 flex-1 overflow-y-auto pr-1 dashboard-scrollbar">
              {recentActivity.length > 0 ? (
                recentActivity.map((r) => {
                  let statusBg = 'bg-slate-100 text-slate-655 border-slate-200/60';
                  let statusLabel = 'Abierto';
                  
                  if (r.status === 'draft') {
                    statusBg = 'bg-amber-50/80 text-amber-700 border-amber-200/50';
                    statusLabel = 'Pendiente';
                  } else if (r.status === 'approved') {
                    statusBg = 'bg-emerald-50/80 text-emerald-700 border-emerald-200/50';
                    statusLabel = 'Firmado';
                  } else if (r.status === 'closed' || r.status === 'sent') {
                    statusBg = 'bg-indigo-50/80 text-indigo-700 border-indigo-200/50';
                    statusLabel = 'Cerrado';
                  }

                  return (
                    <a 
                      key={r.id} 
                      href={`/visit-reports?id=${r.id}`}
                      className="group border border-slate-100/40 hover:border-blue-200/80 pl-4 pr-3.5 py-3 bg-white/70 hover:bg-white rounded-2xl transition-all duration-300 shadow-sm hover:shadow-md flex flex-col gap-1.5 relative overflow-hidden block shrink-0"
                    >
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-slate-200 group-hover:bg-blue-650 transition-all duration-300 animate-pulse" />
                      
                      <div className="flex justify-between items-start gap-2 min-w-0">
                        <div className="flex flex-col min-w-0">
                          <span className="text-[9px] font-black text-blue-700 tracking-tight leading-none mb-1">
                            {r.report_number || `RV-${r.id}`}
                          </span>
                          <h4 className="text-[10px] font-extrabold text-slate-800 uppercase tracking-tight line-clamp-1 leading-tight group-hover:text-blue-900 transition-colors">
                            {r.client_name}
                          </h4>
                          {r.project_name && (
                            <span className="text-[8px] text-slate-400 font-bold uppercase truncate mt-0.5">
                              {r.project_name}
                            </span>
                          )}
                        </div>
                        <span className="text-[8px] font-extrabold text-slate-400 shrink-0 bg-white border border-slate-100 px-1.5 py-0.5 rounded-md">
                          {r.visit_date ? new Date(r.visit_date).toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit' }) : '—'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between gap-4 mt-1 border-t border-slate-200/30 pt-1.5">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <UserIcon className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="text-[8.5px] font-extrabold text-slate-500 uppercase truncate">
                            {r.technician || 'Sin Asignar'}
                          </span>
                        </div>
                        <span className={`text-[7.5px] font-black px-2 py-0.5 rounded-full border uppercase tracking-wider shrink-0 ${statusBg}`}>
                          {statusLabel}
                        </span>
                      </div>
                    </a>
                  );
                })
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 italic gap-2 py-6">
                  <span className="text-xs font-bold">Sin visitas en esta selección</span>
                  <p className="text-[9px] uppercase tracking-widest text-slate-450">Limpia filtros para ver más</p>
                </div>
              )}
            </div>
            <div className="mt-2 border-t border-slate-100/50 pt-2 shrink-0">
              <a href="/visit-reports" className="text-[9px] font-black text-blue-600 hover:text-blue-700 flex items-center justify-center gap-1.5 uppercase tracking-widest hover:underline transition-colors">
                Historial Completo <ArrowTrendingUpIcon className="w-3 h-3" />
              </a>
            </div>
          </VisualCard>

        </div>

      </div>

    </div>
  );
};

// Custom Glassmorphic Tooltip for Recharts
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/80 backdrop-blur-md border border-slate-200/50 p-2.5 px-3.5 rounded-2xl shadow-xl flex flex-col gap-1 animate-in fade-in duration-200 select-none">
        <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">{label}</p>
        <p className="text-xs font-black text-blue-600 flex items-center gap-1.5">
          <span>Visitas:</span>
          <span className="text-slate-900 text-sm font-black">{payload[0].value}</span>
        </p>
      </div>
    );
  }
  return null;
};

// Premium Glassmorphic KPITile Component Theme Configuration
const themeMap: Record<string, {
  accent: string;
  gradient: string;
  bgGlow: string;
  bgLight: string;
  borderActive: string;
  textActive: string;
  badge: string;
  shadow: string;
}> = {
  blue: {
    accent: 'bg-blue-600',
    gradient: 'from-blue-600 to-indigo-600',
    bgGlow: 'bg-blue-500/10',
    bgLight: 'bg-blue-50 text-blue-650',
    borderActive: 'border-blue-200/80',
    textActive: 'text-blue-950',
    badge: 'bg-blue-600',
    shadow: 'shadow-blue-100/40 hover:shadow-blue-200/50'
  },
  amber: {
    accent: 'bg-amber-650',
    gradient: 'from-amber-500 to-orange-500',
    bgGlow: 'bg-amber-550/10',
    bgLight: 'bg-amber-50 text-amber-650',
    borderActive: 'border-amber-200/80',
    textActive: 'text-amber-950',
    badge: 'bg-amber-600',
    shadow: 'shadow-amber-100/40 hover:shadow-amber-200/50'
  },
  emerald: {
    accent: 'bg-emerald-600',
    gradient: 'from-emerald-500 to-teal-600',
    bgGlow: 'bg-emerald-550/10',
    bgLight: 'bg-emerald-50 text-emerald-650',
    borderActive: 'border-emerald-200/80',
    textActive: 'text-emerald-950',
    badge: 'bg-emerald-600',
    shadow: 'shadow-emerald-100/40 hover:shadow-emerald-200/50'
  },
  violet: {
    accent: 'bg-indigo-600',
    gradient: 'from-indigo-500 to-purple-600',
    bgGlow: 'bg-indigo-550/10',
    bgLight: 'bg-indigo-50 text-indigo-650',
    borderActive: 'border-indigo-200/80',
    textActive: 'text-indigo-950',
    badge: 'bg-indigo-600',
    shadow: 'shadow-indigo-100/40 hover:shadow-indigo-200/50'
  }
};

const KPITile = ({ title, value, subtitle, icon, isActive, onClick, theme = 'blue' }: any) => {
  const t = themeMap[theme] || themeMap.blue;
  return (
    <button 
      onClick={onClick}
      className={`w-full text-left p-4 rounded-[2rem] border transition-all duration-300 transform flex items-center gap-4 cursor-pointer focus:outline-none relative overflow-hidden group select-none ${
        isActive 
          ? `bg-white border-slate-300 shadow-xl scale-[1.015] -translate-y-0.5 ${t.shadow}` 
          : `bg-white/60 backdrop-blur-md hover:bg-white border-white/50 hover:border-slate-300 hover:shadow-lg hover:-translate-y-0.5 shadow-sm`
      }`}
    >
      {/* Top Active Indicator Glow Bar */}
      {isActive && (
        <div className={`absolute top-0 left-0 right-0 h-[4px] bg-gradient-to-r ${t.gradient}`} />
      )}
      
      {/* Active Small Badge in corner */}
      {isActive && (
        <div className={`absolute top-0 right-0 ${t.badge} text-[7px] font-black uppercase text-white tracking-widest px-2.5 py-0.5 rounded-bl-xl shadow-md`}>
          Filtro
        </div>
      )}

      {/* Decorative background light circles */}
      <div className={`absolute -right-8 -bottom-8 w-20 h-20 rounded-full transition-all duration-700 ease-out opacity-0 group-hover:opacity-10 group-hover:scale-150 ${t.accent}`} />

      {/* Icon frame with dynamic colors and animations */}
      <div className={`p-3 rounded-2xl shadow-sm transition-all duration-300 flex items-center justify-center shrink-0 ${
        isActive 
          ? `${t.bgLight} scale-105 shadow-md shadow-slate-100` 
          : 'bg-slate-50 text-slate-400 group-hover:scale-105 group-hover:bg-white group-hover:shadow-md'
      }`}>
        {icon}
      </div>

      <div className="min-w-0 flex-1 relative z-10">
        <p className={`text-[8.5px] font-black uppercase tracking-[0.15em] leading-none mb-2 ${
          isActive ? 'text-slate-500' : 'text-slate-400'
        }`}>
          {title}
        </p>
        <h3 className="text-2xl lg:text-3xl font-black text-slate-900 leading-none mb-1 tracking-tight group-hover:text-black transition-colors">
          {value}
        </h3>
        <p className={`text-[8px] font-extrabold truncate leading-none ${
          isActive ? 'text-slate-600' : 'text-slate-400/70'
        }`}>
          {subtitle}
        </p>
      </div>
    </button>
  );
};

// Premium Stitch 2.0 VisualCard
const VisualCard = ({ title, subtitle, children, className = '' }: any) => (
  <div className={`bg-white/60 backdrop-blur-md p-4 lg:p-5 rounded-[2rem] border border-white/60 shadow-md flex flex-col min-h-0 hover:shadow-xl transition-all duration-300 ${className}`}>
    <div className="flex items-center justify-between gap-2 mb-3 border-b border-slate-100 pb-2.5 shrink-0">
      <div className="flex items-center gap-2">
        <div className="w-1.5 h-3.5 bg-gradient-to-b from-blue-500 to-indigo-600 rounded-full" />
        <h3 className="text-[10px] font-black text-slate-800 uppercase tracking-[0.15em] leading-none">{title}</h3>
      </div>
      {subtitle && (
        <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-100">{subtitle}</span>
      )}
    </div>
    {children}
  </div>
);

export default Dashboard;
