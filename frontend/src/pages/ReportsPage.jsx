import React, { useState, useMemo } from 'react';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { incidentsAPI } from '../services/api';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  ResponsiveContainer, CartesianGrid, XAxis, YAxis, Tooltip, Line, ComposedChart, LabelList
} from 'recharts';
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  BeakerIcon,
  TruckIcon,
  ArrowTrendingUpIcon,
  CalendarIcon,
  Square3Stack3DIcon,
  PrinterIcon,
  BoltIcon,
  EyeIcon,
  EyeSlashIcon,
  TrophyIcon,
  ClockIcon,
  ChartBarIcon,
  ExclamationCircleIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';

// Paleta Neon v31 Final
const NEON_PALETTE = [
  '#a855f7', // Purple
  '#06b6d4', // Cyan
  '#ec4899', // Pink
  '#f59e0b', // Amber
  '#10b981', // Emerald
  '#3b82f6'  // Blue
];

const MONTH_NAMES_ES = {
  'Jan': 'Ene', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Abr',
  'May': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Ago',
  'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dec': 'Dic'
};

const ModernTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#0f172a]/95 backdrop-blur-xl border border-white/10 px-3 py-2 rounded-lg shadow-2xl z-50 ring-1 ring-white/10">
        <div className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]"
            style={{ backgroundColor: payload[0].payload.fill, boxShadow: `0 0 8px ${payload[0].payload.fill}` }}
          />
          <span className="text-gray-300 font-medium text-xs">{payload[0].name}:</span>
          <span className="font-bold text-white text-sm tabular-nums">{payload[0].value}</span>
        </div>
      </div>
    );
  }
  return null;
};

const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  if (percent < 0.05) return null;

  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" className="text-[10px] font-black drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)] pointer-events-none select-none">
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

const renderBarLabel = (props) => {
  const { x, y, width, value } = props;
  return (
    <text x={x + width / 2} y={y - 5} fill="#fff" textAnchor="middle" fontSize={10} fontWeight="bold" className="drop-shadow-md">
      {value}
    </text>
  );
};


const CustomLegend = ({ data, colors }) => (
  <div className="flex flex-col justify-center gap-1.5 h-full overflow-hidden pr-2">
    {data.map((entry, index) => (
      <div
        key={`legend-${index}`}
        className="flex items-center gap-2 group p-1.5 hover:bg-white/[0.05] rounded-lg transition-colors border border-transparent hover:border-white/5 cursor-default"
      >
        <div
          className="w-2 h-2 rounded-full shrink-0 shadow-[0_0_8px_currentColor] transition-transform group-hover:scale-110"
          style={{ backgroundColor: colors[index % colors.length], color: colors[index % colors.length] }}
        />
        <div className="flex justify-between w-full items-center min-w-0">
          <span className="text-gray-400 group-hover:text-white text-[10px] font-medium truncate max-w-[100px] transition-colors" title={entry.name}>
            {entry.name}
          </span>
          <span className="text-white font-bold text-[10px] bg-white/[0.06] px-1.5 py-0.5 rounded border border-white/5 shadow-sm">
            {entry.value}
          </span>
        </div>
      </div>
    ))}
  </div>
);

const ReportsPage = () => {
  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [showCategoryLegend, setShowCategoryLegend] = useState(true);
  const [showProviderLegend, setShowProviderLegend] = useState(true);

  const { data: stats, isLoading, isFetching } = useQuery({
    queryKey: ['reportStats', selectedYear, selectedCategory],
    queryFn: () => incidentsAPI.dashboard({
      year: selectedYear,
      category: selectedCategory
    }).then(res => res.data),
    placeholderData: keepPreviousData,
    refetchInterval: 300000,
    retry: 1,
    staleTime: 60000
  });

  const monthlyStatsES = useMemo(() => {
    if (!stats?.monthlyStats) return [];
    return stats.monthlyStats.map(item => ({
      ...item,
      name: MONTH_NAMES_ES[item.name] || item.name
    }));
  }, [stats]);

  const categoryData = useMemo(() => {
    if (!stats?.categoryTree) return [];

    // Normalización de nombres para agrupar categorías similares
    const normalizeName = (name) => {
      const upperName = name.toUpperCase();
      // Grupos específicos solicitados
      if (upperName.includes('125') || upperName.includes('125 S-3,2')) return '125 / 125 S-3,2';
      if (upperName.includes('160')) return '160';
      if (upperName.includes('200')) return '200';
      if (upperName.includes('250')) return '250';
      if (upperName.includes('315')) return '315';
      if (upperName.includes('400')) return '400';
      if (upperName.includes('BETA FIBRA')) return 'BETA FIBRA';
      return name;
    };

    const groupedData = {};

    Object.entries(stats.categoryTree).forEach(([name, data]) => {
      // Si estamos en nivel de subcategoría (drill-down), NO agrupamos para no perder detalle
      if (selectedCategory) {
        groupedData[name] = (groupedData[name] || 0) + (data.count || data.total || 0);
      } else {
        // En nivel principal, aplicamos normalización solo si es necesario, 
        // pero el usuario pidió esto específicamente para el gráfico de torta.
        // Asumiremos que quiere ver esto limpio SIEMPRE en el gráfico.
        // PERO, si es categoryTree del backend, ya vienen las categorías principales.
        // Si el usuario ve "125" y "125 S-3,2" como CI o SUBCATEGORÍAS, debemos agruparlas.

        // Revisando el requerimiento: "mira ahi esta 125 y 125 s3.2 que podrian ser la misma categoria"
        // Esto sugiere que son SUBCATEGORÍAS dentro de una categoría padre (como TUBERIA_BETA).
        // Por tanto, esta agrupación debe aplicar PRINCIPALMENTE cuando estamos mostrando subcategorías.

        const normalized = normalizeName(name);
        groupedData[normalized] = (groupedData[normalized] || 0) + (data.count || data.total || 0);
      }
    });

    return Object.entries(groupedData)
      .map(([name, value]) => ({
        name,
        value
      }))
      .sort((a, b) => b.value - a.value);
  }, [stats, selectedCategory]);

  const providerData = useMemo(() => {
    if (!stats?.topProviders) return [];
    return stats.topProviders.slice(0, 5).map(([name, value]) => ({ name, value }));
  }, [stats]);

  const topCategoryLegend = useMemo(() => categoryData.slice(0, 7), [categoryData]);
  const topProviderLegend = useMemo(() => providerData.slice(0, 5), [providerData]);

  // Debug logging
  console.debug('📊 [ReportsPage] State:', { isLoading, hasStats: !!stats, isFetching });
  if (stats) console.debug('📊 [ReportsPage] Stats summary:', {
    monthly: stats.monthlyStats?.length,
    categories: Object.keys(stats.categoryTree || {}).length
  });

  // NO RETURN EARLY if isLoading. Show Skeleton or Empty Structure instead.

  return (
    <div className="flex-1 flex flex-col font-sans relative selection:bg-purple-500/30">

      {/* Background Optimized v31 (Fondo sutil sobre el global de App.tsx) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[10%] w-[60%] h-[60%] bg-purple-900/10 blur-[40px] rounded-full mix-blend-screen opacity-40" />
        <div className="absolute bottom-[-20%] right-[10%] w-[60%] h-[60%] bg-cyan-900/10 blur-[40px] rounded-full mix-blend-screen opacity-40" />
      </div>

      <div className="flex-1 relative z-10 flex flex-col gap-5 transition-all duration-300">

        {/* HEADER v31 */}
        <div className="flex flex-col xl:flex-row items-center gap-6 bg-white/[0.03] border border-white/[0.08] rounded-2xl p-3 pr-4 shadow-xl shadow-black/30 backdrop-blur-xl w-full ring-1 ring-white/[0.05]">

          <div className="flex items-center gap-4 pl-2 pr-6 border-r border-white/[0.08] shrink-0">
            <div className="p-2 bg-gradient-to-br from-purple-600 to-indigo-700 rounded-xl shadow-[0_0_15px_rgba(124,58,237,0.3)] ring-1 ring-black/20">
              <BoltIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col leading-none">
              <h1 className="text-lg font-black text-white tracking-tight flex items-center gap-2 whitespace-nowrap">
                PANEL <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 drop-shadow-[0_0_10px_rgba(168,85,247,0.3)]">DE CONTROL</span>
              </h1>
              <span className="text-[9px] font-bold text-gray-500 tracking-[0.25em] uppercase mt-0.5">ANALÍTICA Y RENDIMIENTO</span>
            </div>
          </div>

          <div className="flex-1 w-full grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'ABIERTO', val: stats?.abiertos, color: 'purple', icon: ExclamationTriangleIcon },
              { label: 'LAB', val: stats?.laboratorio, color: 'pink', icon: BeakerIcon },
              { label: 'PROV', val: stats?.proveedor, color: 'cyan', icon: TruckIcon },
              { label: 'CERRADA', val: stats?.cerrados, color: 'emerald', icon: CheckCircleIcon }
            ].map((kpi, i) => (
              <div
                key={i}
                className={`
                      relative flex items-center gap-3 p-2 px-3 rounded-xl transition-all group overflow-hidden
                      bg-gradient-to-br from-white/[0.08] to-white/[0.02] 
                      border border-${kpi.color}-500/20 
                      hover:bg-white/[0.1]
                      backdrop-blur-xl ring-1 ring-${kpi.color}-500/10 shadow-lg
                    `}
              >
                <div className={`p-1.5 rounded-lg bg-${kpi.color}-500/10 text-${kpi.color}-400 group-hover:text-white group-hover:bg-${kpi.color}-500 transition-colors shadow-inner ring-1 ring-white/5`}>
                  <kpi.icon className="h-4 w-4" />
                </div>
                <div className="flex flex-col leading-none min-w-0">
                  {isLoading && kpi.val === undefined ? (
                    <div className="h-5 w-12 bg-white/10 rounded animate-pulse mb-1"></div>
                  ) : (
                    <span className="text-base font-black text-white group-hover:scale-105 transition-transform origin-left animate-fade-in">{kpi.val || 0}</span>
                  )}
                  <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider group-hover:text-gray-300 transition-colors">{kpi.label}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center gap-4 shrink-0 pl-4 xl:border-l border-white/[0.08]">
            {(isFetching || isLoading) && <div className="animate-spin w-3 h-3 border-2 border-purple-500 border-t-transparent rounded-full mr-1" />}

            {/* SELECTOR PRO v31 */}
            <div className="relative group">
              <select
                value={selectedYear || ''}
                onChange={(e) => setSelectedYear(e.target.value ? Number(e.target.value) : null)}
                className={`
                      appearance-none bg-[#0a0a0a]/80 backdrop-blur-xl text-gray-200 text-xs font-bold 
                      rounded-lg pl-4 pr-10 py-2.5 outline-none 
                      border border-white/10 hover:border-purple-500/50 focus:border-purple-500 
                      transition-all cursor-pointer w-36 shadow-lg hover:shadow-purple-500/10
                      ring-1 ring-white/5 focus:ring-purple-500/30
                      ${(isFetching || isLoading) ? 'opacity-80' : ''}
                    `}
              >
                <option value="">📅 Histórico</option>
                {(stats?.years || []).map(year => (
                  <option key={year} value={year} className="bg-[#0f172a] text-gray-300">Año {year}</option>
                ))}
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 group-hover:text-white transition-colors">
                <ChevronDownIcon className="h-3 w-3 stroke-[3]" />
              </div>
            </div>

            <button
              onClick={() => window.print()}
              className="p-2 bg-[#0a0a0a]/60 text-gray-400 hover:text-white rounded-lg border border-white/10 hover:border-purple-500 transition-all active:scale-95 hover:shadow-[0_0_10px_rgba(168,85,247,0.2)]"
            >
              <PrinterIcon className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className={`flex flex-col gap-5 flex-1 min-h-0 transition-opacity duration-300`}>

          {/* Row 1: Charts (Velocity Mode) */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-5 lg:h-[35vh] min-h-[280px] shrink-0">

            {/* TENDENCIA */}
            <div className="bg-gradient-to-br from-purple-900/[0.12] to-[#0a0a0a]/90 backdrop-blur-xl border border-purple-500/20 rounded-2xl p-4 flex flex-col relative shadow-xl shadow-black/20 ring-1 ring-purple-500/10 group transition-all">
              <div className="absolute top-4 right-5 z-20">
                <div className="flex flex-col items-end">
                  <p className="text-[9px] text-gray-500 uppercase font-black tracking-wider">Res. 2026</p>
                  <p className="text-xs font-black text-emerald-400 flex items-center justify-end gap-1">
                    85% <ClockIcon className="h-3 w-3" />
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 mb-2 z-10">
                <div className="p-1 rounded bg-purple-500/20 text-purple-400">
                  <ArrowTrendingUpIcon className="h-4 w-4" />
                </div>
                <h3 className="text-xs font-black text-white uppercase tracking-wider">Tendencia Mensual</h3>
              </div>

              <div className="w-full relative group">
                {isLoading && !stats ? (
                  <div className="w-full h-[260px] flex items-center justify-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={monthlyStatsES} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="neonPurpleArea" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#a855f7" stopOpacity={0.6} />
                          <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} dy={5} fontWeight={600} />
                      <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                      <Tooltip content={<ModernTooltip />} cursor={{ stroke: '#a855f7', strokeWidth: 1, strokeDasharray: '4 4' }} />
                      <Area
                        type="monotone"
                        dataKey="total"
                        stroke="#a855f7"
                        strokeWidth={2}
                        fill="url(#neonPurpleArea)"
                        activeDot={{ r: 4, fill: "#fff", stroke: "#a855f7" }}
                        animationDuration={800}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* EVOLUCIÓN */}
            <div className="bg-gradient-to-br from-cyan-900/[0.12] to-[#0a0a0a]/90 backdrop-blur-xl border border-cyan-500/20 rounded-2xl p-4 flex flex-col relative shadow-xl shadow-black/20 ring-1 ring-cyan-500/10 group transition-all">

              <div className="flex items-center gap-2 mb-2 z-10">
                <div className="p-1 rounded bg-cyan-500/20 text-cyan-400">
                  <ChartBarIcon className="h-4 w-4" />
                </div>
                <h3 className="text-xs font-black text-white uppercase tracking-wider">Evolución Anual</h3>
              </div>

              <div className="w-full relative z-10">
                {isLoading && !stats ? (
                  <div className="w-full h-[260px] flex items-center justify-center">
                    <div className="animate-pulse w-full h-3/4 bg-cyan-500/5 rounded-lg"></div>
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <ComposedChart data={stats?.yearlyStatsData || []} barGap={0} barCategoryGap="30%">
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} dy={5} fontWeight={600} />
                      <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />

                      <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={50} animationDuration={800}>
                        {stats?.yearlyStatsData?.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={`url(#cyanBarGrad-${index})`}
                          />
                        ))}
                        <LabelList dataKey="value" content={renderBarLabel} />
                      </Bar>

                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#06b6d4"
                        strokeWidth={2}
                        dot={{ r: 3, fill: "#083344", stroke: "#06b6d4", strokeWidth: 1.5 }}
                        activeDot={{ r: 0 }}
                        strokeOpacity={0.8}
                        animationDuration={1000}
                      />

                      <defs>
                        {stats?.yearlyStatsData?.map((entry, index) => (
                          <linearGradient key={`cyanBarGrad-${index}`} id={`cyanBarGrad-${index}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.9} />
                            <stop offset="100%" stopColor="#0891b2" stopOpacity={0.1} />
                          </linearGradient>
                        ))}
                      </defs>
                    </ComposedChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </div>

          {/* Row 2: Tortas y Clientes */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 xl:h-[30vh] min-h-[250px] shrink-0 mb-4">

            {/* CATEGORÍA */}
            <div className="bg-gradient-to-br from-pink-900/[0.12] to-[#0a0a0a]/90 backdrop-blur-xl border border-pink-500/20 rounded-2xl p-4 flex flex-col relative shadow-xl shadow-black/20 ring-1 ring-pink-500/10 group transition-all">

              <div className="flex justify-between items-center mb-1 z-10 w-full">
                <div className="flex items-center gap-2 overflow-hidden">
                  <h3 className="text-[10px] font-black text-white flex items-center gap-2 uppercase tracking-wide whitespace-nowrap">
                    <Square3Stack3DIcon className="h-4 w-4 text-pink-400" />
                    {selectedCategory ? (
                      <span className="flex items-center gap-1">
                        <button
                          onClick={() => setSelectedCategory(null)}
                          className="hover:text-pink-400 transition-colors flex items-center gap-1"
                          title="Volver a todas las categorías"
                        >
                          <ChevronDownIcon className="h-3 w-3 rotate-90" />
                          CATEGORÍAS
                        </button>
                        <span className="text-gray-500">/</span>
                        <span className="text-pink-400 truncate max-w-[100px]">{selectedCategory}</span>
                      </span>
                    ) : (
                      "POR CATEGORÍA"
                    )}
                  </h3>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setShowCategoryLegend(!showCategoryLegend)}
                  className="text-gray-500 hover:text-white transition-colors p-1 shrink-0"
                >
                  {showCategoryLegend ? <EyeSlashIcon className="h-3 w-3" /> : <EyeIcon className="h-3 w-3" />}
                </motion.button>
              </div>

              <div className="flex items-center gap-3 z-10">
                {isLoading && !stats ? (
                  <div className="w-full h-[180px] flex items-center justify-center">
                    <div className="animate-pulse w-24 h-24 rounded-full bg-pink-500/5"></div>
                  </div>
                ) : (
                  <>
                    <motion.div
                      layout
                      className="relative"
                      style={{ width: showCategoryLegend ? '50%' : '100%' }}
                      transition={{ type: "spring", stiffness: 350, damping: 25 }}
                    >
                      <ResponsiveContainer width="100%" height={180}>
                        <PieChart>
                          <Pie
                            data={categoryData}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            innerRadius={selectedCategory ? "40%" : "50%"}
                            outerRadius={showCategoryLegend ? "80%" : "90%"}
                            paddingAngle={3}
                            stroke="none"
                            label={renderCustomizedLabel}
                            labelLine={false}
                            animationDuration={600}
                            onClick={(data) => {
                              if (!selectedCategory) {
                                setSelectedCategory(data.name);
                              }
                            }}
                            className={!selectedCategory ? "cursor-pointer" : "cursor-default"}
                          >
                            {categoryData.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={NEON_PALETTE[index % NEON_PALETTE.length]}
                                style={{
                                  filter: 'drop-shadow(0 0 4px rgba(0,0,0,0.3))',
                                  cursor: !selectedCategory ? 'pointer' : 'default',
                                  opacity: selectedCategory ? 0.8 : 1
                                }}
                              />
                            ))}
                          </Pie>
                          <Tooltip content={<ModernTooltip />} isAnimationActive={false} />
                        </PieChart>
                      </ResponsiveContainer>
                    </motion.div>

                    <AnimatePresence>
                      {showCategoryLegend && (
                        <motion.div
                          initial={{ opacity: 0, width: 0, scale: 0.9 }}
                          animate={{ opacity: 1, width: '50%', scale: 1 }}
                          exit={{ opacity: 0, width: 0, scale: 0.9 }}
                          transition={{ type: "spring", stiffness: 200, damping: 25 }}
                          className="h-full pl-3 border-l border-white/5 overflow-hidden flex flex-col justify-center origin-left"
                        >
                          <CustomLegend data={topCategoryLegend} colors={NEON_PALETTE} />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </>
                )}
              </div>
            </div>

            {/* PROVEEDORES */}
            <div className="bg-gradient-to-br from-emerald-900/[0.12] to-[#0a0a0a]/90 backdrop-blur-xl border border-emerald-500/20 rounded-2xl p-4 flex flex-col relative shadow-xl shadow-black/20 ring-1 ring-emerald-500/10 group transition-all">

              <div className="flex justify-between items-center mb-1 z-10">
                <h3 className="text-[10px] font-black text-white flex items-center gap-2 uppercase tracking-wide">
                  <TruckIcon className="h-4 w-4 text-emerald-400" />
                  Proveedores
                </h3>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setShowProviderLegend(!showProviderLegend)}
                  className="text-gray-500 hover:text-white transition-colors p-1"
                >
                  {showProviderLegend ? <EyeSlashIcon className="h-3 w-3" /> : <EyeIcon className="h-3 w-3" />}
                </motion.button>
              </div>

              <div className="flex items-center gap-3 z-10">
                {isLoading && !stats ? (
                  <div className="w-full h-[180px] flex items-center justify-center">
                    <div className="animate-pulse w-24 h-24 rounded-full bg-emerald-500/5"></div>
                  </div>
                ) : (
                  <>
                    <motion.div
                      layout
                      className="relative"
                      style={{ width: showProviderLegend ? '50%' : '100%' }}
                      transition={{ type: "spring", stiffness: 350, damping: 25 }}
                    >
                      <ResponsiveContainer width="100%" height={180}>
                        <PieChart>
                          <Pie
                            data={providerData}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            innerRadius="50%"
                            outerRadius={showProviderLegend ? "80%" : "90%"}
                            paddingAngle={3}
                            stroke="none"
                            label={renderCustomizedLabel}
                            labelLine={false}
                            animationDuration={600}
                          >
                            {providerData.map((entry, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={NEON_PALETTE[(index + 1) % NEON_PALETTE.length]}
                                style={{ filter: 'drop-shadow(0 0 4px rgba(0,0,0,0.3))' }}
                              />
                            ))}
                          </Pie>
                          <Tooltip content={<ModernTooltip />} isAnimationActive={false} />
                        </PieChart>
                      </ResponsiveContainer>
                    </motion.div>
                    <AnimatePresence>
                      {showProviderLegend && (
                        <motion.div
                          initial={{ opacity: 0, width: 0, scale: 0.9 }}
                          animate={{ opacity: 1, width: '50%', scale: 1 }}
                          exit={{ opacity: 0, width: 0, scale: 0.9 }}
                          transition={{ type: "spring", stiffness: 200, damping: 25 }}
                          className="h-full pl-3 border-l border-white/5 overflow-hidden flex flex-col justify-center origin-left"
                        >
                          <CustomLegend data={topProviderLegend} colors={NEON_PALETTE.map((_, i, arr) => arr[(i + 1) % arr.length])} />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </>
                )}
              </div>
            </div>

            {/* CLIENTES CRÍTICOS */}
            <div className="bg-gradient-to-br from-amber-900/[0.12] to-[#0a0a0a]/90 backdrop-blur-xl border border-amber-500/20 rounded-2xl p-4 flex flex-col relative shadow-xl shadow-black/20 ring-1 ring-amber-500/10 group transition-all">

              <h3 className="text-[10px] font-black text-white flex items-center gap-2 mb-2 uppercase tracking-wide z-10">
                <ExclamationCircleIcon className="h-4 w-4 text-amber-500" />
                CLIENTES CRÍTICOS
              </h3>
              <div className="space-y-1.5 overflow-y-auto custom-scrollbar flex-1 pr-1 z-10">
                {isLoading && !stats ? (
                  <div className="space-y-2">
                    {[1, 2, 3].map(i => <div key={i} className="h-8 bg-amber-500/5 rounded animate-pulse"></div>)}
                  </div>
                ) : (
                  (stats?.topClients || []).slice(0, 7).map(([name, count], i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-white/[0.03] hover:bg-white/[0.07] border border-white/[0.05] hover:border-amber-500/30 transition-all group/item cursor-default shadow-sm hover:ring-1 hover:ring-amber-500/20">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className={`
                                 w-5 h-5 rounded-md flex items-center justify-center text-[9px] font-black
                                 ${i === 0 ? 'bg-amber-500 text-black shadow-lg shadow-amber-500/30' :
                            i === 1 ? 'bg-gray-400 text-black shadow-lg shadow-gray-400/30' :
                              i === 2 ? 'bg-orange-700 text-white shadow-lg shadow-orange-700/30' :
                                'bg-white/10 text-gray-500'}
                              `}>
                          {i + 1}
                        </div>
                        <span className="text-gray-400 font-bold text-[10px] truncate max-w-[130px] group-hover/item:text-white transition-colors" title={name}>
                          {name}
                        </span>
                      </div>
                      <span className="text-[10px] font-black text-white tabular-nums bg-white/5 px-1.5 py-0.5 rounded border border-white/5">{count}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;