import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import PageHeader from '../components/PageHeader';
import ErrorBoundary from '../components/ErrorBoundary';
import DocumentViewer from '../components/DocumentViewer';
import BulkDocumentActions from '../components/BulkDocumentActions';
import DocumentsByIncident from '../components/DocumentsByIncident';
import {
  DocumentTextIcon,
  EyeIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentArrowDownIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  XMarkIcon,
  PlusIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const Documents = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedIncident, setSelectedIncident] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [viewerOpen, setViewerOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [notification, setNotification] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadFormData, setUploadFormData] = useState({
    title: '',
    description: '',
    document_type: 'general',
    incident_id: ''
  });
  
  const queryClient = useQueryClient();

  // Obtener incidencias para filtros
  const { data: incidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => api.get('/incidents/').then(res => res.data),
  });

  // Obtener documentos organizados por incidencias
  const { data: documentsByIncidents, isLoading: documentsLoading, refetch: refetchDocuments } = useQuery({
    queryKey: ['documents-by-incidents'],
    queryFn: () => api.get('/documents/by-incidents/').then(res => res.data),
    refetchInterval: 30000, // Refrescar cada 30 segundos
  });

  // Mutación para eliminar documento
  const deleteDocumentMutation = useMutation({
    mutationFn: ({ documentType, incidentId, filename }) => 
      api.delete(`/documents/delete/${documentType}/${incidentId}/${filename}/`),
    onSuccess: () => {
      queryClient.invalidateQueries(['documents-by-incidents']);
    },
  });

  // Mutación para eliminar todos los documentos de una incidencia
  const deleteAllIncidentDocumentsMutation = useMutation({
    mutationFn: (incidentId) => 
      api.delete(`/documents/delete-all/${incidentId}/`),
    onSuccess: () => {
      queryClient.invalidateQueries(['documents-by-incidents']);
    },
  });

  // Mutación para subir documento
  const uploadDocumentMutation = useMutation({
    mutationFn: (formData) => api.post('/documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: () => {
      queryClient.invalidateQueries(['documents-by-incidents']);
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadFormData({
        title: '',
        description: '',
        document_type: 'general',
        incident_id: ''
      });
      showNotification('Documento subido exitosamente');
    },
    onError: (error) => {
      console.error('Error uploading document:', error);
      alert('Error al subir el documento: ' + (error.response?.data?.error || error.message));
    }
  });

  // Procesar documentos organizados por incidencias
  const allDocuments = React.useMemo(() => {
    const docs = [];
    
    if (documentsByIncidents?.incidents) {
      documentsByIncidents.incidents.forEach(incident => {
        if (incident.documents && incident.documents.length > 0) {
          incident.documents.forEach(doc => {
            docs.push({
              ...doc,
              source: 'incident',
              type: doc.type || 'general',
              incident_id: incident.id,
              incident_code: incident.code,
              incident_title: incident.title,
              filename: doc.filename,
              created_at: doc.created_at,
              status: 'active',
            });
          });
        }
      });
    }
    
    
    return docs;
  }, [documentsByIncidents]);

  // Filtrar documentos
  const filteredDocuments = React.useMemo(() => {
    return allDocuments.filter(doc => {
      const matchesSearch = doc.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           doc.incident_code?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = selectedType === 'all' || doc.type === selectedType;
      const matchesStatus = selectedStatus === 'all' || doc.status === selectedStatus;
      const matchesIncident = selectedIncident === 'all' || doc.incident_id?.toString() === selectedIncident;
      
      return matchesSearch && matchesType && matchesStatus && matchesIncident;
    });
  }, [allDocuments, searchTerm, selectedType, selectedStatus, selectedIncident]);

  // Tipos de documentos disponibles
  const documentTypes = [
    { value: 'all', label: 'Todos los tipos', icon: DocumentTextIcon },
    { value: 'visit-report', label: 'Reportes de Visita', icon: DocumentTextIcon },
    { value: 'lab-report', label: 'Reportes de Laboratorio', icon: DocumentTextIcon },
    { value: 'supplier-report', label: 'Reportes de Proveedores', icon: DocumentTextIcon },
    { value: 'quality-report', label: 'Reportes de Calidad', icon: DocumentTextIcon },
  ];

  // Función para abrir documento en visualizador
  const handleOpenDocument = (document) => {
    setSelectedDocument(document);
    setViewerOpen(true);
  };

  // Función para cerrar visualizador
  const handleCloseViewer = () => {
    setViewerOpen(false);
    setSelectedDocument(null);
  };

  // Función para descargar documento
  const handleDownloadDocument = async (document) => {
    try {
      // Implementar descarga de documento
      console.log('Descargando documento:', document);
      // Aquí se implementaría la lógica de descarga
    } catch (error) {
      console.error('Error downloading document:', error);
    }
  };

  // Función para eliminar documento
  const handleDeleteDocument = async (document) => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar "${document.filename}"?`)) {
      try {
        await deleteDocumentMutation.mutateAsync({
          documentType: document.type,
          incidentId: document.incident_id,
          filename: document.filename,
        });
        alert('Documento eliminado exitosamente');
      } catch (error) {
        console.error('Error eliminando documento:', error);
        alert('Error al eliminar el documento');
      }
    }
  };

  // Función para eliminar todos los documentos de una incidencia
  const handleDeleteAllIncidentDocuments = async (incidentId) => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar TODOS los documentos de esta incidencia?`)) {
      try {
        await deleteAllIncidentDocumentsMutation.mutateAsync(incidentId);
        alert('Documentos eliminados exitosamente');
      } catch (error) {
        console.error('Error eliminando documentos:', error);
        alert('Error al eliminar los documentos');
      }
    }
  };

  // Función para seleccionar/deseleccionar documento
  const toggleDocumentSelection = (documentId) => {
    setSelectedDocuments(prev => 
      prev.includes(documentId) 
        ? prev.filter(id => id !== documentId)
        : [...prev, documentId]
    );
  };

  // Función para seleccionar todos los documentos visibles
  const selectAllDocuments = () => {
    setSelectedDocuments(filteredDocuments.map(doc => doc.id || `${doc.type}-${doc.incident_id}-${doc.filename}`));
  };

  // Función para deseleccionar todos los documentos
  const deselectAllDocuments = () => {
    setSelectedDocuments([]);
  };

  // Función para mostrar notificación
  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => setNotification(null), 3000);
  };

  // Función para limpiar selección
  const handleClearSelection = () => {
    setSelectedDocuments([]);
  };

  // Función para manejar el cambio de archivo
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadFile(file);
      if (!uploadFormData.title) {
        setUploadFormData(prev => ({
          ...prev,
          title: file.name
        }));
      }
    }
  };

  // Función para manejar el upload
  const handleUploadSubmit = (e) => {
    e.preventDefault();
    if (!uploadFile) {
      alert('Por favor selecciona un archivo');
      return;
    }

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('title', uploadFormData.title);
    formData.append('description', uploadFormData.description);
    formData.append('document_type', uploadFormData.document_type);
    if (uploadFormData.incident_id) {
      formData.append('incident_id', uploadFormData.incident_id);
    }

    uploadDocumentMutation.mutate(formData);
  };

  const isLoading = documentsLoading || incidentsLoading;

  return (
    <div className="page-container space-y-6">
      {/* Header con botón de acción */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <DocumentTextIcon className="h-8 w-8 mr-3 text-blue-600" />
            Gestión de Documentos
          </h1>
          <p className="mt-2 text-gray-600">Visualiza, gestiona y carga documentos del sistema</p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 transform hover:scale-105"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Subir Documento
        </button>
      </div>

      {/* Barra de búsqueda y filtros */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Búsqueda */}
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por nombre de archivo o código de incidencia..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Botón de filtros */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <FunnelIcon className="h-5 w-5 mr-2" />
            Filtros
          </button>

          {/* Botón de vista */}
          <div className="flex border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'}`}
            >
              Cuadrícula
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 ${viewMode === 'list' ? 'bg-blue-500 text-white' : 'bg-white text-gray-700'}`}
            >
              Lista
            </button>
          </div>
        </div>

        {/* Filtros expandibles */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Filtro por tipo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Documento
                </label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {documentTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Filtro por estado */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado
                </label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">Todos los estados</option>
                  <option value="active">Activo</option>
                  <option value="archived">Archivado</option>
                  <option value="deleted">Eliminado</option>
                </select>
              </div>

              {/* Filtro por incidencia */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Incidencia
                </label>
                <select
                  value={selectedIncident}
                  onChange={(e) => setSelectedIncident(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">Todas las incidencias</option>
                  {incidents?.results?.map(incident => (
                    <option key={incident.id} value={incident.id.toString()}>
                      {incident.code} - {incident.cliente}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Acciones masivas */}
      <BulkDocumentActions
        selectedDocuments={selectedDocuments}
        documents={filteredDocuments}
        onClearSelection={handleClearSelection}
        onSuccess={showNotification}
      />

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Documentos</p>
              <p className="text-2xl font-bold text-gray-900">{allDocuments.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <EyeIcon className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Filtrados</p>
              <p className="text-2xl font-bold text-gray-900">{filteredDocuments.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <BuildingOfficeIcon className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Incidencias</p>
              <p className="text-2xl font-bold text-gray-900">{incidents?.results?.length || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Seleccionados</p>
              <p className="text-2xl font-bold text-gray-900">{selectedDocuments.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de documentos */}
      <ErrorBoundary>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Documentos ({filteredDocuments.length})
              </h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={selectAllDocuments}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Seleccionar Todos
                </button>
                <button
                  onClick={deselectAllDocuments}
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  Deseleccionar
                </button>
                <button
                  onClick={refetchDocuments}
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  <ArrowPathIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : documentsByIncidents?.incidents?.length === 0 ? (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay documentos</h3>
              <p className="mt-1 text-sm text-gray-500">
                No se encontraron documentos que coincidan con los filtros aplicados.
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {documentsByIncidents?.incidents?.map((incidentGroup) => {
                const incident = incidentGroup.incident;
                const documents = incidentGroup.documents;
                
                // Filtrar documentos de esta incidencia
                const filteredIncidentDocuments = documents.filter(doc => {
                  const matchesSearch = doc.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                       doc.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                       incident.code?.toLowerCase().includes(searchTerm.toLowerCase());
                  const matchesType = selectedType === 'all' || doc.type === selectedType;
                  const matchesStatus = selectedStatus === 'all' || doc.status === selectedStatus;
                  const matchesIncident = selectedIncident === 'all' || incident.id?.toString() === selectedIncident;
                  
                  return matchesSearch && matchesType && matchesStatus && matchesIncident;
                });
                
                if (filteredIncidentDocuments.length === 0) return null;
                
                return (
                  <DocumentsByIncident
                    key={incident.id}
                    incident={incident}
                    documents={filteredIncidentDocuments}
                    viewMode={viewMode}
                    selectedDocuments={selectedDocuments}
                    onToggleSelection={toggleDocumentSelection}
                    onViewDocument={handleOpenDocument}
                    onDownloadDocument={handleDownloadDocument}
                    onDeleteDocument={handleDeleteDocument}
                  />
                );
              })}
            </div>
          )}
        </div>
      </ErrorBoundary>

      {/* Visualizador de documentos */}
      <DocumentViewer
        isOpen={viewerOpen}
        onClose={handleCloseViewer}
        document={selectedDocument}
          onError={(error) => {
          console.error('Error en visualizador:', error);
          alert('Error al cargar el documento');
        }}
      />

      {/* Modal de Upload */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl">
            <div className="px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center">
                  <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
                  Subir Documento
                </h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="text-white hover:text-gray-200 transition-colors duration-200"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>
            
            <form onSubmit={handleUploadSubmit} className="p-6">
              <div className="space-y-4">
                {/* Archivo */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Seleccionar Archivo *
                  </label>
                  <input
                    type="file"
                    onChange={handleFileChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {uploadFile && (
                    <p className="mt-2 text-sm text-gray-600">
                      Archivo seleccionado: {uploadFile.name}
                    </p>
                  )}
                </div>

                {/* Título */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Título del Documento *
                  </label>
                  <input
                    type="text"
                    value={uploadFormData.title}
                    onChange={(e) => setUploadFormData(prev => ({ ...prev, title: e.target.value }))}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Ej: Reporte de Calidad - Cliente XYZ"
                  />
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Descripción
                  </label>
                  <textarea
                    value={uploadFormData.description}
                    onChange={(e) => setUploadFormData(prev => ({ ...prev, description: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Descripción opcional del documento..."
                  />
                </div>

                {/* Tipo de Documento */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tipo de Documento *
                  </label>
                  <select
                    value={uploadFormData.document_type}
                    onChange={(e) => setUploadFormData(prev => ({ ...prev, document_type: e.target.value }))}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="general">General</option>
                    <option value="visit-report">Reporte de Visita</option>
                    <option value="quality-report">Reporte de Calidad</option>
                    <option value="supplier-report">Reporte de Proveedor</option>
                    <option value="lab-report">Reporte de Laboratorio</option>
                    <option value="invoice">Factura</option>
                    <option value="contract">Contrato</option>
                    <option value="other">Otro</option>
                  </select>
                </div>

                {/* Incidencia (opcional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Asociar a Incidencia (Opcional)
                  </label>
                  <select
                    value={uploadFormData.incident_id}
                    onChange={(e) => setUploadFormData(prev => ({ ...prev, incident_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Sin asociar</option>
                    {incidents?.results?.map(incident => (
                      <option key={incident.id} value={incident.id}>
                        {incident.code} - {incident.cliente}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Botones */}
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-6 py-2 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={uploadDocumentMutation.isPending}
                  className="inline-flex items-center px-6 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploadDocumentMutation.isPending ? (
                    <>
                      <ArrowPathIcon className="animate-spin h-4 w-4 mr-2" />
                      Subiendo...
                    </>
                  ) : (
                    <>
                      <CheckCircleIcon className="h-4 w-4 mr-2" />
                      Subir Documento
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Notificación */}
      {notification && (
        <div className="fixed top-4 right-4 z-50">
          <div className="bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg">
            {notification}
          </div>
        </div>
      )}
    </div>
  );
};

export default Documents;