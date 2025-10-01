import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { documentsAPI } from '../services/api';
import {
  DocumentTextIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  FolderIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

const DocumentsByIncidents = () => {
  const [filters, setFilters] = useState({
    search: '',
    document_type: '',
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['documents-by-incidents', filters],
    queryFn: () => documentsAPI.getByIncidents(filters),
  });

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const getStatusBadge = (estado) => {
    const statusClasses = {
      abierto: 'bg-blue-100 text-blue-800 border-blue-200',
      triage: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      inspeccion: 'bg-orange-100 text-orange-800 border-orange-200',
      laboratorio: 'bg-purple-100 text-purple-800 border-purple-200',
      propuesta: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      en_progreso: 'bg-cyan-100 text-cyan-800 border-cyan-200',
      cerrado: 'bg-green-100 text-green-800 border-green-200',
    };
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusClasses[estado] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {estado?.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const getPriorityBadge = (prioridad) => {
    const priorityClasses = {
      baja: 'bg-green-100 text-green-800 border-green-200',
      media: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      alta: 'bg-orange-100 text-orange-800 border-orange-200',
      critica: 'bg-red-100 text-red-800 border-red-200',
    };
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${priorityClasses[prioridad] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {prioridad?.toUpperCase()}
      </span>
    );
  };

  const getDocumentTypeIcon = (documentType) => {
    const iconClasses = {
      incident_report: 'text-blue-600',
      lab_report: 'text-purple-600',
      visit_report: 'text-green-600',
      client_report: 'text-indigo-600',
      provider_letter: 'text-orange-600',
      technical_report: 'text-red-600',
      analysis_report: 'text-pink-600',
      resolution_report: 'text-teal-600',
      other: 'text-gray-600',
    };
    
    return (
      <DocumentTextIcon className={`h-5 w-5 ${iconClasses[documentType] || 'text-gray-600'}`} />
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Cargando documentos...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error al cargar documentos</h3>
        <p className="mt-1 text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }

  const incidents = data?.incidents || [];
  const documentsWithoutIncident = data?.documents_without_incident || [];
  const totalDocuments = data?.total_documents || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow-xl rounded-xl border border-gray-100 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Documentos por Incidencias</h1>
            <p className="mt-2 text-lg text-gray-600">
              {totalDocuments} documentos organizados por {data?.total_incidents || 0} incidencias
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow-xl rounded-xl border border-gray-100 p-6">
        <div className="flex items-center mb-4">
          <FunnelIcon className="h-5 w-5 text-gray-500 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Filtros</h3>
        </div>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Búsqueda</label>
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por título, incidencia, cliente..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Documento</label>
            <select
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              value={filters.document_type}
              onChange={(e) => handleFilterChange('document_type', e.target.value)}
            >
              <option value="">Todos los tipos</option>
              <option value="incident_report">Informe de Incidencia</option>
              <option value="lab_report">Informe de Laboratorio</option>
              <option value="visit_report">Reporte de Visita</option>
              <option value="client_report">Informe para Cliente</option>
              <option value="provider_letter">Carta para Proveedor</option>
              <option value="technical_report">Informe Técnico</option>
              <option value="analysis_report">Informe de Análisis</option>
              <option value="resolution_report">Informe de Resolución</option>
              <option value="other">Otro</option>
            </select>
          </div>
        </div>
      </div>

      {/* Documents by Incidents */}
      {incidents.length === 0 && documentsWithoutIncident.length === 0 ? (
        <div className="text-center py-16">
          <DocumentTextIcon className="mx-auto h-16 w-16 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No hay documentos</h3>
          <p className="mt-2 text-sm text-gray-500">
            No se encontraron documentos con los filtros aplicados.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Documents by Incidents */}
          {incidents.map((incidentGroup) => (
            <div key={incidentGroup.incident.id} className="bg-white shadow-xl rounded-xl border border-gray-100 overflow-hidden">
              {/* Incident Header */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <FolderIcon className="h-8 w-8 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {incidentGroup.incident.code}
                      </h3>
                      <div className="flex items-center space-x-4 mt-1">
                        <p className="text-sm text-gray-600">
                          Cliente: <span className="font-medium">{incidentGroup.incident.cliente}</span>
                        </p>
                        <p className="text-sm text-gray-600">
                          Proveedor: <span className="font-medium">{incidentGroup.incident.provider}</span>
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {getStatusBadge(incidentGroup.incident.estado)}
                    {getPriorityBadge(incidentGroup.incident.prioridad)}
                    <span className="text-sm text-gray-500">
                      {incidentGroup.documents.length} documento{incidentGroup.documents.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
              </div>

              {/* Documents List */}
              <div className="divide-y divide-gray-200">
                {incidentGroup.documents.map((document) => (
                  <div key={document.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        {getDocumentTypeIcon(document.document_type)}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{document.title}</h4>
                          <div className="flex items-center space-x-4 mt-1">
                            <p className="text-sm text-gray-500">
                              {document.document_type_display}
                            </p>
                            <p className="text-sm text-gray-500">
                              v{document.version}
                            </p>
                            <p className="text-sm text-gray-500">
                              {new Date(document.created_at).toLocaleDateString('es-ES')}
                            </p>
                            <p className="text-sm text-gray-500">
                              por {document.created_by.first_name} {document.created_by.last_name}
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {document.is_final ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-500" title="Documento final" />
                        ) : (
                          <ClockIcon className="h-5 w-5 text-yellow-500" title="Borrador" />
                        )}
                        <button
                          className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Ver documento"
                        >
                          <EyeIcon className="h-5 w-5" />
                        </button>
                        <button
                          className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                          title="Descargar documento"
                        >
                          <ArrowDownTrayIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Documents without Incident */}
          {documentsWithoutIncident.length > 0 && (
            <div className="bg-white shadow-xl rounded-xl border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <DocumentTextIcon className="h-6 w-6 text-gray-600" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    Documentos sin Incidencia
                  </h3>
                  <span className="text-sm text-gray-500">
                    ({documentsWithoutIncident.length} documento{documentsWithoutIncident.length !== 1 ? 's' : ''})
                  </span>
                </div>
              </div>
              
              <div className="divide-y divide-gray-200">
                {documentsWithoutIncident.map((document) => (
                  <div key={document.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        {getDocumentTypeIcon(document.document_type)}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">{document.title}</h4>
                          <div className="flex items-center space-x-4 mt-1">
                            <p className="text-sm text-gray-500">
                              {document.document_type_display}
                            </p>
                            <p className="text-sm text-gray-500">
                              v{document.version}
                            </p>
                            <p className="text-sm text-gray-500">
                              {new Date(document.created_at).toLocaleDateString('es-ES')}
                            </p>
                            <p className="text-sm text-gray-500">
                              por {document.created_by.first_name} {document.created_by.last_name}
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {document.is_final ? (
                          <CheckCircleIcon className="h-5 w-5 text-green-500" title="Documento final" />
                        ) : (
                          <ClockIcon className="h-5 w-5 text-yellow-500" title="Borrador" />
                        )}
                        <button
                          className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Ver documento"
                        >
                          <EyeIcon className="h-5 w-5" />
                        </button>
                        <button
                          className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                          title="Descargar documento"
                        >
                          <ArrowDownTrayIcon className="h-5 w-5" />
                        </button>
                      </div>
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
};

export default DocumentsByIncidents;
