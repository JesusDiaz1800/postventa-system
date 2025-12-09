import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNotifications } from '../hooks/useNotifications';
import PageHeader from '../components/PageHeader';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  TagIcon,
  PaperClipIcon,
  DocumentIcon,
  ChartBarIcon,
  ArrowPathIcon,
  PlusIcon,
  CloudArrowUpIcon,
  DocumentMagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

const DocumentsNew = () => {
  const { showSuccess, showError } = useNotifications();
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    incidentCode: '',
    client: '',
    obra: '',
    category: '',
    subcategory: '',
    dateFrom: '',
    dateTo: '',
    documentType: '',
    status: ''
  });
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  // Query para obtener todas las incidencias con sus documentos
  const { data: incidentsData, isLoading: incidentsLoading, refetch: refetchIncidents } = useQuery({
    queryKey: ['incidents-documents', filters],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/incidents/?search=${searchTerm}&estado=&prioridad=`);
        if (!response.ok) throw new Error('Error al cargar incidencias');
        return response.json();
      } catch (error) {
        showError('Error al cargar incidencias: ' + error.message);
        throw error;
      }
    },
    enabled: true,
  });

  // Query para obtener documentos por incidencia
  const { data: documentsData, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents-by-incident', selectedIncident?.id],
    queryFn: async () => {
      if (!selectedIncident?.id) return null;
      
      try {
        const [documentsRes, visitReportsRes, qualityReportsRes, supplierReportsRes, labReportsRes] = await Promise.all([
          fetch(`/api/documents/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/visit-reports/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/quality-reports/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/supplier-reports/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/lab-reports/?incident_id=${selectedIncident.id}`)
        ]);

        const [documents, visitReports, qualityReports, supplierReports, labReports] = await Promise.all([
          documentsRes.ok ? documentsRes.json() : { results: [] },
          visitReportsRes.ok ? visitReportsRes.json() : { results: [] },
          qualityReportsRes.ok ? qualityReportsRes.json() : { results: [] },
          supplierReportsRes.ok ? supplierReportsRes.json() : { results: [] },
          labReportsRes.ok ? labReportsRes.json() : { results: [] }
        ]);

        return {
          documents: documents.results || documents.data || documents || [],
          visitReports: visitReports.results || visitReports.data || visitReports || [],
          qualityReports: qualityReports.results || qualityReports.data || qualityReports || [],
          supplierReports: supplierReports.results || supplierReports.data || supplierReports || [],
          labReports: labReports.results || labReports.data || labReports || []
        };
      } catch (error) {
        showError('Error al cargar documentos: ' + error.message);
        return null;
      }
    },
    enabled: !!selectedIncident?.id,
  });

  // Procesar datos de incidencias
  const incidents = incidentsData?.data?.results || incidentsData?.results || incidentsData || [];
  
  // Filtrar incidencias basado en los filtros
  const filteredIncidents = incidents.filter(incident => {
    const matchesSearch = !searchTerm || 
      (incident.code && incident.code.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (incident.cliente && incident.cliente.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (incident.obra && incident.obra.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilters = 
      (!filters.incidentCode || (incident.code && incident.code.includes(filters.incidentCode))) &&
      (!filters.client || (incident.cliente && incident.cliente.toLowerCase().includes(filters.client.toLowerCase()))) &&
      (!filters.obra || (incident.obra && incident.obra.toLowerCase().includes(filters.obra.toLowerCase()))) &&
      (!filters.category || (incident.categoria && incident.categoria.name === filters.category)) &&
      (!filters.subcategory || (incident.subcategoria && incident.subcategoria.toLowerCase().includes(filters.subcategory.toLowerCase()))) &&
      (!filters.dateFrom || new Date(incident.fecha_reporte) >= new Date(filters.dateFrom)) &&
      (!filters.dateTo || new Date(incident.fecha_reporte) <= new Date(filters.dateTo)) &&
      (!filters.status || incident.estado === filters.status);

    return matchesSearch && matchesFilters;
  });

  // Combinar todos los documentos de una incidencia
  const getAllDocumentsForIncident = (incidentId) => {
    if (!documentsData || selectedIncident?.id !== incidentId) return [];
    
    const allDocs = [
      ...documentsData.documents.map(doc => ({ ...doc, type: 'document', typeLabel: 'Documento' })),
      ...documentsData.visitReports.map(doc => ({ ...doc, type: 'visit_report', typeLabel: 'Reporte de Visita' })),
      ...documentsData.qualityReports.map(doc => ({ ...doc, type: 'quality_report', typeLabel: 'Reporte de Calidad' })),
      ...documentsData.supplierReports.map(doc => ({ ...doc, type: 'supplier_report', typeLabel: 'Reporte de Proveedor' })),
      ...documentsData.labReports.map(doc => ({ ...doc, type: 'lab_report', typeLabel: 'Reporte de Laboratorio' }))
    ];
    
    return allDocs;
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      incidentCode: '',
      client: '',
      obra: '',
      category: '',
      subcategory: '',
      dateFrom: '',
      dateTo: '',
      documentType: '',
      status: ''
    });
    setSearchTerm('');
  };

  const downloadDocument = async (document) => {
    try {
      const response = await fetch(`/api/documents/${document.id}/download/`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = document.title || document.name || 'documento';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showSuccess('Documento descargado exitosamente');
      } else {
        showError('Error al descargar el documento');
      }
    } catch (error) {
      showError('Error al descargar el documento: ' + error.message);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'abierto': return 'bg-red-100 text-red-800';
      case 'en_proceso': return 'bg-yellow-100 text-yellow-800';
      case 'cerrado': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'alta': return 'bg-red-100 text-red-800';
      case 'media': return 'bg-yellow-100 text-yellow-800';
      case 'baja': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <PageHeader
        title="Trazabilidad de Documentos"
        subtitle="Sistema completo de gestión y trazabilidad de documentos por incidencia"
        icon={DocumentMagnifyingGlassIcon}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros y Búsqueda */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* Búsqueda */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por código, cliente, obra..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Botones */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filtros Avanzados
              </button>
              
              <button
                onClick={() => refetchIncidents()}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Actualizar
              </button>
            </div>
          </div>

          {/* Filtros Avanzados */}
          {showFilters && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Código de Incidencia
                </label>
                <input
                  type="text"
                  value={filters.incidentCode}
                  onChange={(e) => handleFilterChange('incidentCode', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ej: INC-2025-001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente
                </label>
                <input
                  type="text"
                  value={filters.client}
                  onChange={(e) => handleFilterChange('client', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nombre del cliente"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obra
                </label>
                <input
                  type="text"
                  value={filters.obra}
                  onChange={(e) => handleFilterChange('obra', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nombre de la obra"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Todos los estados</option>
                  <option value="abierto">Abierto</option>
                  <option value="en_proceso">En Proceso</option>
                  <option value="cerrado">Cerrado</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha Desde
                </label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha Hasta
                </label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                >
                  Limpiar Filtros
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Incidencias</p>
                <p className="text-2xl font-bold text-gray-900">{filteredIncidents.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <DocumentIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Documentos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredIncidents.reduce((total, incident) => {
                    const docs = getAllDocumentsForIncident(incident.id);
                    return total + docs.length;
                  }, 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Abiertas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredIncidents.filter(incident => incident.estado === 'abierto').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <PaperClipIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Con Adjuntos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredIncidents.filter(incident => {
                    const docs = getAllDocumentsForIncident(incident.id);
                    return docs.length > 0;
                  }).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Lista de Incidencias */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Incidencias y Documentos ({filteredIncidents.length})
            </h3>
          </div>

          {incidentsLoading ? (
            <div className="p-8 text-center">
              <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Cargando incidencias...</p>
            </div>
          ) : filteredIncidents.length === 0 ? (
            <div className="p-8 text-center">
              <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No se encontraron incidencias con los filtros aplicados</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredIncidents.map((incident) => {
                const documents = getAllDocumentsForIncident(incident.id);
                const isSelected = selectedIncident?.id === incident.id;
                
                return (
                  <div key={incident.id} className="p-6 hover:bg-gray-50 transition-colors duration-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <button
                            onClick={() => setSelectedIncident(isSelected ? null : incident)}
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              isSelected 
                                ? 'bg-blue-100 text-blue-800' 
                                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                            }`}
                          >
                            {isSelected ? 'Ocultar Documentos' : 'Ver Documentos'}
                          </button>
                          
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(incident.estado)}`}>
                            {incident.estado}
                          </span>
                          
                          {incident.prioridad && (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(incident.prioridad)}`}>
                              {incident.prioridad}
                            </span>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-1">
                              {incident.code || `INC-${incident.id}`}
                            </h4>
                            <p className="text-sm text-gray-600">
                              <BuildingOfficeIcon className="h-4 w-4 inline mr-1" />
                              {incident.cliente || 'Sin cliente'}
                            </p>
                          </div>

                          <div>
                            <p className="text-sm text-gray-600">
                              <BuildingOfficeIcon className="h-4 w-4 inline mr-1" />
                              {incident.obra || 'Sin obra'}
                            </p>
                            <p className="text-sm text-gray-600">
                              <TagIcon className="h-4 w-4 inline mr-1" />
                              {incident.categoria?.name || 'Sin categoría'}
                            </p>
                          </div>

                          <div>
                            <p className="text-sm text-gray-600">
                              <CalendarIcon className="h-4 w-4 inline mr-1" />
                              {new Date(incident.fecha_reporte).toLocaleDateString()}
                            </p>
                            <p className="text-sm text-gray-600">
                              <UserIcon className="h-4 w-4 inline mr-1" />
                              {incident.provider || 'Sin proveedor'}
                            </p>
                          </div>
                        </div>

                        <p className="text-gray-700 text-sm mb-4">
                          {incident.descripcion || 'Sin descripción'}
                        </p>

                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <DocumentIcon className="h-4 w-4 mr-1" />
                            {documents.length} documentos
                          </span>
                          {incident.sku && (
                            <span className="flex items-center">
                              <TagIcon className="h-4 w-4 mr-1" />
                              SKU: {incident.sku}
                            </span>
                          )}
                          {incident.lote && (
                            <span className="flex items-center">
                              <TagIcon className="h-4 w-4 mr-1" />
                              Lote: {incident.lote}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Documentos de la Incidencia */}
                    {isSelected && (
                      <div className="mt-6 pt-6 border-t border-gray-200">
                        {documentsLoading ? (
                          <div className="text-center py-4">
                            <ArrowPathIcon className="h-6 w-6 animate-spin text-blue-600 mx-auto mb-2" />
                            <p className="text-gray-600">Cargando documentos...</p>
                          </div>
                        ) : documents.length === 0 ? (
                          <div className="text-center py-8">
                            <PaperClipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600">No hay documentos adjuntos para esta incidencia</p>
                          </div>
                        ) : (
                          <div>
                            <h5 className="font-semibold text-gray-900 mb-4">Documentos Adjuntos</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                              {documents.map((doc, index) => (
                                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                                  <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center">
                                      <DocumentIcon className="h-5 w-5 text-blue-600 mr-2" />
                                      <div>
                                        <p className="font-medium text-gray-900 text-sm">
                                          {doc.title || doc.name || `Documento ${index + 1}`}
                                        </p>
                                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                          {doc.typeLabel}
                                        </span>
                                      </div>
                                    </div>
                                  </div>

                                  {doc.description && (
                                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                                      {doc.description}
                                    </p>
                                  )}

                                  <div className="flex items-center justify-between">
                                    <div className="text-xs text-gray-500">
                                      {doc.created_at && (
                                        <span>
                                          {new Date(doc.created_at).toLocaleDateString()}
                                        </span>
                                      )}
                                    </div>
                                    <button
                                      onClick={() => downloadDocument(doc)}
                                      className="inline-flex items-center px-3 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                      <DocumentArrowDownIcon className="h-3 w-3 mr-1" />
                                      Descargar
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentsNew;
