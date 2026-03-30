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
import { exportIncidents } from '../utils/exportUtils';
import IncidentClosureForm from '../components/IncidentClosureForm';
import IncidentImages from '../components/IncidentImages';
import IncidentAttachments from '../components/IncidentAttachments';
import IncidentDetail from './IncidentDetailView';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  PaperClipIcon,
  TrashIcon,
  XMarkIcon,
  EyeIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  PencilSquareIcon
} from '@heroicons/react/24/outline';

const Incidents = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();
  const { canReopenIncidents, user } = usePermissions();

  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  const [activeModal, setActiveModal] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [isClosing, setIsClosing] = useState(false);

  const [filters, setFilters] = useState({
    search: '',
    estado: '',
    start_year: '',
    end_year: '',
    page: 1,
    page_size: 10,
  });

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    setFilters(prev => ({ ...prev, search: normalizeText(debouncedSearch), page: 1 }));
  }, [debouncedSearch]);


  const { data, isLoading, refetch } = useQuery({
    queryKey: ['incidents', filters],
    queryFn: async () => {
      const response = await incidentsAPI.list(filters);
      return response.data || response;
    },
    keepPreviousData: true,
    staleTime: 30000,
  });

  const { incidents, totalCount } = useMemo(() => {
    let incidentsList = [];
    let count = 0;
    if (data) {
      if (Array.isArray(data)) {
        incidentsList = data; count = data.length;
      } else if (data.results) {
        incidentsList = data.results; count = data.count || data.results.length;
      } else if (data.data?.results) {
        incidentsList = data.data.results; count = data.data.count || data.data.results.length;
      } else if (data.data?.incidents) {
        incidentsList = data.data.incidents; count = data.data.count || data.data.incidents.length;
      }
    }
    return { incidents: incidentsList, totalCount: count };
  }, [data]);

  const handleExport = async () => {
    try {
      const response = await incidentsAPI.export(filters);
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      // Get filename from header or default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'incidencias.xlsx';
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
        if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
      }
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      showSuccess('Reporte generado correctamente');
    } catch (error) {
      console.error("Export error:", error);
      showError('Error al exportar reporte. Intente nuevamente.');
    }
  };

  const handleAction = (incident, action, e) => {
    if (e) e.stopPropagation();
    setSelectedIncident(incident);
    setActiveModal(action);
  };

  const handleViewDetail = (incident, e) => {
    if (e) e.stopPropagation();
    setSelectedIncident(incident);
    setActiveModal('view');
  };

  const handleDeleteConfirm = async () => {
    if (!selectedIncident) return;
    try {
      await incidentsAPI.delete(selectedIncident.id);
      showSuccess(`Incidencia ${selectedIncident.code} eliminada`);
      queryClient.invalidateQueries(['incidents-search']);
      setActiveModal(null);
      refetch();
    } catch (error) {
      showError('Error al eliminar la incidencia');
    }
  };

  const handleClosureSubmit = async (formData) => {
    if (!selectedIncident) return;
    setIsClosing(true);
    try {
      // Usar FormData para soportar carga de archivos adjuntos si existen
      const payload = new FormData();
      payload.append('stage', formData.stage);
      payload.append('closure_summary', formData.closure_summary);
      if (formData.closure_attachment) {
        payload.append('closure_attachment', formData.closure_attachment);
      }
      
      await incidentsAPI.close(selectedIncident.id, payload);
      showSuccess('Incidencia cerrada correctamente');
      queryClient.invalidateQueries(['incidents-search']);
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

  const getStatusBadge = (estado) => {
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

  const PremiumModal = ({ children, onClose, maxWidth = "max-w-6xl" }) => {
    return createPortal(
      <div className="fixed inset-0 z-[10000] flex items-center justify-center p-4 md:p-6 bg-slate-900/60 backdrop-blur-md transition-all">
        <div
          className={`bg-white w-[95%] md:w-full ${maxWidth} max-h-[85vh] md:max-h-[90vh] shadow-2xl rounded-[2rem] lg:rounded-[3rem] overflow-hidden flex flex-col border border-white/20`}
          onClick={e => e.stopPropagation()}
        >
          <div className="flex-1 overflow-y-auto">
            {children}
          </div>
        </div>
      </div>,
      document.body
    );
  };

  return (
    <div className="relative min-h-screen pb-12 bg-slate-50">
      <div className="relative z-10 space-y-4 w-full max-w-[98%] mx-auto px-3 pt-3">

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
          <div className="flex flex-col xl:flex-row items-center justify-between gap-4">

            {/* Title Area */}
            <div className="flex items-center gap-3 min-w-fit">
              <div className="w-1.5 h-8 bg-indigo-600 rounded-full"></div>
              <div>
                <h1 className="text-xl font-black text-slate-800 uppercase tracking-tight">
                  Centro de <span className="text-indigo-600">Incidencias</span>
                </h1>
              </div>
            </div>

            {/* Central Search Bar */}
            <div className="flex-1 w-full max-w-3xl relative group mx-4">
              <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
              <input
                type="text"
                className="block w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700 placeholder:text-slate-400 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
                placeholder="Buscar por Código, Cliente, Obra..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Actions Toolbar */}
            <div className="flex items-center gap-3 min-w-fit">
              <div className="w-[160px]">
                <ModernSelect
                  label="Categoría"
                  value={filters.categoria}
                  onChange={(val) => setFilters(p => ({ ...p, categoria: val, page: 1 }))}
                  options={[
                    { value: '', label: 'Todas' },
                    { value: 'calidad_interna', label: 'Calidad Interna' },
                    { value: 'calidad_cliente', label: 'Calidad Cliente' },
                    { value: 'postventa', label: 'Postventa' },
                    { value: 'seguridad', label: 'Seguridad' },
                  ]}
                />
              </div>

              <button
                onClick={refetch}
                className="p-2.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all border border-transparent hover:border-indigo-100"
                title="Actualizar Datos"
              >
                <ArrowPathIcon className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              </button>

              <div className="h-8 w-px bg-slate-100 mx-1"></div>

              <button
                onClick={handleExport}
                className="px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2 shadow-sm"
                title="Descargar Reporte Excel"
              >
                <ArrowDownTrayIcon className="w-4 h-4 text-slate-400" />
                <span className="hidden sm:inline">Exportar</span>
              </button>

              <button
                onClick={() => navigate('/incidents/new')}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-indigo-600/20 transition-all flex items-center gap-2"
              >
                <PlusIcon className="w-4 h-4" />
                <span className="hidden sm:inline">Nuevo Caso</span>
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-[3rem] shadow-2xl shadow-slate-200/40 border border-slate-100 overflow-x-auto relative min-h-[600px]">
          {isLoading && (
            <div className="absolute inset-0 z-20 flex items-center justify-center bg-white/70 backdrop-blur-sm">
              <div className="w-14 h-14 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
          <table className="w-full">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-100">
                <th className="px-10 py-7 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">código</th>
                <th className="px-8 py-7 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">detalle cliente</th>
                <th className="px-8 py-7 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">clasificación</th>
                <th className="px-8 py-7 text-left text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">estado actual</th>
                <th className="px-10 py-7 text-center text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">operaciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {incidents?.length > 0 ? incidents.map((inc) => (
                <tr 
                  key={inc.id} 
                  onClick={() => handleViewDetail(inc)} 
                  className="group cursor-pointer hover:bg-indigo-50/20 transition-all"
                >
                  <td className="px-10 py-6">
                    <span className="text-lg font-black text-indigo-600 group-hover:text-indigo-800 transition-colors uppercase tracking-tight">{inc.code}</span>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex flex-col">
                      <span className="text-sm font-black text-slate-800 uppercase leading-none mb-1.5">{inc.cliente}</span>
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{inc.obra}</span>
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex flex-col">
                      <span className="text-xs font-bold text-slate-700 uppercase mb-1">
                        {inc.categoria ? inc.categoria.replace(/_/g, ' ') : 'S/C'}
                      </span>
                      {inc.subcategoria && (
                        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide">
                          {inc.subcategoria}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-8 py-6">{getStatusBadge(inc.estado)}</td>
                  <td className="px-10 py-6">
                    <div className="flex items-center justify-center gap-3">
                      <button
                        onClick={(e) => handleViewDetail(inc, e)}
                        className="w-12 h-12 flex items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600 hover:bg-indigo-600 hover:text-white transition-all shadow-sm"
                        title="Explorar Detalle"
                      >
                        <EyeIcon className="w-6 h-6" />
                      </button>

                      {inc.estado !== 'cerrado' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); navigate(`/incidents/${inc.id}/edit`); }}
                          className="w-12 h-12 flex items-center justify-center rounded-2xl bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all shadow-sm"
                          title="Editar Incidencia"
                        >
                          <PencilSquareIcon className="w-6 h-6" />
                        </button>
                      )}

                      {inc.estado !== 'cerrado' && inc.estado !== 'cancelada' ? (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAction(inc, 'close', e); }}
                          className="w-12 h-12 flex items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white transition-all shadow-sm"
                          title="Cerrar Incidencia"
                        >
                          <CheckCircleIcon className="w-6 h-6" />
                        </button>
                      ) : (
                        inc.estado !== 'cancelada' && canReopenIncidents() && (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleAction(inc, 'reopen', e); }}
                            className="w-12 h-12 flex items-center justify-center rounded-2xl bg-amber-50 text-amber-600 hover:bg-amber-600 hover:text-white transition-all shadow-sm"
                            title="Reabrir Incidencia"
                          >
                            <ArrowPathIcon className="w-6 h-6" />
                          </button>
                        )
                      )}

                      {(user?.role === 'admin' || user?.role === 'administrador' || user?.role === 'coordinador') && inc.estado !== 'cancelada' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAction(inc, 'delete', e); }}
                          className="w-12 h-12 flex items-center justify-center rounded-2xl bg-rose-50 text-rose-500 hover:bg-rose-500 hover:text-white transition-all shadow-sm"
                          title="Cancelar Incidencia"
                        >
                          <TrashIcon className="w-6 h-6" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="4" className="py-32 text-center text-slate-300 font-black uppercase tracking-widest text-sm">
                    No se han detectado registros en la base de datos
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {activeModal === 'view' && selectedIncident && (
          <PremiumModal onClose={() => setActiveModal(null)}>
            <IncidentDetail
              incidentId={selectedIncident.id}
              isModal={true}
              onClose={() => setActiveModal(null)}
            />
          </PremiumModal>
        )}

        {activeModal === 'reopen' && selectedIncident && (
          <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-slate-900/50 backdrop-blur-md">
            <div className="bg-white p-12 rounded-[3.5rem] shadow-2xl max-w-md w-full text-center border border-white">
              <div className="w-24 h-24 bg-amber-50 text-amber-500 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
                <ArrowPathIcon className="w-12 h-12" />
              </div>
              <h3 className="text-3xl font-black text-slate-900 mb-4 uppercase tracking-tighter">¿Reactivar Caso?</h3>
              <p className="text-sm text-slate-500 mb-10 leading-relaxed font-bold">El expediente <span className="text-amber-600">{selectedIncident.code}</span> volverá al estado "Abierta".</p>
              <div className="flex gap-4">
                <button onClick={() => setActiveModal(null)} className="flex-1 py-4 bg-slate-100 text-slate-600 rounded-2xl font-black text-xs uppercase tracking-widest">CANCELAR</button>
                <button onClick={handleReopenConfirm} className="flex-1 py-4 bg-amber-500 text-white rounded-2xl font-black text-xs border-b-4 border-amber-700 active:border-b-0 transition-all uppercase tracking-widest">REABRIR</button>
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

        {activeModal === 'delete' && selectedIncident && (
          <div className="fixed inset-0 z-[10000] flex items-center justify-center bg-slate-900/50 backdrop-blur-md">
            <div className="bg-white p-12 rounded-[3.5rem] shadow-2xl max-w-md w-full text-center border border-white">
              <div className="w-24 h-24 bg-slate-50 text-slate-500 rounded-full flex items-center justify-center mx-auto mb-8">
                <XMarkIcon className="w-12 h-12" />
              </div>
              <h3 className="text-3xl font-black text-slate-900 mb-4 uppercase tracking-tighter">CANCELAR INCIDENCIA</h3>
              <p className="text-sm text-slate-600 mb-10 leading-relaxed">¿Confirmas que deseas cancelar permanentemente el expediente <span className="font-bold text-slate-900">{selectedIncident.code}</span>?</p>
              <div className="flex gap-4">
                <button onClick={() => setActiveModal(null)} className="flex-1 py-4 bg-slate-100 text-slate-600 rounded-2xl font-black text-xs uppercase tracking-widest">REGRESAR</button>
                <button onClick={handleDeleteConfirm} className="flex-1 py-4 bg-slate-900 text-white rounded-2xl font-black text-xs border-b-4 border-slate-700 active:border-b-0 transition-all uppercase tracking-widest">CANCELAR AHORA</button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div >
  );
};

export default Incidents;
