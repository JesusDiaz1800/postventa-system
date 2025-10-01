import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';
import IncidentAttachments from '../components/IncidentAttachments';
import IncidentImages from '../components/IncidentImages';
import {
  PlusIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  PaperClipIcon,
  XMarkIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const Incidents = () => {
  console.log('=== INCIDENTS COMPONENT LOADED ===');
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  
  const [filters, setFilters] = useState({
    search: '',
    estado: '',
    prioridad: '',
  });
  
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showAttachmentsModal, setShowAttachmentsModal] = useState(false);
  const [showImagesModal, setShowImagesModal] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['incidents', filters],
    queryFn: () => incidentsAPI.list(filters),
  });

  // Debug logging
  console.log('=== INCIDENTS DEBUG ===');
  console.log('Data:', data);
  console.log('IsLoading:', isLoading);
  console.log('Error:', error);

  // Handle different response formats
  let incidents = [];
  let totalCount = 0;
  
  if (data) {
    console.log('Processing data structure:', data);
    if (Array.isArray(data)) {
      // Direct array response
      console.log('Using direct array response');
      incidents = data;
      totalCount = data.length;
    } else if (data.results && Array.isArray(data.results)) {
      // Paginated response
      console.log('Using paginated response');
      incidents = data.results;
      totalCount = data.count || data.results.length;
    } else if (data.data && Array.isArray(data.data)) {
      // Alternative data wrapper
      console.log('Using data.data array');
      incidents = data.data;
      totalCount = data.data.length;
    } else if (data.data && data.data.results && Array.isArray(data.data.results)) {
      // Nested data.results structure
      console.log('Using nested data.data.results');
      incidents = data.data.results;
      totalCount = data.data.count || data.data.results.length;
    } else if (data.data && typeof data.data === 'object') {
      // Check if data.data has incidents array
      console.log('Checking data.data structure:', data.data);
      if (data.data.incidents && Array.isArray(data.data.incidents)) {
        console.log('Using data.data.incidents');
        incidents = data.data.incidents;
        totalCount = data.data.count || data.data.incidents.length;
      } else if (Array.isArray(data.data)) {
        console.log('Using data.data as array');
        incidents = data.data;
        totalCount = data.data.length;
      }
    }
    
    console.log('Final incidents array:', incidents);
    console.log('Final incidents count:', incidents.length);
  }
  

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // Action handlers
  const handleViewDetails = (incident) => {
    setSelectedIncident(incident);
    setShowDetailModal(true);
  };

  const handleEdit = (incident) => {
    setSelectedIncident(incident);
    setShowEditModal(true);
  };

  const handleDelete = (incident) => {
    setSelectedIncident(incident);
    setShowDeleteModal(true);
  };

  const handleViewAttachments = (incident) => {
    setSelectedIncident(incident);
    setShowAttachmentsModal(true);
  };

  const handleViewImages = (incident) => {
    setSelectedIncident(incident);
    setShowImagesModal(true);
  };

  const handleReopen = async (incident) => {
    try {
      await incidentsAPI.reopen(incident.id);
      queryClient.invalidateQueries(['incidents']);
      showSuccess('Incidencia reabierta exitosamente');
    } catch (error) {
      console.error('Error reopening incident:', error);
      showError('Error al reabrir la incidencia: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedIncident) return;
    
    try {
      await incidentsAPI.delete(selectedIncident.id);
      // Refresh the incidents list using React Query instead of page reload
      queryClient.invalidateQueries(['incidents']);
      showSuccess('Incidencia eliminada exitosamente');
    } catch (error) {
      console.error('Error deleting incident:', error);
      showError('Error al eliminar la incidencia: ' + (error.response?.data?.error || error.message));
    } finally {
      setShowDeleteModal(false);
      setSelectedIncident(null);
    }
  };

  const handleEditSave = async (updatedData) => {
    if (!selectedIncident) return;
    
    try {
      await incidentsAPI.update(selectedIncident.id, updatedData);
      // Refresh the incidents list using React Query
      queryClient.invalidateQueries(['incidents']);
      showSuccess('Incidencia actualizada exitosamente');
    } catch (error) {
      console.error('Error updating incident:', error);
      showError('Error al actualizar la incidencia: ' + (error.response?.data?.error || error.message));
    } finally {
      setShowEditModal(false);
      setSelectedIncident(null);
    }
  };

  const getStatusBadge = (incident) => {
    // Determinar el estado simplificado basado en el estado actual y escalaciones
    let displayStatus = '';
    let statusClass = '';
    
    if (incident.estado === 'cerrado') {
      displayStatus = 'Cerrado';
      statusClass = 'bg-green-100 text-green-800 border-green-200';
    } else if (incident.escalated_to_supplier) {
      displayStatus = 'Proveedor';
      statusClass = 'bg-orange-100 text-orange-800 border-orange-200';
    } else if (incident.escalated_to_quality || incident.estado === 'laboratorio') {
      displayStatus = 'Laboratorio';
      statusClass = 'bg-purple-100 text-purple-800 border-purple-200';
    } else {
      displayStatus = 'Abierto';
      statusClass = 'bg-blue-100 text-blue-800 border-blue-200';
    }
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${statusClass}`}>
        {displayStatus}
      </span>
    );
  };

  const getPriorityBadge = (prioridad) => {
    const priorityClasses = {
      baja: 'bg-gray-100 text-gray-800 border-gray-200',
      media: 'bg-blue-100 text-blue-800 border-blue-200',
      alta: 'bg-orange-100 text-orange-800 border-orange-200',
      critica: 'bg-red-100 text-red-800 border-red-200',
    };
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${priorityClasses[prioridad] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {prioridad}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error al cargar las incidencias</p>
      </div>
    );
  }

  return (
    <div className="page-container space-y-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
      <div className="flex justify-between items-center">
        <div>
              <h1 className="text-3xl font-bold text-gray-900">Incidencias</h1>
              <p className="mt-2 text-lg text-gray-600">
            {totalCount} incidencias encontradas
          </p>
        </div>
        <Link
          to="/incidents/new"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:scale-105"
        >
              <PlusIcon className="h-5 w-5 mr-2" />
          Nueva Incidencia
        </Link>
          </div>
      </div>

      {/* Filters */}
        <div className="bg-white shadow-lg rounded-xl border border-gray-100 p-6 mb-6">
          <div className="flex items-center mb-4">
            <FunnelIcon className="h-5 w-5 text-gray-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Filtros</h3>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Buscar</label>
            <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="Código, cliente, proveedor..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
              />
            </div>
          </div>
          <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Estado</label>
            <select
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              value={filters.estado}
              onChange={(e) => handleFilterChange('estado', e.target.value)}
            >
              <option value="">Todos los estados</option>
              <option value="abierto">Abierto</option>
              <option value="triage">Triage</option>
              <option value="inspeccion">Inspección</option>
              <option value="laboratorio">Laboratorio</option>
              <option value="propuesta">Propuesta</option>
              <option value="en_progreso">En Progreso</option>
              <option value="cerrado">Cerrado</option>
            </select>
          </div>
          <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Prioridad</label>
            <select
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              value={filters.prioridad}
              onChange={(e) => handleFilterChange('prioridad', e.target.value)}
            >
              <option value="">Todas las prioridades</option>
              <option value="baja">Baja</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="critica">Crítica</option>
            </select>
          </div>
        </div>
      </div>

      {/* Incidents Table */}
        <div className="bg-white shadow-xl rounded-xl border border-gray-100 overflow-hidden">
        {incidents.length === 0 ? (
            <div className="text-center py-16">
              <ExclamationTriangleIcon className="mx-auto h-16 w-16 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">No hay incidencias</h3>
              <p className="mt-2 text-sm text-gray-500">
              Comience creando una nueva incidencia.
            </p>
              <div className="mt-8">
                <Link 
                  to="/incidents/new" 
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:scale-105"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                Nueva Incidencia
              </Link>
            </div>
          </div>
        ) : (
        <div className="table-container overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[120px]">
                    Código
                  </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[150px]">
                    Cliente
                  </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[150px]">
                    Proveedor
                  </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[180px]">
                    Categoría
                  </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[120px]">
                    Estado
                  </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[100px]">
                    Prioridad
                  </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[120px]">
                    Fecha
                  </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider min-w-[200px]">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {incidents.map((incident) => {
                  // Determinar el estilo de la fila basado en el estado
                  let rowClassName = "hover:bg-gray-50 transition-colors duration-200";
                  
                  if (incident.estado === 'cerrado') {
                    rowClassName += " bg-green-50 border-l-4 border-green-400";
                  } else if (incident.escalated_to_quality) {
                    rowClassName += " bg-purple-50 border-l-4 border-purple-400";
                  } else if (incident.escalated_to_supplier) {
                    rowClassName += " bg-orange-50 border-l-4 border-orange-400";
                  }
                  
                  return (
                    <tr key={incident.id} className={rowClassName}>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      <Link
                        to={`/incidents/${incident.id}`}
                          className="text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                      >
                        {incident.code}
                      </Link>
                    </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        <div className="max-w-[140px] truncate" title={incident.cliente}>
                          {incident.cliente}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        <div className="max-w-[140px] truncate" title={incident.provider}>
                          {incident.provider}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                      <div className="flex flex-col max-w-[160px]">
                        <span className="font-medium truncate" title={incident.categoria}>{incident.categoria}</span>
                        {incident.subcategoria && (
                          <span className="text-xs text-gray-500 truncate" title={incident.subcategoria}>{incident.subcategoria}</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {getStatusBadge(incident)}
                    </td>
                    <td className="px-4 py-3">
                      {getPriorityBadge(incident.prioridad)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(incident.fecha_reporte).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium">
                      <div className="flex items-center space-x-1 flex-wrap">
                        <button
                          onClick={() => handleViewDetails(incident)}
                          className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Ver detalles"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(incident)}
                          className="p-1.5 text-gray-400 hover:text-yellow-600 transition-colors"
                          title="Editar"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        {incident.images_count > 0 && (
                          <button
                            onClick={() => handleViewImages(incident)}
                            className="p-1.5 text-gray-400 hover:text-green-600 transition-colors"
                            title="Ver Imágenes"
                          >
                            <EyeIcon className="h-4 w-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleViewAttachments(incident)}
                          className="p-1.5 text-gray-400 hover:text-purple-600 transition-colors"
                          title="Ver Adjuntos"
                        >
                          <PaperClipIcon className="h-4 w-4" />
                        </button>
                        {incident.estado === 'cerrado' && (
                          <button
                            onClick={() => handleReopen(incident)}
                            className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors"
                            title="Reabrir Incidencia"
                          >
                            <ArrowPathIcon className="h-4 w-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(incident)}
                          className="p-1.5 text-gray-400 hover:text-red-600 transition-colors"
                          title="Eliminar"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        </div>
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedIncident && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Detalles de la Incidencia
                </h3>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-6">
                {/* Información Básica */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Información Básica</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Código</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.code}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Estado</label>
                      <div className="mt-1">
                        {getStatusBadge(selectedIncident)}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Prioridad</label>
                      <div className="mt-1">
                        {getPriorityBadge(selectedIncident.prioridad)}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Responsable</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {selectedIncident.responsable === 'patricio_morales' ? 'Patricio Morales' : 'Marco Montenegro'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Información del Cliente y Proveedor */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Cliente y Proveedor</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Cliente</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.cliente}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Proveedor</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.provider}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Obra</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.obra}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Creado por</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.created_by?.full_name || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {/* Información del Producto */}
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Información del Producto</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">SKU</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.sku || 'No especificado'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Lote</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.lote || 'No especificado'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Categoría</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.categoria}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Subcategoría</label>
                      <p className="mt-1 text-sm text-gray-900">{selectedIncident.subcategoria || 'No especificada'}</p>
                    </div>
                  </div>
                </div>

                {/* Detalles de la Incidencia */}
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Detalles de la Incidencia</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Descripción</label>
                      <p className="mt-1 text-sm text-gray-900 bg-white p-3 rounded border">{selectedIncident.descripcion}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Fecha de Detección</label>
                        <p className="mt-1 text-sm text-gray-900">{selectedIncident.fecha_deteccion}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Hora de Detección</label>
                        <p className="mt-1 text-sm text-gray-900">{selectedIncident.hora_deteccion}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Fecha de Reporte</label>
                        <p className="mt-1 text-sm text-gray-900">
                          {new Date(selectedIncident.fecha_reporte).toLocaleDateString('es-CL')}
                        </p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Creado</label>
                        <p className="mt-1 text-sm text-gray-900">
                          {new Date(selectedIncident.created_at).toLocaleDateString('es-CL')}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Estado de Escalación */}
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Estado de Escalación</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Escalado a Calidad</label>
                      <div className="mt-1">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          selectedIncident.escalated_to_quality 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedIncident.escalated_to_quality ? 'Sí' : 'No'}
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Escalado a Proveedor</label>
                      <div className="mt-1">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          selectedIncident.escalated_to_supplier 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {selectedIncident.escalated_to_supplier ? 'Sí' : 'No'}
                        </span>
                      </div>
                    </div>
                    {selectedIncident.escalation_date && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Fecha de Escalación</label>
                        <p className="mt-1 text-sm text-gray-900">
                          {new Date(selectedIncident.escalation_date).toLocaleDateString('es-CL')}
                        </p>
                      </div>
                    )}
                    {selectedIncident.escalation_reason && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Razón de Escalación</label>
                        <p className="mt-1 text-sm text-gray-900">{selectedIncident.escalation_reason}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Imágenes Adjuntas */}
                {selectedIncident.images_count > 0 && (
                  <div className="bg-indigo-50 p-4 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Imágenes Adjuntas</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Array.from({ length: selectedIncident.images_count }).map((_, index) => (
                        <div key={index} className="bg-white p-2 rounded border">
                          <div className="w-full h-32 bg-gray-200 rounded flex items-center justify-center">
                            <span className="text-gray-500 text-sm">Imagen {index + 1}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="mt-2 text-sm text-gray-600">
                      {selectedIncident.images_count} imagen(es) adjunta(s)
                    </p>
                  </div>
                )}

                {/* Documentos Adjuntos */}
                {selectedIncident.documents_count > 0 && (
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Documentos Adjuntos</h4>
                    <p className="text-sm text-gray-600">
                      {selectedIncident.documents_count} documento(s) adjunto(s)
                    </p>
                  </div>
                )}
              </div>

              {/* Imágenes Adjuntas */}
              {selectedIncident.images_count > 0 && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Imágenes Adjuntas</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">
                      {selectedIncident.images_count} imagen{selectedIncident.images_count !== 1 ? 'es' : ''} adjunta{selectedIncident.images_count !== 1 ? 's' : ''}
                    </span>
                    <button
                      onClick={() => {
                        setShowDetailModal(false);
                        handleViewImages(selectedIncident);
                      }}
                      className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <EyeIcon className="h-4 w-4 mr-1" />
                      Ver Imágenes
                    </button>
                  </div>
                </div>
              )}

              {/* Sin Documentos Adjuntos */}
              {selectedIncident.images_count === 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">Documentos Adjuntos</h4>
                  <p className="text-sm text-gray-600">Sin documentos adjuntos</p>
                </div>
              )}
              
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Cerrar
                </button>
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    handleEdit(selectedIncident);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Editar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && selectedIncident && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Editar Incidencia
                </h3>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const updatedData = {
                  cliente: formData.get('cliente'),
                  provider: formData.get('provider'),
                  obra: formData.get('obra'),
                  sku: formData.get('sku'),
                  lote: formData.get('lote'),
                  descripcion: formData.get('descripcion'),
                  estado: formData.get('estado'),
                  prioridad: formData.get('prioridad'),
                  categoria: formData.get('categoria'),
                  subcategoria: formData.get('subcategoria'),
                  responsable: formData.get('responsable'),
                  fecha_deteccion: formData.get('fecha_deteccion'),
                  hora_deteccion: formData.get('hora_deteccion'),
                };
                handleEditSave(updatedData);
              }}>
                <div className="space-y-6">
                  {/* Información Básica */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Información Básica</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Estado</label>
                        <select
                          name="estado"
                          defaultValue={selectedIncident.estado}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="abierto">Abierto</option>
                          <option value="cerrado">Cerrado</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Prioridad</label>
                        <select
                          name="prioridad"
                          defaultValue={selectedIncident.prioridad}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="baja">Baja</option>
                          <option value="media">Media</option>
                          <option value="alta">Alta</option>
                          <option value="critica">Crítica</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Responsable</label>
                        <select
                          name="responsable"
                          defaultValue={selectedIncident.responsable}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="patricio_morales">Patricio Morales</option>
                          <option value="marco_montenegro">Marco Montenegro</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Cliente y Proveedor */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Cliente y Proveedor</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Cliente</label>
                        <input
                          type="text"
                          name="cliente"
                          defaultValue={selectedIncident.cliente}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Proveedor</label>
                        <input
                          type="text"
                          name="provider"
                          defaultValue={selectedIncident.provider}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="col-span-2">
                        <label className="block text-sm font-medium text-gray-700">Obra</label>
                        <input
                          type="text"
                          name="obra"
                          defaultValue={selectedIncident.obra}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Información del Producto */}
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Información del Producto</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">SKU</label>
                        <input
                          type="text"
                          name="sku"
                          defaultValue={selectedIncident.sku || ''}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Lote</label>
                        <input
                          type="text"
                          name="lote"
                          defaultValue={selectedIncident.lote || ''}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Categoría</label>
                        <select
                          name="categoria"
                          defaultValue={selectedIncident.categoria}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <optgroup label="Tubería">
                            <option value="tuberia_beta">Tubería BETA</option>
                            <option value="tuberia_ppr">Tubería PPR</option>
                            <option value="tuberia_hdpe">Tubería HDPE</option>
                          </optgroup>
                          <optgroup label="Fitting">
                            <option value="fitting_inserto_metalico">Fitting con inserto metálico</option>
                            <option value="fitting_ppr">Fitting PPR</option>
                            <option value="fitting_hdpe_electrofusion">Fitting HDPE Electrofusión</option>
                            <option value="fitting_hdpe_fusion_tope">Fitting HDPE Fusión Tope</option>
                          </optgroup>
                          <optgroup label="Otros">
                            <option value="llave">LLave</option>
                            <option value="flange">Flange</option>
                            <option value="inserto_metalico">Inserto metálico</option>
                            <option value="otro">Otro</option>
                          </optgroup>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Subcategoría</label>
                        <input
                          type="text"
                          name="subcategoria"
                          defaultValue={selectedIncident.subcategoria || ''}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Detalles de la Incidencia */}
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Detalles de la Incidencia</h4>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Descripción</label>
                        <textarea
                          name="descripcion"
                          rows={4}
                          defaultValue={selectedIncident.descripcion}
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Fecha de Detección</label>
                          <input
                            type="date"
                            name="fecha_deteccion"
                            defaultValue={selectedIncident.fecha_deteccion}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Hora de Detección</label>
                          <input
                            type="time"
                            name="hora_deteccion"
                            defaultValue={selectedIncident.hora_deteccion}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowEditModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    Guardar Cambios
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedIncident && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
                <ExclamationTriangleIcon className="w-6 h-6 text-red-600" />
              </div>
              <div className="mt-2 text-center">
                <h3 className="text-lg font-medium text-gray-900">Eliminar Incidencia</h3>
                <div className="mt-2">
                  <p className="text-sm text-gray-500">
                    ¿Estás seguro de que quieres eliminar la incidencia <strong>{selectedIncident.code}</strong>?
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    Esta acción no se puede deshacer.
                  </p>
                </div>
              </div>
              <div className="mt-6 flex justify-center space-x-3">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  Eliminar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Attachments Modal */}
      {showAttachmentsModal && selectedIncident && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-11/12 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Adjuntos - {selectedIncident.code}
              </h3>
              <button
                onClick={() => setShowAttachmentsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <IncidentAttachments 
              incidentId={selectedIncident.id} 
              incidentCode={selectedIncident.code} 
            />
          </div>
        </div>
      )}

      {/* Images Modal */}
      {showImagesModal && selectedIncident && (
        <IncidentImages
          incident={selectedIncident}
          onClose={() => {
            setShowImagesModal(false);
            setSelectedIncident(null);
          }}
        />
      )}
    </div>
  );
};

export default Incidents;
