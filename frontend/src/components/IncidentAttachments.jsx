import React, { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PaperClipIcon,
  DocumentIcon,
  PhotoIcon,
  VideoCameraIcon,
  SpeakerWaveIcon,
  TrashIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  PlusIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  ArchiveBoxIcon,
  ShareIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  CalendarIcon,
  UserIcon,
  GlobeAltIcon,
  LockClosedIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';
import DocumentManager from './DocumentManager';
import DocumentViewer from './DocumentViewer';

/**
 * Componente profesional para gestión de documentos adjuntos de incidencias
 * Integra subida, visualización, descarga y eliminación de documentos
 */
const IncidentAttachments = ({ incidentId, incidentCode }) => {
  console.log('=== INCIDENT ATTACHMENTS COMPONENT LOADED ===');
  console.log('Incident ID:', incidentId);
  console.log('Incident Code:', incidentCode);
  
  // Estados principales
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [viewMode, setViewMode] = useState('list');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showBulkActions, setShowBulkActions] = useState(false);
  
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  // Obtener documentos adjuntos
  const { 
    data: attachments = [], 
    isLoading: attachmentsLoading, 
    error: attachmentsError,
    refetch: refetchAttachments 
  } = useQuery({
    queryKey: ['incident-attachments', incidentId],
    queryFn: async () => {
      if (!incidentId) return [];
      try {
        const response = await api.get(`/documents/incident-attachments/${incidentId}/`);
        return response.data.attachments || [];
      } catch (error) {
        console.error('Error fetching attachments:', error);
        return [];
      }
    },
    enabled: !!incidentId,
  });

  // Mutación para eliminar documento
  const deleteAttachmentMutation = useMutation({
    mutationFn: async (attachmentId) => {
      const response = await api.delete(`/documents/incident-attachments/${incidentId}/${attachmentId}/delete/`);
        return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['incident-attachments', incidentId]);
      showSuccess('Documento eliminado exitosamente');
    },
    onError: (error) => {
      console.error('Error deleting attachment:', error);
      showError('Error al eliminar el documento');
    },
  });

  // Filtrar y ordenar documentos
  const filteredAttachments = useMemo(() => {
    let filtered = Array.isArray(attachments) ? attachments : [];

    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(attachment =>
        attachment.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (attachment.description && attachment.description.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Filtrar por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(attachment => {
        const extension = attachment.filename.split('.').pop()?.toLowerCase();
        switch (filterType) {
          case 'images':
            return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension);
          case 'documents':
            return ['pdf', 'doc', 'docx', 'txt', 'rtf'].includes(extension);
          case 'spreadsheets':
            return ['xls', 'xlsx', 'csv'].includes(extension);
          case 'presentations':
            return ['ppt', 'pptx'].includes(extension);
          case 'videos':
            return ['mp4', 'avi', 'mov', 'wmv', 'flv'].includes(extension);
          case 'audio':
            return ['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(extension);
          default:
            return true;
        }
      });
    }

    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.filename.localeCompare(b.filename);
        case 'size':
          return b.size - a.size;
        case 'date':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

    return filtered;
  }, [attachments, searchTerm, filterType, sortBy]);

  // Manejar visualización de documento
  const handleViewDocument = useCallback(async (attachment) => {
    try {
      const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}/api/documents/incident-attachments/${incidentId}/${attachment.id}/view/`;
      window.open(url, '_blank');
    } catch (error) {
      console.error('Error opening document:', error);
      showError('Error al abrir el documento');
    }
  }, [incidentId, showError]);

  // Manejar descarga de documento
  const handleDownloadDocument = useCallback(async (attachment) => {
    try {
      const response = await api.get(
        `/documents/incident-attachments/${incidentId}/${attachment.id}/download/`,
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = attachment.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading document:', error);
      showError('Error al descargar el documento');
    }
  }, [incidentId, showError]);

  // Manejar eliminación de documento
  const handleDeleteDocument = useCallback((attachment) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este documento?')) {
      deleteAttachmentMutation.mutate(attachment.id);
    }
  }, [deleteAttachmentMutation]);

  // Manejar selección de archivos
  const handleFileSelection = useCallback((attachmentId, isSelected) => {
    setSelectedFiles(prev => 
      isSelected 
        ? [...prev, attachmentId]
        : prev.filter(id => id !== attachmentId)
    );
  }, []);

  // Seleccionar todos los archivos
  const handleSelectAll = useCallback(() => {
    setSelectedFiles(filteredAttachments.map(attachment => attachment.id));
  }, [filteredAttachments]);

  // Limpiar selección
  const handleClearSelection = useCallback(() => {
    setSelectedFiles([]);
  }, []);

  // Acciones en lote
  const handleBulkDownload = useCallback(async () => {
    for (const attachmentId of selectedFiles) {
      const attachment = attachments.find(a => a.id === attachmentId);
      if (attachment) {
        await handleDownloadDocument(attachment);
        // Pequeña pausa entre descargas
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
    setSelectedFiles([]);
    setShowBulkActions(false);
  }, [selectedFiles, attachments, handleDownloadDocument]);

  const handleBulkDelete = useCallback(() => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar ${selectedFiles.length} documentos?`)) {
      selectedFiles.forEach(attachmentId => {
        deleteAttachmentMutation.mutate(attachmentId);
      });
      setSelectedFiles([]);
      setShowBulkActions(false);
    }
  }, [selectedFiles, deleteAttachmentMutation]);

  // Obtener icono según tipo de archivo
  const getFileIcon = useCallback((filename) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'doc':
      case 'docx':
        return '📝';
      case 'xls':
      case 'xlsx':
        return '📊';
      case 'ppt':
      case 'pptx':
        return '📈';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return '🖼️';
      case 'mp4':
      case 'avi':
      case 'mov':
        return '🎥';
      case 'mp3':
      case 'wav':
        return '🎵';
      case 'txt':
        return '📄';
      default:
        return '📄';
    }
  }, []);

  // Formatear tamaño de archivo
  const formatFileSize = useCallback((bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  // Formatear fecha
  const formatDate = useCallback((dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

  if (!incidentId) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No se ha seleccionado ninguna incidencia</p>
      </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
      <div className="flex items-center justify-between">
            <div className="flex items-center">
              <PaperClipIcon className="h-6 w-6 text-blue-600 mr-3" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Documentos Adjuntos
                </h3>
                <p className="text-sm text-gray-500">
                  Incidencia {incidentCode} • {attachments.length} documento{attachments.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  showFilters 
                    ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filtros
              </button>
        <button
                onClick={() => refetchAttachments()}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Actualizar
        </button>
            </div>
          </div>
      </div>

        {/* Filtros */}
        {showFilters && (
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Búsqueda */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Buscar
                </label>
                <div className="relative">
                  <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Buscar por nombre o descripción..."
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Filtro por tipo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de archivo
                </label>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">Todos los tipos</option>
                  <option value="images">Imágenes</option>
                  <option value="documents">Documentos</option>
                  <option value="spreadsheets">Hojas de cálculo</option>
                  <option value="presentations">Presentaciones</option>
                  <option value="videos">Videos</option>
                  <option value="audio">Audio</option>
                </select>
              </div>

              {/* Ordenar por */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ordenar por
                </label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="date">Fecha (más reciente)</option>
                  <option value="name">Nombre (A-Z)</option>
                  <option value="size">Tamaño (mayor a menor)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Acciones en lote */}
        {selectedFiles.length > 0 && (
          <div className="px-6 py-3 bg-blue-50 border-b border-blue-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CheckCircleIcon className="h-5 w-5 text-blue-600 mr-2" />
                <span className="text-sm font-medium text-blue-900">
                  {selectedFiles.length} documento{selectedFiles.length !== 1 ? 's' : ''} seleccionado{selectedFiles.length !== 1 ? 's' : ''}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleBulkDownload}
                  className="inline-flex items-center px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                  Descargar
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="inline-flex items-center px-3 py-1 text-sm font-medium text-red-700 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
                >
                  <TrashIcon className="h-4 w-4 mr-1" />
                  Eliminar
                </button>
                <button
                  onClick={handleClearSelection}
                  className="inline-flex items-center px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <XMarkIcon className="h-4 w-4 mr-1" />
                  Cancelar
                </button>
              </div>
            </div>
        </div>
      )}
            </div>
            
      {/* Gestor de documentos */}
      <DocumentManager
        incidentId={incidentId}
        documentType="incident_attachments"
        onDocumentUploaded={() => {
          refetchAttachments();
          showSuccess('Documento subido exitosamente');
        }}
        onDocumentDeleted={() => {
          refetchAttachments();
          showSuccess('Documento eliminado exitosamente');
        }}
      />

      {/* Lista de documentos */}
      <DocumentViewer
        documents={filteredAttachments}
        onView={handleViewDocument}
        onDownload={handleDownloadDocument}
        onDelete={handleDeleteDocument}
        isLoading={attachmentsLoading}
      />

      {/* Estado de carga */}
      {attachmentsLoading && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="animate-pulse space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gray-200 rounded"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
              </div>
            </div>
      )}

      {/* Estado de error */}
      {attachmentsError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-sm text-red-700">
              Error al cargar los documentos. Intenta actualizar la página.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentAttachments;