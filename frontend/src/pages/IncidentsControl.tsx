import React, { useState, useMemo, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { normalizeText } from '../utils/stringUtils';
import { useNotifications } from '../hooks/useNotifications';
import { usePermissions } from '../hooks/usePermissions';
import { useDebounce } from '../hooks/useDebounce';
import ModernSelect from '../components/ui/ModernSelect';
import IncidentClosureForm from '../components/IncidentClosureForm';
import IncidentDetail from './IncidentDetailView';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  EyeIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  PencilSquareIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

// --- Interfaces Estrictas ---
interface Incident {
  id: number;
  code: string;
  cliente: string;
  obra: string;
  estado: string;
  categoria?: string;
  subcategoria?: string;
  sap_doc_num?: number;
  sap_call_id?: number;
}

interface PaginatedResponse {
  results: Incident[];
  count: number;
  data?: {
    results: Incident[];
    count: number;
  };
}

interface FilterState {
  search: string;
  estado: string;
  categoria: string;
  start_year: string;
  end_year: string;
  page: number;
  page_size: number;
}

const Incidents: React.FC = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();
  const { canReopenIncidents, user } = usePermissions();

  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  const [activeModal, setActiveModal] = useState<'view' | 'close' | 'reopen' | 'delete' | null>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [isClosing, setIsClosing] = useState(false);

  const [filters, setFilters] = useState<FilterState>({
    search: '',
    estado: '',
    categoria: '',
    start_year: '',
    end_year: '',
    page: 1,
    page_size: 15,
  });

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    setFilters(prev => ({ ...prev, search: debouncedSearch, page: 1 }));
  }, [debouncedSearch]);

  const { data, isLoading, refetch } = useQuery<PaginatedResponse>({
    queryKey: ['incidents', filters],
    queryFn: async () => {
      // Sanitización profunda: Eliminamos parámetros vacíos para no interferir con la búsqueda icontains en el backend
      const cleanParams: any = {};
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== '' && value !== null && value !== undefined) {
          cleanParams[key] = value;
        }
      });
      
      const response = await incidentsAPI.list(cleanParams);
      return response.data || response;
    },
    staleTime: 30000,
  });

  const { incidents, totalCount } = useMemo(() => {
    let list: Incident[] = [];
    let count = 0;
    
    if (data) {
      if (Array.isArray(data)) {
        list = data;
        count = data.length;
      } else if (data.results) {
        list = data.results;
        count = data.count;
      } else if (data.data?.results) {
        list = data.data.results;
        count = data.data.count;
      }
    }
    return { incidents: list, totalCount: count };
  }, [data]);

  const handleExport = async () => {
    try {
      const response = await incidentsAPI.export(filters);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'incidencias.xlsx';
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
        if (matches?.[1]) filename = matches[1].replace(/['"]/g, '');
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      showSuccess('Reporte generado correctamente');
    } catch (error) {
      console.error("Export error:", error);
      showError('Error al exportar reporte');
    }
  };

  const handleAction = (incident: Incident, action: 'view' | 'close' | 'reopen' | 'delete', e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setSelectedIncident(incident);
    setActiveModal(action);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedIncident) return;
    try {
      await incidentsAPI.delete(selectedIncident.id);
      showSuccess(`Incidencia ${selectedIncident.code} eliminada`);
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      setActiveModal(null);
      refetch();
    } catch (error) {
      showError('Error al eliminar la incidencia');
    }
  };

  const handleClosureSubmit = async (formData: any) => {
    if (!selectedIncident) return;
    setIsClosing(true);
    try {
      const payload = new FormData();
      payload.append('stage', formData.stage);
      payload.append('closure_summary', formData.closure_summary);
      if (formData.closure_attachment) {
        payload.append('closure_attachment', formData.closure_attachment);
      }
      
      await incidentsAPI.close(selectedIncident.id, payload);
      showSuccess('Incidencia cerrada correctamente');
      queryClient.invalidateQueries({ queryKey: ['incidents'] });
      setActiveModal(null);
      refetch();
    } catch (error) {
      showError('Error al cerrar incidencia');
    } finally {
      setIsClosing(false);
    }
  };

  const handleReopenConfirm = async () => {
    if (!selectedIncident) return;
    try {
      await incidentsAPI.update(selectedIncident.id, {
        estado: 'abierta',
        closed_at: null,
        reopened_at: new Date().toISOString()
      });
      showSuccess('Incidencia reabierta exitosamente');
      setActiveModal(null);
      refetch();
    } catch (error) {
      showError('Error al reabrir incidencia');
    }
  };

  const getStatusBadge = (estado: string) => {
    const config = {
      'abierta': { bg: 'bg-blue-50', text: 'text-blue-600', dot: 'bg-blue-500', label: 'Abierta' },
      'en_progreso': { bg: 'bg-indigo-50', text: 'text-indigo-600', dot: 'bg-indigo-500', label: 'En Progreso' },
      'escalado': { bg: 'bg-amber-50', text: 'text-amber-600', dot: 'bg-amber-500', label: 'Escalado' },
      'cerrado': { bg: 'bg-emerald-50', text: 'text-emerald-600', dot: 'bg-emerald-500', label: 'Cerrado' },
      'cancelada': { bg: 'bg-slate-100', text: 'text-slate-500', dot: 'bg-slate-400', label: 'Cancelada' },
    }[estado?.toLowerCase()] || { bg: 'bg-slate-50', text: 'text-slate-600', dot: 'bg-slate-500', label: estado };

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-widest ${config.bg} ${config.text}`}>
        <span className={`w-1.5 h-1.5 rounded-full mr-2 ${config.dot}`}></span>
        {config.label}
      </span>
    );
  };

  return (
    <div className="relative min-h-screen pb-12 bg-slate-50/50">
      <div className="relative z-10 space-y-6 w-full max-w-[98%] mx-auto px-4 pt-6">

        {/* Toolbar Superior */}
        <div className="bg-white/70 backdrop-blur-xl rounded-[2rem] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white p-6">
          <div className="flex flex-col xl:flex-row items-center justify-between gap-6">

            <div className="flex items-center gap-4">
              <div className="w-2 h-10 bg-indigo-600 rounded-full shadow-lg shadow-indigo-200"></div>
              <div>
                <h1 className="text-2xl font-black text-slate-800 uppercase tracking-tight leading-none">
                  Gestión de <span className="text-indigo-600 font-extrabold">Incidencias</span>
                </h1>
              </div>
            </div>

            <div className="flex-1 w-full max-w-2xl relative group">
              <div className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-600 transition-colors">
                <MagnifyingGlassIcon className="h-5 w-5" />
              </div>
              <input
                type="text"
                className="block w-full pl-14 pr-6 py-4 bg-slate-100/50 border border-transparent rounded-[1.5rem] text-sm font-bold text-slate-700 placeholder:text-slate-400 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all shadow-inner"
                placeholder="Buscar por código, cliente, obra, categoría o folio SAP..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="flex items-center gap-4">
              <div className="w-[180px]">
                <ModernSelect
                  label="Tipo de Categoría"
                  value={filters.categoria}
                  onChange={(val) => setFilters(p => ({ ...p, categoria: val, page: 1 }))}
                  options={[
                    { value: '', label: 'Todas las áreas' },
                    { value: 'Tuberias PE', label: 'Tuberías PE' },
                    { value: 'Fitting Electrofusion', label: 'Fitting Electrofusión' },
                    { value: 'Fitting Mecanico', label: 'Fitting Mecánico' },
                    { value: 'Valvulas', label: 'Válvulas' },
                    { value: 'Herramientas', label: 'Herramientas' },
                  ]}
                />
              </div>

              <button
                onClick={() => refetch()}
                className="p-3.5 text-slate-400 hover:text-indigo-600 hover:bg-white rounded-2xl transition-all border border-slate-100 hover:shadow-xl group"
              >
                <ArrowPathIcon className={`w-6 h-6 ${isLoading ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
              </button>

              <button
                onClick={handleExport}
                className="px-6 py-3.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2 shadow-sm"
              >
                <ArrowDownTrayIcon className="w-5 h-5 text-slate-400" />
                <span className="hidden sm:inline">Exportar</span>
              </button>

              <button
                onClick={() => navigate('/incidents/new')}
                className="px-7 py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-[0_10px_20px_rgba(79,70,229,0.3)] transition-all flex items-center gap-2 hover:-translate-y-0.5"
              >
                <PlusIcon className="w-5 h-5" />
                <span className="hidden sm:inline">Nuevo Caso</span>
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-[3rem] shadow-[0_20px_50px_rgba(0,0,0,0.02)] border border-slate-100 overflow-hidden relative min-h-[650px]">
          {isLoading && (
            <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-white/60 backdrop-blur-md">
              <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4 shadow-2xl"></div>
              <p className="text-[10px] font-black text-indigo-600 uppercase tracking-widest animate-pulse">Sincronizando expedientes...</p>
            </div>
          )}

          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-slate-50/50">
                <th className="px-10 py-8 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em] border-b border-slate-100">expediente</th>
                <th className="px-8 py-8 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em] border-b border-slate-100">cliente & proyecto</th>
                <th className="px-8 py-8 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em] border-b border-slate-100">clasificación</th>
                <th className="px-8 py-8 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em] border-b border-slate-100">estado actual</th>
                <th className="px-10 py-8 text-center text-[11px] font-black text-slate-400 uppercase tracking-[0.3em] border-b border-slate-100">acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {incidents?.length > 0 ? incidents.map((inc) => (
                <tr 
                  key={inc.id} 
                  onClick={() => handleAction(inc, 'view')} 
                  className="group cursor-pointer hover:bg-slate-50/80 transition-all duration-300"
                >
                  <td className="px-10 py-7">
                    <div className="flex flex-col">
                      <span className="text-xl font-black text-indigo-600 group-hover:scale-105 transition-transform origin-left uppercase tracking-tighter">{inc.code}</span>
                      {(inc.sap_doc_num || inc.sap_call_id) && (
                        <span className="text-[10px] font-bold text-slate-400 mt-1 uppercase">SAP: {inc.sap_doc_num || inc.sap_call_id}</span>
                      )}
                    </div>
                  </td>
                  <td className="px-8 py-7">
                    <div className="flex flex-col">
                      <span className="text-sm font-black text-slate-800 uppercase leading-none mb-1.5">{inc.cliente}</span>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{inc.obra}</span>
                    </div>
                  </td>
                  <td className="px-8 py-7">
                    <div className="flex flex-col">
                      <span className="text-xs font-black text-slate-700 uppercase mb-1 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-indigo-200"></span>
                        {inc.categoria ? inc.categoria.replace(/_/g, ' ') : 'S/C'}
                      </span>
                      {inc.subcategoria && (
                        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-[0.1em] pl-4">
                          {inc.subcategoria}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-8 py-7">{getStatusBadge(inc.estado)}</td>
                  <td className="px-10 py-7">
                    <div className="flex items-center justify-center gap-3">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleAction(inc, 'view', e); }}
                        className="w-11 h-11 flex items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white transition-all shadow-sm hover:shadow-indigo-200"
                      >
                        <EyeIcon className="w-5 h-5" />
                      </button>

                      {inc.estado !== 'cerrado' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); navigate(`/incidents/${inc.id}/edit`); }}
                          className="w-11 h-11 flex items-center justify-center rounded-2xl bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all shadow-sm hover:shadow-blue-200"
                        >
                          <PencilSquareIcon className="w-5 h-5" />
                        </button>
                      )}

                      {inc.estado !== 'cerrado' && inc.estado !== 'cancelada' ? (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAction(inc, 'close', e); }}
                          className="w-11 h-11 flex items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm hover:shadow-emerald-200"
                        >
                          <CheckCircleIcon className="w-5 h-5" />
                        </button>
                      ) : (
                        inc.estado !== 'cancelada' && canReopenIncidents() && (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleAction(inc, 'reopen', e); }}
                            className="w-11 h-11 flex items-center justify-center rounded-2xl bg-amber-50 text-amber-600 hover:bg-amber-600 hover:text-white transition-all shadow-sm hover:shadow-amber-200"
                          >
                            <ArrowPathIcon className="w-5 h-5" />
                          </button>
                        )
                      )}

                      {(user?.role === 'admin' || user?.role === 'administrador' || user?.role === 'coordinador') && inc.estado !== 'cancelada' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAction(inc, 'delete', e); }}
                          className="w-11 h-11 flex items-center justify-center rounded-2xl bg-rose-50 text-rose-500 hover:bg-rose-500 hover:text-white transition-all shadow-sm hover:shadow-rose-200"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="py-40 text-center">
                    <div className="flex flex-col items-center justify-center text-slate-300">
                      <MagnifyingGlassIcon className="w-16 h-16 mb-4 opacity-50" />
                      <p className="font-black uppercase tracking-[0.3em] text-sm">Sin registros detectados</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {activeModal === 'view' && selectedIncident && (
          <PremiumModal onClose={() => setActiveModal(null)}>
            <IncidentDetail
              incidentId={selectedIncident.id.toString()}
              isModal={true}
              onClose={() => setActiveModal(null)}
            />
          </PremiumModal>
        )}

        {(activeModal === 'reopen' || activeModal === 'delete') && selectedIncident && (
          <div className="fixed inset-0 z-[10000] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xl transition-all">
            <div className="bg-white p-10 md:p-14 rounded-[3.5rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] max-w-md w-full text-center border border-white/20">
              <div className={`w-24 h-24 rounded-[2rem] flex items-center justify-center mx-auto mb-8 shadow-inner ${
                activeModal === 'reopen' ? 'bg-amber-50 text-amber-500' : 'bg-rose-50 text-rose-500'
              }`}>
                {activeModal === 'reopen' ? <ArrowPathIcon className="w-12 h-12" /> : <XMarkIcon className="w-12 h-12" />}
              </div>
              <h3 className="text-3xl font-black text-slate-900 mb-4 uppercase tracking-tighter">
                {activeModal === 'reopen' ? '¿Reactivar Caso?' : 'Desactivar Expediente'}
              </h3>
              <p className="text-sm text-slate-500 mb-10 leading-relaxed font-bold">
                {activeModal === 'reopen' 
                  ? `El expediente ${selectedIncident.code} volverá al estado "Abierta".`
                  : `¿Confirmas que deseas cancelar permanentemente el expediente ${selectedIncident.code}?`
                }
              </p>
              <div className="flex gap-4">
                <button 
                  onClick={() => setActiveModal(null)} 
                  className="flex-1 py-4.5 bg-slate-100 text-slate-600 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-slate-200 transition-colors"
                >
                  CANCELAR
                </button>
                <button 
                  onClick={activeModal === 'reopen' ? handleReopenConfirm : handleDeleteConfirm} 
                  className={`flex-1 py-4.5 text-white rounded-2xl font-black text-xs border-b-4 transition-all uppercase tracking-widest active:border-b-0 ${
                    activeModal === 'reopen' 
                      ? 'bg-amber-500 border-amber-700 hover:bg-amber-600' 
                      : 'bg-slate-900 border-slate-700 hover:bg-black'
                  }`}
                >
                  {activeModal === 'reopen' ? 'REABRIR AHORA' : 'CONCLUIR'}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeModal === 'close' && selectedIncident && (
          <IncidentClosureForm
            incident={selectedIncident}
            onSubmit={handleClosureSubmit}
            onCancel={() => setActiveModal(null)}
            isClosing={isClosing}
          />
        )}

      </div>
    </div >
  );
};

const PremiumModal: React.FC<{ children: React.ReactNode; onClose: () => void; maxWidth?: string }> = ({ 
  children, 
  onClose, 
  maxWidth = "max-w-7xl" 
}) => {
  return createPortal(
    <div className="fixed inset-0 z-[10000] flex items-center justify-center p-4 md:p-6 bg-slate-900/60 backdrop-blur-xl transition-all">
      <div
        className={`bg-white w-[98%] md:w-full ${maxWidth} max-h-[92vh] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] rounded-[3rem] overflow-hidden flex flex-col border border-white/20`}
        onClick={e => e.stopPropagation()}
      >
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {children}
        </div>
      </div>
    </div>,
    document.body
  );
};

export default Incidents;
