import React, { useState, useMemo, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { normalizeText } from '../utils/stringUtils';
import { useNotifications } from '../hooks/useNotifications';
import { useDebounce } from '../hooks/useDebounce';
import { exportIncidents } from '../utils/exportUtils';
import IncidentAttachments from '../components/IncidentAttachments';
import IncidentImages from '../components/IncidentImages';
import IncidentClosureForm from '../components/IncidentClosureForm';
import { useAuth } from '../hooks/useAuth';
import {
  PlusIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  TrashIcon,
  PaperClipIcon,
  XMarkIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ArrowDownTrayIcon,
  PhotoIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

const Incidents = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();

  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 500);

  const [filters, setFilters] = useState({
    search: '',
    estado: '',
    categoria: '',
    page: 1,
    page_size: 20,
  });

  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    setFilters(prev => ({ ...prev, search: normalizeText(debouncedSearch) }));
  }, [debouncedSearch]);

  const [selectedIncident, setSelectedIncident] = useState(null);
  const [activeModal, setActiveModal] = useState(null);

  const { data: dashboardData } = useQuery({
    queryKey: ['incidents-dashboard'],
    queryFn: () => incidentsAPI.dashboard(),
  });

  const kpis = dashboardData?.data?.kpis || {
    total_incidents: 0,
    open_incidents: 0,
    closed_incidents: 0
  };

  const statusDist = dashboardData?.data?.status_distribution || [];
  const getStatusCount = (statusName) => {
    const item = statusDist.find(d => d.estado === statusName);
    return item ? item.count : 0;
  };

  const labCount = getStatusCount('laboratorio') + getStatusCount('calidad') + getStatusCount('reporte_visita');
  const providerCount = getStatusCount('proveedor');

  const { data, isLoading, error } = useQuery({
    queryKey: ['incidents', filters],
    queryFn: () => incidentsAPI.list(filters),
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

  const totalPages = Math.ceil(totalCount / filters.page_size);
  const startIndex = (filters.page - 1) * filters.page_size + 1;
  const endIndex = Math.min(filters.page * filters.page_size, totalCount);

  const handleFilterChange = (key, value) => {
    if (key === 'search') setSearchTerm(value);
    else setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setFilters(prev => ({ ...prev, page: newPage }));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleViewDetails = async (incident) => {
    try {
      const response = await incidentsAPI.get(incident.id);
      setSelectedIncident(response.data || response);
      setActiveModal('detail');
    } catch (err) {
      setSelectedIncident(incident);
      setActiveModal('detail');
    }
  };

  const handleRefresh = () => {
    queryClient.invalidateQueries(['incidents']);
    showSuccess('Datos actualizados');
  };

  const handleDelete = (incident) => {
    setSelectedIncident(incident);
    setActiveModal('delete');
  };

  const handleViewAttachments = (incident) => {
    setSelectedIncident(incident);
    setActiveModal('attachments');
  };

  const handleViewImages = (incident) => {
    setSelectedIncident(incident);
    setActiveModal('images');
  };

  const handleReopen = async (incident) => {
    try {
      await incidentsAPI.reopen(incident.id);
      queryClient.invalidateQueries(['incidents']);
      showSuccess('Incidencia reabierta');
    } catch (err) {
      showError('Error al reabrir: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleClose = (incident) => {
    setSelectedIncident(incident);
    setActiveModal('close');
  };

  const handleClosureSubmit = async (formData) => {
    setIsClosing(true);
    try {
      let attachmentPath = '';
      if (formData.closure_attachment) {
        const fileData = new FormData();
        fileData.append('file', formData.closure_attachment);
        fileData.append('title', `Cierre: ${formData.closure_attachment.name}`);
        const uploadResponse = await incidentsAPI.uploadAttachment(selectedIncident.id, fileData);
        attachmentPath = uploadResponse.data?.file_path || uploadResponse.data?.filename || formData.closure_attachment.name;
      }

      await incidentsAPI.close(selectedIncident.id, {
        stage: formData.stage,
        closure_summary: formData.closure_summary,
        closure_attachment: attachmentPath,
        closure_date: formData.closure_date
      });

      queryClient.invalidateQueries(['incidents']);
      showSuccess('Incidencia cerrada correctamente');
      setActiveModal(null);
      setSelectedIncident(null);
    } catch (err) {
      showError('Error al cerrar: ' + (err.response?.data?.error || err.message));
    } finally {
      setIsClosing(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedIncident) return;
    try {
      await incidentsAPI.delete(selectedIncident.id);
      queryClient.invalidateQueries(['incidents']);
      showSuccess('Registro eliminado');
    } catch (err) {
      showError('Error al eliminar: ' + (err.response?.data?.error || err.message));
    } finally {
      setActiveModal(null);
      setSelectedIncident(null);
    }
  };

  const getStatusBadge = (incident) => {
    let label = 'Abierto';
    let color = 'bg-blue-100 text-blue-800';
    if (incident.estado === 'cerrado') {
      label = 'Cerrado'; color = 'bg-green-100 text-green-800';
    } else if (incident.estado === 'proveedor' || incident.escalated_to_supplier) {
      label = 'Proveedor'; color = 'bg-orange-100 text-orange-800';
    } else if (incident.estado === 'calidad' || incident.escalated_to_quality || incident.estado === 'laboratorio') {
      label = 'Laboratorio'; color = 'bg-purple-100 text-purple-800';
    } else if (incident.estado === 'reporte_visita') {
      label = 'Auditoría'; color = 'bg-indigo-100 text-indigo-800';
    }
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${color}`}>
        {label}
      </span>
    );
  };

  const getPriorityBadge = (prioridad) => {
    const map = {
      baja: 'bg-gray-100 text-gray-800',
      media: 'bg-blue-100 text-blue-800',
      alta: 'bg-orange-100 text-orange-800',
      critica: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${map[prioridad] || 'bg-gray-100 text-gray-800'}`}>
        {prioridad}
      </span>
    );
  };

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center p-20 space-y-4">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <div className="text-gray-500 font-medium">Cargando incidencias...</div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Listado de Incidencias</h1>
          <p className="text-gray-500">Gestión y seguimiento de protocolos de postventa.</p>
        </div>

        <div className="flex flex-wrap gap-3">
          <button onClick={() => exportIncidents(incidents, 'incidencias')} className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
            <ArrowDownTrayIcon className="w-4 h-4" />
            Exportar
          </button>
          <button onClick={handleRefresh} className="p-2 text-gray-500 hover:text-blue-600 bg-gray-50 rounded-lg">
            <ArrowPathIcon className="w-5 h-5" />
          </button>
          <Link to="/incidents/new" className="flex items-center gap-2 px-6 py-2 text-sm font-bold text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm transition-all">
            <PlusIcon className="w-5 h-5" />
            Nueva Incidencia
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Total', val: kpis.total_incidents, color: 'text-gray-900', bg: 'bg-gray-50' },
          { label: 'Abiertas', val: kpis.open_incidents, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Laboratorio', val: labCount, color: 'text-purple-600', bg: 'bg-purple-50' },
          { label: 'Proveedor', val: providerCount, color: 'text-orange-600', bg: 'bg-orange-50' },
          { label: 'Cerradas', val: kpis.closed_incidents, color: 'text-green-600', bg: 'bg-green-50' }
        ].map((k, i) => (
          <div key={i} className={`p-4 rounded-xl border border-gray-100 ${k.bg} shadow-sm`}>
            <p className="text-xs font-semibold text-gray-500 uppercase mb-1 tracking-wider">{k.label}</p>
            <span className={`text-2xl font-bold ${k.color}`}>{k.val}</span>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por cliente, código o descripción..."
            value={searchTerm}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="w-full bg-gray-50 border-gray-200 rounded-lg pl-10 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="flex gap-4">
          <select
            value={filters.estado}
            onChange={(e) => handleFilterChange('estado', e.target.value)}
            className="bg-white border-gray-200 rounded-lg text-sm text-gray-600 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Todos los estados</option>
            <option value="abierto">Abierto</option>
            <option value="calidad">Laboratorio</option>
            <option value="proveedor">Proveedor</option>
            <option value="cerrado">Cerrado</option>
          </select>
          <select
            value={filters.categoria}
            onChange={(e) => handleFilterChange('categoria', e.target.value)}
            className="bg-white border-gray-200 rounded-lg text-sm text-gray-600 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Todas las categorías</option>
            <option value="tuberia_beta">Tubería BETA</option>
            <option value="tuberia_ppr">Tubería PPR</option>
            <option value="tuberia_hdpe">Tubería HDPE</option>
            <option value="fitting_beta">Fitting BETA</option>
            <option value="fitting_ppr">Fitting PPR</option>
            <option value="fitting_hdpe">Fitting HDPE</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Código</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Cliente</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Categoría</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Prioridad</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">Fecha</th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {incidents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-20 text-center text-gray-400 font-medium">No se encontraron incidencias.</td>
                </tr>
              ) : incidents.map(inc => (
                <tr key={inc.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-bold text-gray-900">{inc.code}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900 truncate max-w-[200px]">{inc.cliente}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {inc.categoria?.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4">{getStatusBadge(inc)}</td>
                  <td className="px-6 py-4">{getPriorityBadge(inc.prioridad)}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 tabular-nums">
                    {new Date(inc.fecha_deteccion || inc.fecha_reporte).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button onClick={() => handleViewDetails(inc)} className="p-1.5 text-gray-400 hover:text-blue-600 bg-white border border-gray-200 rounded-md hover:border-blue-200 transition-all">
                        <EyeIcon className="w-5 h-5" />
                      </button>
                      <button onClick={() => navigate(`/incidents/${inc.id}/edit`)} className="p-1.5 text-gray-400 hover:text-blue-600 bg-white border border-gray-200 rounded-md hover:border-blue-200 transition-all">
                        <ArrowPathIcon className="w-5 h-5" />
                      </button>
                      {inc.estado !== 'cerrado' ? (
                        <button onClick={() => handleClose(inc)} className="p-1.5 text-gray-400 hover:text-green-600 bg-white border border-gray-200 rounded-md hover:border-green-200 transition-all">
                          <CheckCircleIcon className="w-5 h-5" />
                        </button>
                      ) : (
                        <button onClick={() => handleReopen(inc)} className="p-1.5 text-gray-400 hover:text-orange-600 bg-white border border-gray-200 rounded-md hover:border-orange-200 transition-all">
                          <ArrowPathIcon className="w-5 h-5" />
                        </button>
                      )}
                      {user?.role === 'admin' && (
                        <button onClick={() => handleDelete(inc)} className="p-1.5 text-gray-400 hover:text-red-600 bg-white border border-gray-200 rounded-md hover:border-red-200 transition-all">
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="text-sm text-gray-600">
            Mostrando <span className="font-semibold text-gray-900">{startIndex}-{endIndex}</span> de <span className="font-semibold text-gray-900">{totalCount}</span>
          </div>

          <div className="flex items-center gap-4">
            <select
              value={filters.page_size}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              className="text-sm bg-white border-gray-200 rounded-lg text-gray-600 py-1"
            >
              {[10, 20, 50, 100].map(v => <option key={v} value={v}>{v} por página</option>)}
            </select>

            <div className="flex items-center gap-2">
              <button
                onClick={() => handlePageChange(filters.page - 1)}
                disabled={filters.page === 1}
                className="p-1.5 text-gray-500 hover:bg-white border border-transparent hover:border-gray-200 rounded-md disabled:opacity-30"
              >
                <ChevronLeftIcon className="w-5 h-5" />
              </button>
              <span className="text-sm font-medium text-gray-700">Página {filters.page} de {totalPages}</span>
              <button
                onClick={() => handlePageChange(filters.page + 1)}
                disabled={filters.page === totalPages}
                className="p-1.5 text-gray-500 hover:bg-white border border-transparent hover:border-gray-200 rounded-md disabled:opacity-30"
              >
                <ChevronRightIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {activeModal === 'detail' && selectedIncident && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600/50 backdrop-blur-sm">
          <div className="bg-white w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col rounded-2xl shadow-2xl animate-scale-in">
            <div className="px-8 py-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <div>
                <h3 className="text-xl font-bold text-gray-900">Detalle de Incidencia</h3>
                <p className="text-sm text-gray-500 uppercase tracking-wider font-semibold">Código: {selectedIncident.code}</p>
              </div>
              <button onClick={() => setActiveModal(null)} className="p-2 text-gray-400 hover:text-gray-600"><XMarkIcon className="w-6 h-6" /></button>
            </div>

            <div className="p-8 overflow-y-auto flex-1">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-6">
                  <div>
                    <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Descripción de la incidencia</h4>
                    <div className="bg-gray-50 p-6 rounded-xl border border-gray-100 text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {selectedIncident.description || 'Sin descripción detallada.'}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl border border-gray-100">
                      <p className="text-xs font-bold text-gray-400 uppercase mb-1">Categoría</p>
                      <p className="font-semibold text-gray-900">{selectedIncident.categoria?.replace(/_/g, ' ')}</p>
                    </div>
                    <div className="p-4 rounded-xl border border-gray-100">
                      <p className="text-xs font-bold text-gray-400 uppercase mb-1">Subcategoría</p>
                      <p className="font-semibold text-gray-900">{selectedIncident.subcategoria || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-gray-50 p-6 rounded-xl border border-gray-100 space-y-4">
                    <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest border-b border-gray-200 pb-2">Estado del Proceso</h4>
                    <div className="space-y-4">
                      <div>
                        <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Prioridad Actual</p>
                        {getPriorityBadge(selectedIncident.prioridad)}
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Estado Operativo</p>
                        {getStatusBadge(selectedIncident)}
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Fecha de Registro</p>
                        <p className="text-sm font-semibold text-gray-900">{new Date(selectedIncident.fecha_deteccion).toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Responsable</p>
                        <p className="text-sm font-semibold text-blue-600">{selectedIncident.responsable?.replace(/_/g, ' ')}</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-3">
                    <button onClick={() => handleViewAttachments(selectedIncident)} className="flex items-center justify-center gap-2 w-full py-2.5 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors">
                      <PaperClipIcon className="w-4 h-4" /> Adjuntos
                    </button>
                    <button onClick={() => handleViewImages(selectedIncident)} className="flex items-center justify-center gap-2 w-full py-2.5 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors">
                      <PhotoIcon className="w-4 h-4" /> Fotos
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div className="px-8 py-5 bg-gray-50 border-t border-gray-100 flex gap-4">
              <button onClick={() => navigate(`/incidents/${selectedIncident.id}/edit`)} className="px-6 py-2 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 transition-all">Editar Información</button>
              <button onClick={() => setActiveModal(null)} className="px-6 py-2 bg-white text-gray-600 border border-gray-300 rounded-lg font-bold hover:bg-gray-50 transition-all ml-auto">Cerrar Vista</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {activeModal === 'delete' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600/50 backdrop-blur-sm">
          <div className="bg-white max-w-md w-full p-8 rounded-2xl shadow-2xl text-center space-y-6">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Eliminar Registro</h3>
              <p className="text-gray-500 text-sm">¿Estás seguro de que deseas eliminar permanentemente la incidencia <span className="font-bold text-gray-900">{selectedIncident.code}</span>? Esta acción es irreversible.</p>
            </div>
            <div className="flex gap-4">
              <button onClick={() => setActiveModal(null)} className="flex-1 px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-xl font-bold hover:bg-gray-50">Cancelar</button>
              <button onClick={handleDeleteConfirm} className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 shadow-sm">Confirmar</button>
            </div>
          </div>
        </div>
      )}

      {/* Attachments / Images (Lazy usage) */}
      {activeModal === 'attachments' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600/50 backdrop-blur-sm">
          <div className="bg-white w-full max-w-4xl max-h-[80vh] flex flex-col rounded-2xl shadow-2xl p-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-900">Documentos Adjuntos</h3>
              <button onClick={() => setActiveModal(null)} className="p-1 text-gray-400 hover:text-gray-600"><XMarkIcon className="w-6 h-6" /></button>
            </div>
            <div className="flex-1 overflow-y-auto">
              <IncidentAttachments incidentId={selectedIncident.id} incidentCode={selectedIncident.code} onUpdate={() => queryClient.invalidateQueries(['incidents'])} />
            </div>
          </div>
        </div>
      )}

      {activeModal === 'images' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600/50 backdrop-blur-sm">
          <div className="bg-white w-full max-w-5xl max-h-[90vh] flex flex-col rounded-2xl shadow-2xl p-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-900">Galería de Imágenes</h3>
              <button onClick={() => setActiveModal(null)} className="p-1 text-gray-400 hover:text-gray-600"><XMarkIcon className="w-6 h-6" /></button>
            </div>
            <div className="flex-1 overflow-y-auto">
              <IncidentImages incidentId={selectedIncident.id} onClose={() => setActiveModal(null)} incident={selectedIncident} />
            </div>
          </div>
        </div>
      )}

      {/* Final Closure Modal */}
      {activeModal === 'close' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-600/50 backdrop-blur-sm">
          <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden border border-green-50">
            <div className="p-8">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">Cierre de Incidencia</h3>
                  <p className="text-sm text-gray-500 mt-1">Finalización formal del proceso de garantía.</p>
                </div>
                <button onClick={() => setActiveModal(null)} className="text-gray-400 hover:text-gray-600"><XMarkIcon className="w-6 h-6" /></button>
              </div>
              <IncidentClosureForm onSubmit={handleClosureSubmit} onCancel={() => setActiveModal(null)} isDisabled={isClosing} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Incidents;
