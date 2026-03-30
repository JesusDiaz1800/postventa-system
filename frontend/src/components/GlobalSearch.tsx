import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, FileText, AlertTriangle, BarChart2, ArrowRight, Loader2 } from 'lucide-react';
import { useDebounce } from '../hooks/useDebounce';

interface SearchResult {
  id: number;
  type: 'incident' | 'visit_report' | 'quality_report' | 'supplier_report';
  title: string;
  subtitle: string;
  url: string;
}

const TYPE_CONFIG: Record<SearchResult['type'], { icon: React.ElementType; color: string; label: string }> = {
  incident: { icon: AlertTriangle, color: 'text-orange-500', label: 'Incidencia' },
  visit_report: { icon: FileText, color: 'text-blue-500', label: 'Reporte de Visita' },
  quality_report: { icon: BarChart2, color: 'text-purple-500', label: 'Reporte de Calidad' },
  supplier_report: { icon: FileText, color: 'text-green-500', label: 'Reporte de Proveedor' },
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

  // Ctrl+K / Cmd+K shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(prev => !prev);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Focus input when opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 80);
      setQuery('');
      setResults([]);
      setSelectedIndex(0);
    }
  }, [open]);

  // Search
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

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setSelectedIndex(i => Math.min(i + 1, results.length - 1)); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setSelectedIndex(i => Math.max(i - 1, 0)); }
    if (e.key === 'Enter' && results[selectedIndex]) handleSelect(results[selectedIndex]);
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] flex items-start justify-center pt-[12vh] px-4"
      onClick={() => setOpen(false)}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl ring-1 ring-black/5 overflow-hidden animate-slide-down"
        onClick={e => e.stopPropagation()}
      >
        {/* Input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-slate-100">
          <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Buscar incidencias, reportes, clientes…"
            value={query}
            onChange={e => { setQuery(e.target.value); setSelectedIndex(0); }}
            onKeyDown={handleKeyDown}
            className="flex-1 text-sm text-slate-800 placeholder-slate-400 bg-transparent outline-none"
          />
          {loading && <Loader2 className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />}
          {!loading && query && (
            <button onClick={() => setQuery('')}>
              <X className="w-4 h-4 text-slate-400 hover:text-slate-600" />
            </button>
          )}
        </div>

        {/* Results */}
        {results.length > 0 && (
          <ul className="max-h-80 overflow-y-auto py-2">
            {results.map((result, index) => {
              const cfg = TYPE_CONFIG[result.type];
              const Icon = cfg.icon;
              const isSelected = index === selectedIndex;
              return (
                <li key={`${result.type}-${result.id}`}>
                  <button
                    onClick={() => handleSelect(result)}
                    onMouseEnter={() => setSelectedIndex(index)}
                    className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors ${isSelected ? 'bg-blue-50' : 'hover:bg-slate-50'}`}
                  >
                    <div className={`flex-shrink-0 ${cfg.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-800 truncate">{result.title}</p>
                      <p className="text-xs text-slate-500 truncate">{cfg.label} · {result.subtitle}</p>
                    </div>
                    {isSelected && <ArrowRight className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />}
                  </button>
                </li>
              );
            })}
          </ul>
        )}

        {/* Empty state */}
        {!loading && debouncedQuery.length >= 2 && results.length === 0 && (
          <p className="px-4 py-6 text-center text-sm text-slate-400">
            No se encontraron resultados para "<strong className="text-slate-600">{debouncedQuery}</strong>"
          </p>
        )}

        {/* Footer hint */}
        <div className="px-4 py-2 border-t border-slate-100 flex items-center gap-3 text-[11px] text-slate-400">
          <span><kbd className="font-mono bg-slate-100 px-1 rounded">↑↓</kbd> navegar</span>
          <span><kbd className="font-mono bg-slate-100 px-1 rounded">Enter</kbd> abrir</span>
          <span><kbd className="font-mono bg-slate-100 px-1 rounded">Esc</kbd> cerrar</span>
          <span className="ml-auto"><kbd className="font-mono bg-slate-100 px-1 rounded">Ctrl+K</kbd> búsqueda global</span>
        </div>
      </div>
    </div>
  );
}
