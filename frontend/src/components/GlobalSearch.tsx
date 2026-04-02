import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, FileText, AlertTriangle, BarChart2, ArrowRight, Loader2, User, Command } from 'lucide-react';
import { useDebounce } from '../hooks/useDebounce';

interface SearchResult {
  id: number;
  type: 'incident' | 'visit_report' | 'quality_report' | 'supplier_report' | 'user';
  category: string;
  title: string;
  subtitle: string;
  url: string;
}

const TYPE_CONFIG: Record<SearchResult['type'], { icon: React.ElementType; color: string; bg: string; label: string }> = {
  incident: { icon: AlertTriangle, color: 'text-orange-500', bg: 'bg-orange-50', label: 'Incidencia' },
  visit_report: { icon: FileText, color: 'text-blue-500', bg: 'bg-blue-50', label: 'Reporte de Visita' },
  quality_report: { icon: BarChart2, color: 'text-purple-500', bg: 'bg-purple-50', label: 'Reporte de Calidad' },
  supplier_report: { icon: FileText, color: 'text-green-500', bg: 'bg-green-50', label: 'Reporte de Proveedor' },
  user: { icon: User, color: 'text-indigo-500', bg: 'bg-indigo-50', label: 'Usuario' },
};

async function fetchSearchResults(query: string, country: string): Promise<SearchResult[]> {
  const token = localStorage.getItem('access_token');
  const baseUrl = import.meta.env.VITE_API_URL || '';
  const res = await fetch(`${baseUrl}/api/incidents/global-search/?q=${encodeURIComponent(query)}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-Country-Code': country || 'CL',
    },
  });
  if (!res.ok) return [];
  const data = await res.json();
  return data.results || [];
}

export function GlobalSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const debouncedQuery = useDebounce(query, 300);

  // Group results by category
  const groupedResults = useMemo(() => {
    const groups: Record<string, SearchResult[]> = {};
    results.forEach(res => {
      if (!groups[res.category]) groups[res.category] = [];
      groups[res.category].push(res);
    });
    return groups;
  }, [results]);

  // Serialized list for keyboard navigation
  const flatResults = useMemo(() => {
    return Object.values(groupedResults).flat();
  }, [groupedResults]);

  // Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(prev => !prev);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    const handleOpenSearch = () => setOpen(true);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('open-global-search', handleOpenSearch);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('open-global-search', handleOpenSearch);
    };
  }, []);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150);
      setQuery('');
      setResults([]);
      setSelectedIndex(0);
    }
  }, [open]);

  useEffect(() => {
    if (debouncedQuery.trim().length < 2) {
      setResults([]);
      return;
    }
    const country = localStorage.getItem('country_code') || 'CL';
    setLoading(true);
    fetchSearchResults(debouncedQuery, country)
      .then(setResults)
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  const handleSelect = useCallback((result: SearchResult) => {
    navigate(result.url);
    setOpen(false);
  }, [navigate]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') { 
      e.preventDefault(); 
      setSelectedIndex(i => Math.min(i + 1, flatResults.length - 1)); 
    }
    if (e.key === 'ArrowUp') { 
      e.preventDefault(); 
      setSelectedIndex(i => Math.max(i - 1, 0)); 
    }
    if (e.key === 'Enter' && flatResults[selectedIndex]) {
      handleSelect(flatResults[selectedIndex]);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[9999] flex items-start justify-center pt-[10vh] px-4">
          {/* Backdrop */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
            className="absolute inset-0 bg-slate-900/40 backdrop-blur-md" 
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="relative w-full max-w-2xl bg-white/80 backdrop-blur-2xl rounded-3xl shadow-[0_32px_64px_-12px_rgba(0,0,0,0.14)] ring-1 ring-slate-200/50 overflow-hidden flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            {/* Search Input Area */}
            <div className="relative flex items-center gap-4 px-6 py-5 border-b border-slate-100">
              <div className="flex items-center justify-center w-10 h-10 rounded-2xl bg-indigo-50 text-indigo-600">
                <Search className="w-5 h-5" />
              </div>
              <input
                ref={inputRef}
                type="text"
                placeholder="Busca por código, cliente, folio SAP, usuario..."
                value={query}
                onChange={e => { setQuery(e.target.value); setSelectedIndex(0); }}
                onKeyDown={handleKeyDown}
                className="flex-1 text-lg font-medium text-slate-800 placeholder-slate-400 bg-transparent outline-none"
              />
              <div className="flex items-center gap-2">
                {loading && <Loader2 className="w-5 h-5 text-indigo-500 animate-spin" />}
                {query && !loading && (
                  <button 
                    onClick={() => setQuery('')}
                    className="p-1.5 hover:bg-slate-100 rounded-full transition-colors"
                  >
                    <X className="w-4 h-4 text-slate-400" />
                  </button>
                )}
                <div className="hidden sm:flex items-center gap-1 px-2 py-1 bg-slate-100 rounded-lg text-[10px] font-black text-slate-400 border border-slate-200">
                  <span className="uppercase">Esc</span>
                </div>
              </div>
            </div>

            {/* Results Scroller */}
            <div className="max-h-[60vh] overflow-y-auto overflow-x-hidden custom-scrollbar py-2">
              {Object.entries(groupedResults).length > 0 ? (
                Object.entries(groupedResults).map(([category, categoryResults]) => (
                  <div key={category} className="mb-4">
                    <h3 className="px-6 py-2 text-[11px] font-black uppercase tracking-[0.2em] text-slate-400 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
                      {category}
                    </h3>
                    <ul>
                      {categoryResults.map((result) => {
                        const cfg = TYPE_CONFIG[result.type];
                        const Icon = cfg.icon;
                        const absoluteIndex = flatResults.indexOf(result);
                        const isSelected = absoluteIndex === selectedIndex;

                        return (
                          <li key={`${result.type}-${result.id}`} className="px-3">
                            <button
                              onClick={() => handleSelect(result)}
                              onMouseEnter={() => setSelectedIndex(absoluteIndex)}
                              className={`w-full group relative flex items-center gap-4 px-4 py-3 rounded-2xl transition-all duration-200 text-left ${
                                isSelected 
                                  ? 'bg-indigo-600 shadow-xl shadow-indigo-200' 
                                  : 'hover:bg-slate-50'
                              }`}
                            >
                              {/* Selection Indicator (Premium Touch) */}
                              {isSelected && (
                                <motion.div 
                                  layoutId="active-pill"
                                  className="absolute left-0 w-1 h-8 bg-white rounded-r-full"
                                />
                              )}

                              <div className={`flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-xl transition-colors ${
                                isSelected ? 'bg-white/20' : cfg.bg
                              }`}>
                                <Icon className={`w-5 h-5 ${isSelected ? 'text-white' : cfg.color}`} />
                              </div>

                              <div className="flex-1 min-w-0">
                                <p className={`text-sm font-bold truncate transition-colors ${
                                  isSelected ? 'text-white' : 'text-slate-800'
                                }`}>
                                  {result.title}
                                </p>
                                <p className={`text-xs truncate transition-colors ${
                                  isSelected ? 'text-indigo-100' : 'text-slate-500'
                                }`}>
                                  {cfg.label} <span className="mx-1 opacity-50">•</span> {result.subtitle}
                                </p>
                              </div>

                              <ArrowRight className={`w-4 h-4 transition-all ${
                                isSelected ? 'text-white translate-x-0 opacity-100' : 'text-slate-300 -translate-x-2 opacity-0'
                              }`} />
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ))
              ) : (
                debouncedQuery.length >= 2 && !loading && (
                  <div className="py-12 flex flex-col items-center justify-center text-center px-6">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                      <Command className="w-8 h-8 text-slate-300" />
                    </div>
                    <h4 className="text-slate-800 font-bold mb-1">Sin coincidencias exactas</h4>
                    <p className="text-sm text-slate-400 max-w-[240px]">
                      No pudimos encontrar registros para "<span className="text-slate-600 font-semibold">{debouncedQuery}</span>"
                    </p>
                  </div>
                )
              )}
              
              {query.length < 2 && (
                <div className="py-12 flex flex-col items-center justify-center text-center px-6 opacity-40">
                  <Command className="w-12 h-12 text-slate-300 mb-2" />
                  <p className="text-xs font-black uppercase tracking-widest text-slate-400">Escribe para iniciar búsqueda global</p>
                </div>
              )}
            </div>

            {/* Footer / Shortcuts */}
            <div className="px-6 py-3 bg-slate-50/50 border-t border-slate-100 flex items-center gap-6 text-[10px] font-black uppercase tracking-widest text-slate-400">
              <div className="flex items-center gap-2">
                <kbd className="bg-white border border-slate-200 shadow-sm px-1.5 py-0.5 rounded text-slate-500 block">↑↓</kbd>
                <span>Navegar</span>
              </div>
              <div className="flex items-center gap-2">
                <kbd className="bg-white border border-slate-200 shadow-sm px-1.5 py-0.5 rounded text-slate-500 block">↵</kbd>
                <span>Seleccionar</span>
              </div>
              <div className="ml-auto flex items-center gap-2 opacity-60">
                <Command className="w-3 h-3" />
                <span>Shift + K</span>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
