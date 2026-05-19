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
  // This is used to compute the correct global KPI tiles counts (Power BI Style)
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
      <div className="h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-blue-500/10 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
          </div>
          <p className="text-xs font-black text-slate-500 uppercase tracking-widest animate-pulse">Cargando Power BI Sertec...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-100 min-h-screen text-slate-800 p-4 lg:p-6 flex flex-col gap-6 overflow-x-hidden">
      
      {/* POWER BI HEADER BAR */}
      <div className="bg-white/80 backdrop-blur-md px-6 py-4 rounded-2xl border border-white/60 shadow-xl flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
        <div className="flex items-center gap-4">
          <div className="bg-blue-600 p-3 rounded-xl shadow-lg shadow-blue-200">
            <ChartBarIcon className="h-7 w-7 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight leading-none flex items-center gap-2">
              PowerBI <span className="text-blue-600">Sertec 2.0</span>
              <SparklesIcon className="w-5 h-5 text-cyan-500" />
            </h1>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.25em] mt-1">
              Dashboard de Inteligencia Interactivo en Tiempo Real
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 w-full lg:w-auto">
          {/* Quick Date Inputs */}
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl p-1.5 shadow-sm">
            <CalendarIcon className="w-4 h-4 text-slate-400 ml-1.5" />
            <input 
              type="date" 
              value={startDate}
              onChange={e => setStartDate(e.target.value)}
              className="bg-transparent border-none text-[10px] font-bold text-slate-600 focus:ring-0 outline-none p-0 w-24"
              placeholder="Desde"
            />
            <span className="text-slate-300 text-xs font-bold">/</span>
            <input 
              type="date" 
              value={endDate}
              onChange={e => setEndDate(e.target.value)}
              className="bg-transparent border-none text-[10px] font-bold text-slate-600 focus:ring-0 outline-none p-0 w-24"
              placeholder="Hasta"
            />
          </div>

          <button 
            onClick={() => refetch()} 
            disabled={isRefetching}
            className="flex items-center gap-2 px-4 py-2.5 bg-slate-800 text-white rounded-xl text-xs font-black uppercase tracking-wider hover:bg-black transition-all shadow-sm"
          >
            <ArrowPathIcon className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
            Sincronizar
          </button>
        </div>
      </div>

      {/* FILTER NOTIFICATIONS BAR */}
      {activeFilters.length > 0 && (
        <div className="bg-blue-50 border border-blue-100 rounded-2xl px-5 py-3 flex flex-wrap items-center justify-between gap-4 animate-fadeIn shadow-sm">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-black text-blue-800 uppercase tracking-widest flex items-center gap-1.5">
              <FunnelIcon className="w-3.5 h-3.5 text-blue-600" />
              Slices Activos ({activeFilters.length}):
            </span>
            {activeFilters.map(filter => (
              <span 
                key={filter.label} 
                className="inline-flex items-center gap-1 bg-white border border-blue-200 px-3 py-1 rounded-full text-[10px] font-bold text-blue-700 shadow-sm"
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
                  <XMarkIcon className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>

          <button 
            onClick={handleClearFilters}
            className="text-[10px] font-black text-rose-600 hover:text-rose-700 bg-white border border-rose-100 px-3.5 py-1.5 rounded-xl uppercase tracking-wider hover:bg-rose-50 transition-all shadow-sm flex items-center gap-1"
          >
            <XMarkIcon className="w-3.5 h-3.5" />
            Restablecer Filtros
          </button>
        </div>
      )}

      {/* KPI TILES (Click p/ Filtrar) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPITile 
          title="TOTAL VISITAS" 
          value={kpis.total} 
          subtitle="En el periodo filtrado" 
          icon={<ChartBarIcon className="w-5.5 h-5.5 text-blue-600" />} 
          isActive={selectedStatus === null}
          onClick={() => setSelectedStatus(null)}
          activeColor="border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50/20 text-blue-900 shadow-blue-100/50" 
          baseColor="border-slate-200"
        />
        <KPITile 
          title="VISITAS PENDIENTES" 
          value={kpis.pending} 
          subtitle="Planificadas en borrador" 
          icon={<ClockIcon className="w-5.5 h-5.5 text-amber-600" />} 
          isActive={selectedStatus === 'draft'}
          onClick={() => setSelectedStatus(prev => prev === 'draft' ? null : 'draft')}
          activeColor="border-amber-500 bg-gradient-to-br from-amber-50 to-yellow-50/20 text-amber-900 shadow-amber-100/50" 
          baseColor="border-slate-200"
        />
        <KPITile 
          title="VISITAS FIRMADAS" 
          value={kpis.signed} 
          subtitle="Aprobadas por el cliente" 
          icon={<DocumentCheckIcon className="w-5.5 h-5.5 text-emerald-600" />} 
          isActive={selectedStatus === 'approved'}
          onClick={() => setSelectedStatus(prev => prev === 'approved' ? null : 'approved')}
          activeColor="border-emerald-500 bg-gradient-to-br from-emerald-50 to-teal-50/20 text-emerald-900 shadow-emerald-100/50" 
          baseColor="border-slate-200"
        />
        <KPITile 
          title="VISITAS CERRADAS" 
          value={kpis.closed} 
          subtitle="Sincronizadas y enviadas" 
          icon={<EnvelopeOpenIcon className="w-5.5 h-5.5 text-indigo-600" />} 
          isActive={selectedStatus === 'closed'}
          onClick={() => setSelectedStatus(prev => prev === 'closed' ? null : 'closed')}
          activeColor="border-indigo-500 bg-gradient-to-br from-indigo-50 to-purple-50/20 text-indigo-900 shadow-indigo-100/50" 
          baseColor="border-slate-200"
        />
      </div>

      {/* INTERACTIVE INSIGHTS ROW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* LEFT COLUMN: VISUALIZATIONS */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          
          {/* AREA CHART - VISITS FLUX */}
          <VisualCard title="Fluctuación y Tendencia de Visitas">
            <div className="h-[260px] w-full mt-2">
              {distributions.trends.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={distributions.trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorVisits" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{fontSize: 9, fill: '#64748b', fontWeight: 600}} axisLine={{stroke: '#cbd5e1'}} tickLine={false} />
                    <YAxis tick={{fontSize: 9, fill: '#64748b', fontWeight: 600}} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{fontSize: '11px', border: '1px solid #e2e8f0', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)'}} />
                    <Area type="monotone" dataKey="count" name="Visitas" stroke="#2563eb" strokeWidth={3} fillOpacity={1} fill="url(#colorVisits)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs font-bold text-slate-400 italic">
                  Sin datos de tendencia en el periodo
                </div>
              )}
            </div>
          </VisualCard>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* BAR CHART - TECHNICIANS */}
            <VisualCard title="Productividad de Técnicos (Click p/ Filtrar)">
              <div className="h-[210px] w-full mt-2">
                {distributions.byTech.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distributions.byTech} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <XAxis dataKey="name" tick={{fontSize: 9, fontWeight: 700, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <YAxis tick={{fontSize: 9, fill: '#64748b'}} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{fontSize: '10px', borderRadius: '8px'}} cursor={{fill: '#f8fafc'}} />
                      <Bar dataKey="count" name="Visitas" fill="#93c5fd" radius={[6, 6, 0, 0]}>
                        {distributions.byTech.map((entry, index) => {
                          const isSelected = selectedTech === entry.fullName;
                          const hasSelection = selectedTech !== null;
                          return (
                            <Cell 
                              key={`cell-${index}`} 
                              cursor="pointer"
                              fill={isSelected ? '#2563eb' : hasSelection ? '#e2e8f0' : '#93c5fd'}
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
            <VisualCard title="Distribución Geográfica (Click p/ Filtrar)">
              <div className="flex flex-col gap-2.5 mt-2 h-[210px] overflow-y-auto pr-1">
                {distributions.byCity.length > 0 ? (
                  distributions.byCity.map((c) => {
                    const isSelected = selectedCity === c.name;
                    const hasSelection = selectedCity !== null;
                    return (
                      <div 
                        key={c.name}
                        onClick={() => setSelectedCity(prev => prev === c.name ? null : c.name)}
                        className={`p-2.5 rounded-xl cursor-pointer transition-all border flex flex-col gap-1.5 ${
                          isSelected 
                            ? 'bg-blue-50 border-blue-200 shadow-sm' 
                            : hasSelection
                              ? 'bg-white/40 border-slate-100 opacity-60 hover:opacity-100 hover:bg-slate-50'
                              : 'bg-white border-slate-100 hover:bg-slate-50 hover:shadow-sm'
                        }`}
                      >
                        <div className="flex justify-between items-center text-xs font-bold">
                          <span className={`uppercase flex items-center gap-1.5 ${isSelected ? 'text-blue-700' : 'text-slate-700'}`}>
                            <MapPinIcon className={`w-3.5 h-3.5 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                            {c.name}
                          </span>
                          <span className={isSelected ? 'text-blue-700 font-extrabold' : 'text-slate-600 font-extrabold'}>{c.count}</span>
                        </div>
                        <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all duration-500 ${isSelected ? 'bg-blue-600' : 'bg-blue-400'}`} 
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
        <div className="lg:col-span-4 flex flex-col gap-6">
          
          {/* TOP OBRAS / PROJECTS */}
          <VisualCard title="Obras y Proyectos (Click p/ Filtrar)">
            <div className="flex flex-col gap-2 mt-2 h-[260px] overflow-y-auto pr-1">
              {distributions.byProject.length > 0 ? (
                distributions.byProject.map((p) => {
                  const isSelected = selectedProject === p.name;
                  const hasSelection = selectedProject !== null;
                  return (
                    <div 
                      key={p.name}
                      onClick={() => setSelectedProject(prev => prev === p.name ? null : p.name)}
                      className={`flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all border ${
                        isSelected 
                          ? 'bg-blue-50 border-blue-200 shadow-sm' 
                          : hasSelection
                            ? 'bg-white/40 border-transparent opacity-60 hover:opacity-100 hover:border-slate-100 hover:bg-slate-50'
                            : 'hover:bg-slate-50 border-transparent hover:border-slate-100 hover:shadow-sm'
                      }`}
                    >
                      <div className="flex flex-col min-w-0">
                        <span className={`text-[11px] font-black uppercase truncate ${isSelected ? 'text-blue-700' : 'text-slate-800'}`}>
                          {p.name}
                        </span>
                        <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Reportes Asociados</span>
                      </div>
                      <span className={`text-[10px] font-black px-2.5 py-1 rounded-full transition-all ${
                        isSelected ? 'bg-blue-200 text-blue-800 border border-blue-300' : 'bg-slate-100 text-slate-600'
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

          {/* DETALLES DE VISITAS BAJO SELECCIÓN PANEL (Power BI Detail Pane) */}
          <VisualCard 
            title={`Visitas bajo Selección (${recentActivity.length})`}
            subtitle={filteredReports.length > 50 ? `Mostrando 50 de ${filteredReports.length}` : `Mostrando todas`}
          >
            <div className="flex flex-col gap-3 mt-2 h-[210px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-200">
              {recentActivity.length > 0 ? (
                recentActivity.map((r) => {
                  let statusBg = 'bg-slate-100 text-slate-600 border-slate-200';
                  let statusLabel = 'Abierto';
                  
                  if (r.status === 'draft') {
                    statusBg = 'bg-amber-50 text-amber-700 border-amber-200';
                    statusLabel = 'Pendiente';
                  } else if (r.status === 'approved') {
                    statusBg = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                    statusLabel = 'Firmado';
                  } else if (r.status === 'closed' || r.status === 'sent') {
                    statusBg = 'bg-indigo-50 text-indigo-700 border-indigo-200';
                    statusLabel = 'Cerrado';
                  }

                  return (
                    <a 
                      key={r.id} 
                      href={`/visit-reports?id=${r.id}`}
                      className="group border border-slate-100 hover:border-blue-200 pl-3.5 pr-2.5 py-3 bg-slate-50 hover:bg-gradient-to-r hover:from-white hover:to-blue-50/10 rounded-xl transition-all duration-300 shadow-sm hover:shadow flex flex-col gap-1 relative overflow-hidden block"
                    >
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-slate-300 group-hover:bg-blue-600 transition-all duration-300" />
                      
                      <div className="flex justify-between items-start gap-2 min-w-0">
                        <div className="flex flex-col min-w-0">
                          <span className="text-[10px] font-black text-blue-700 tracking-tight leading-none mb-1">
                            {r.report_number || `RV-${r.id}`}
                          </span>
                          <h4 className="text-[11px] font-extrabold text-slate-800 uppercase tracking-tight line-clamp-1 leading-tight group-hover:text-blue-900 transition-colors">
                            {r.client_name}
                          </h4>
                          {r.project_name && (
                            <span className="text-[9px] text-slate-400 font-bold uppercase truncate mt-0.5">
                              Obra: {r.project_name}
                            </span>
                          )}
                        </div>
                        <span className="text-[8px] font-extrabold text-slate-400 shrink-0 bg-white border border-slate-100 px-2 py-0.5 rounded-md">
                          {r.visit_date ? new Date(r.visit_date).toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit' }) : '—'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between gap-4 mt-1 border-t border-slate-200/50 pt-2">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <UserIcon className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="text-[9px] font-extrabold text-slate-600 uppercase truncate">
                            {r.technician || 'Sin Asignar'}
                          </span>
                        </div>
                        <span className={`text-[8px] font-black px-2 py-0.5 rounded-full border uppercase tracking-wider shrink-0 ${statusBg}`}>
                          {statusLabel}
                        </span>
                      </div>
                    </a>
                  );
                })
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 italic gap-2 py-6">
                  <span className="text-xs font-bold">Sin visitas en esta selección</span>
                  <p className="text-[9px] uppercase tracking-widest text-slate-400">Limpia filtros para ver más</p>
                </div>
              )}
            </div>
            <div className="mt-4 border-t border-slate-100 pt-3">
              <a href="/visit-reports" className="text-[10px] font-black text-blue-600 hover:text-blue-700 flex items-center justify-center gap-1.5 uppercase tracking-widest hover:underline transition-colors">
                Historial Completo <ArrowTrendingUpIcon className="w-3.5 h-3.5" />
              </a>
            </div>
          </VisualCard>

        </div>

      </div>

    </div>
  );
};

// Premium Interactive KPI Card Component
const KPITile = ({ title, value, subtitle, icon, isActive, onClick, activeColor, baseColor }: any) => {
  return (
    <button 
      onClick={onClick}
      className={`w-full text-left p-5 rounded-2xl shadow-md border-t-4 transition-all duration-300 transform flex items-center gap-4 cursor-pointer focus:outline-none relative overflow-hidden group select-none ${
        isActive 
          ? `${activeColor} ring-4 ring-blue-500/10 shadow-xl scale-[1.02] border-t-4` 
          : `${baseColor} hover:border-slate-300 hover:shadow-lg hover:-translate-y-0.5 bg-white opacity-70 grayscale-[20%] hover:opacity-100 hover:grayscale-0`
      }`}
    >
      {/* Top Active Indicator Glow Bar */}
      {isActive && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 to-blue-500 animate-pulse" />
      )}
      
      {/* Active Small Badge in corner */}
      {isActive && (
        <div className="absolute top-0 right-0 bg-blue-600 text-[8px] font-black uppercase text-white tracking-widest px-2 py-0.5 rounded-bl-lg shadow-sm">
          ACTIVO
        </div>
      )}

      {/* Decorative background light circles */}
      <div className={`absolute -right-6 -bottom-6 w-16 h-16 rounded-full transition-all duration-500 opacity-10 group-hover:scale-150 ${
        isActive ? 'bg-blue-600/30' : 'bg-slate-400'
      }`} />

      {/* Icon frame with micro-animation */}
      <div className={`p-3.5 rounded-xl shadow-md transition-all duration-300 flex items-center justify-center ${
        isActive 
          ? 'bg-white/95 scale-110 shadow-lg text-blue-600 rotate-3' 
          : 'bg-slate-50 text-slate-400 group-hover:scale-105'
      }`}>
        {icon}
      </div>

      <div className="min-w-0 flex-1 relative z-10">
        <p className={`text-[9px] font-extrabold uppercase tracking-wider leading-none mb-1.5 ${
          isActive ? 'text-blue-900/80' : 'text-slate-400'
        }`}>
          {title}
        </p>
        <h3 className="text-2.5xl font-black text-slate-900 leading-none mb-1 tracking-tight">
          {value}
        </h3>
        <p className={`text-[8.5px] font-bold truncate leading-none ${
          isActive ? 'text-blue-800/70' : 'text-slate-400/80'
        }`}>
          {subtitle}
        </p>
      </div>
    </button>
  );
};

// Custom Power BI card style
const VisualCard = ({ title, subtitle, children }: any) => (
  <div className="bg-white p-5 rounded-2xl shadow-lg border border-slate-200 flex flex-col transition-all hover:shadow-xl">
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-3 border-b border-slate-100 pb-3">
      <div className="flex items-center gap-2">
        <div className="w-1.5 h-4 bg-blue-600 rounded-full" />
        <h3 className="text-xs font-black text-slate-800 uppercase tracking-wider">{title}</h3>
      </div>
      {subtitle && (
        <span className="text-[9px] font-extrabold text-slate-400 uppercase tracking-wider">{subtitle}</span>
      )}
    </div>
    {children}
  </div>
);

export default Dashboard;
