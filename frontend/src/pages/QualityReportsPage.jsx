import React, { useState, useEffect, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { 
  PlusIcon, 
  DocumentArrowUpIcon, 
  EyeIcon, 
  TrashIcon,
  XMarkIcon,
  CheckCircleIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

const QualityReportsPage = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  
  // Estados para filtros y búsqueda
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  
  // Estados para modales
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showIncidentModal, setShowIncidentModal] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [attachReportType, setAttachReportType] = useState('cliente');
  
  // Estados para subida de archivos
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedDocuments, setUploadedDocuments] = useState([]);

  // Obtener incidencias abiertas
  const { data: incidents, isLoading: incidentsLoading, error: incidentsError } = useQuery({
    queryKey: ['incidents', { estado: 'abierto' }],
    queryFn: async () => {
      const response = await api.get('/incidents/', {
        params: { estado: 'abierto' }
      });
      return response.data;
    }
  });

  // Obtener reportes de calidad
  const { data: qualityReports, isLoading: reportsLoading, error: reportsError } = useQuery({
    queryKey: ['quality-reports'],
    queryFn: async () => {
      const response = await api.get('/documents/quality-reports/');
      return response.data;
    }
  });

  // Obtener documentos subidos para una incidencia específica
  const { data: uploadedDocs, refetch: refetchUploadedDocs } = useQuery({
    queryKey: ['uploaded-quality-docs', selectedIncident?.id],
    queryFn: async () => {
      if (!selectedIncident) return [];
      const response = await api.get(`/documents/uploaded/quality-report/${selectedIncident.id}/`);
      return response.data;
    },
    enabled: !!selectedIncident
  });

  // Filtrar incidencias
  const filteredIncidents = useMemo(() => {
    if (!incidents?.results) return [];
    
    return incidents.results.filter(incident => {
      const matchesSearch = !searchTerm || 
        incident.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        incident.provider.toLowerCase().includes(searchTerm.toLowerCase()) ||
        incident.cliente.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = !statusFilter || incident.estado === statusFilter;
      const matchesPriority = !priorityFilter || incident.prioridad === priorityFilter;
      
      return matchesSearch && matchesStatus && matchesPriority;
    });
  }, [incidents?.results, searchTerm, statusFilter, priorityFilter]);

  // Manejar selección de incidencia
  const handleIncidentSelect = (incident) => {
    setSelectedIncident(incident);
    setShowIncidentModal(true);
  };

  // Manejar subida de documento
  const handleUploadDocument = async () => {
    if (!uploadFile || !selectedIncident) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('incident_id', selectedIncident.id);
      formData.append('report_type', attachReportType);

      const response = await api.post('/documents/upload/quality-report/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setUploadedDocuments(prev => [...prev, {
          filename: uploadFile.name,
          uploaded_at: new Date().toISOString(),
          report_type: attachReportType
        }]);
        setUploadFile(null);
        setShowUploadModal(false);
        refetchUploadedDocs();
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Error al subir el documento');
    } finally {
      setUploading(false);
    }
  };

  // Manejar eliminación de documento
  const handleDeleteDocument = async (filename) => {
    if (!selectedIncident) return;

    try {
      await api.delete(`/documents/uploaded/quality-report/${selectedIncident.id}/${filename}/`);
      setUploadedDocuments(prev => prev.filter(doc => doc.filename !== filename));
      refetchUploadedDocs();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Error al eliminar el documento');
    }
  };

  // Manejar apertura de documento
  const handleOpenDocument = async (filename) => {
    if (!selectedIncident) return;
    
    // Intentar abrir desde documentos subidos primero
    const uploadedDoc = uploadedDocuments.find(doc => doc.filename === filename);
    if (uploadedDoc) {
      const encodedFilename = encodeURIComponent(filename);
  const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}/api/documents/open/quality-report/${selectedIncident.id}/${encodedFilename}`;
      window.open(url, '_blank');
      return;
    }
    
    // Si no está en documentos subidos, intentar abrir desde reportes generados
    const report = qualityReports?.results?.find(r => r.incident_id === selectedIncident.id);
    if (report) {
      const encodedFilename = encodeURIComponent(filename);
  const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}/api/documents/open/quality-report/${selectedIncident.id}/${encodedFilename}`;
      window.open(url, '_blank');
    }
  };

  if (incidentsLoading || reportsLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-6"></div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Cargando Reportes</h3>
          <p className="text-gray-600">Preparando la información...</p>
        </div>
      </div>
    );
  }

  if (incidentsError || reportsError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Error al Cargar</h3>
          <p className="text-gray-600">No se pudieron cargar los reportes de calidad</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-rose-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BeakerIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  Reportes de Calidad
                </h1>
                <p className="text-sm text-gray-500">
                  Gestión de reportes de control de calidad
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowIncidentModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Nuevo Reporte
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                Adjuntar Documento
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros y Búsqueda */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por código, proveedor o cliente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              <option value="abierto">Abierto</option>
              <option value="en_proceso">En Proceso</option>
              <option value="resuelto">Resuelto</option>
              <option value="cerrado">Cerrado</option>
            </select>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Todas las prioridades</option>
              <option value="critica">Crítica</option>
              <option value="alta">Alta</option>
              <option value="media">Media</option>
              <option value="baja">Baja</option>
            </select>
            <button
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('');
                setPriorityFilter('');
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>

        {/* Lista de Incidencias */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">
              Incidencias Abiertas ({filteredIncidents.length})
            </h2>
          </div>
          <div className="divide-y divide-gray-200">
            {filteredIncidents.map((incident) => (
              <div key={incident.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900">
                          {incident.code}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {incident.provider} • {incident.cliente}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          incident.prioridad === 'critica' ? 'bg-red-100 text-red-800' :
                          incident.prioridad === 'alta' ? 'bg-orange-100 text-orange-800' :
                          incident.prioridad === 'media' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {incident.prioridad.toUpperCase()}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          incident.estado === 'abierto' ? 'bg-red-100 text-red-800' :
                          incident.estado === 'en_proceso' ? 'bg-yellow-100 text-yellow-800' :
                          incident.estado === 'resuelto' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {incident.estado.toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-600">
                      <p><strong>Obra:</strong> {incident.obra}</p>
                      <p><strong>SKU:</strong> {incident.sku} • <strong>Lote:</strong> {incident.lote || 'N/A'}</p>
                      <p><strong>Descripción:</strong> {incident.descripcion}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleIncidentSelect(incident)}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                    >
                      <PlusIcon className="h-4 w-4 mr-2" />
                      Crear Reporte
                    </button>
                    <button
                      onClick={() => setSelectedIncident(incident)}
                      className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                    >
                      <DocumentArrowUpIcon className="h-4 w-4 mr-2" />
                      Adjuntar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lista de Reportes Generados */}
        {qualityReports?.results && qualityReports.results.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Reportes Generados ({qualityReports.results.length})
              </h2>
            </div>
            <div className="divide-y divide-gray-200">
              {qualityReports.results.map((report) => (
                <div key={report.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4">
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">
                            Reporte de Calidad - {report.incident_code}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {report.report_type === 'cliente' ? '👤 Cliente' : '🏢 Interno'} • 
                            Creado: {new Date(report.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          report.report_type === 'cliente' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {report.report_type === 'cliente' ? 'CLIENTE' : 'INTERNO'}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleOpenDocument(report.filename)}
                        className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                      >
                        <EyeIcon className="h-4 w-4 mr-2" />
                        Ver
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modal de Selección de Incidencia */}
      {showIncidentModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Seleccionar Acción para la Incidencia
              </h3>
              <div className="space-y-3">
                <button
                  onClick={() => {
                    setShowIncidentModal(false);
                    navigate('/quality-reports/form');
                  }}
                  className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Crear Nuevo Reporte
                </button>
                <button
                  onClick={() => {
                    setShowIncidentModal(false);
                    setShowUploadModal(true);
                  }}
                  className="w-full inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
                >
                  <DocumentArrowUpIcon className="h-4 w-4 mr-2" />
                  Adjuntar Documento
                </button>
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setShowIncidentModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Subida de Documento */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Adjuntar Documento
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Reporte
                  </label>
                  <select
                    value={attachReportType}
                    onChange={(e) => setAttachReportType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="cliente">Para Cliente</option>
                    <option value="interno">Interno</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Archivo
                  </label>
                  <input
                    type="file"
                    onChange={(e) => setUploadFile(e.target.files[0])}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    accept=".pdf,.doc,.docx"
                  />
                </div>
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleUploadDocument}
                  disabled={!uploadFile || uploading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Subiendo...' : 'Subir'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QualityReportsPage;
