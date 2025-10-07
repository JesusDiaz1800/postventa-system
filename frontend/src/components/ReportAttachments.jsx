import React, { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  DocumentArrowUpIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  TrashIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PaperClipIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowUpTrayIcon,
  DocumentIcon,
  CalendarIcon,
  UserIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import useDocumentManager from '../hooks/useDocumentManager';
import { api } from '../services/api';

/**
 * Componente optimizado para gestión de adjuntos en reportes
 * Reutiliza la lógica optimizada de IncidentAttachments
 */
const ReportAttachments = ({ 
  reportId, 
  reportType, 
  onAttachmentUploaded, 
  onAttachmentDeleted,
  className = "" 
}) => {
  const {
    uploadDocument,
    deleteDocument,
    downloadDocument,
    openDocument,
    uploadProgress,
    isUploading,
    setIsUploading,
  } = useDocumentManager();

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [viewMode, setViewMode] = useState('list');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showBulkActions, setShowBulkActions] = useState(false);

  // Obtener adjuntos del reporte
  const { 
    data: attachments = [], 
    isLoading: attachmentsLoading, 
    error: attachmentsError,
    refetch: refetchAttachments 
  } = useQuery({
    queryKey: ['report-attachments', reportId, reportType],
    queryFn: async () => {
      if (!reportId || !reportType) return [];
      try {
        const response = await api.get(`/documents/report-attachments/${reportId}/${reportType}/`);
        return response.data.attachments || [];
      } catch (error) {
        console.error('Error fetching report attachments:', error);
        return [];
      }
    },
    enabled: !!reportId && !!reportType,
  });

  // Manejar selección de archivo
  const handleFileSelect = useCallback((file) => {
    if (file) {
      setSelectedFile(file);
      setDescription(file.name);
    }
  }, []);

  // Manejar drag and drop
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, [handleFileSelect]);

  // Filtrar y ordenar adjuntos
  const filteredAttachments = useMemo(() => {
    let filtered = Array.isArray(attachments) ? attachments : [];
    
    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(attachment =>
        attachment.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        attachment.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        attachment.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Filtrar por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(attachment => {
        const extension = attachment.filename?.split('.').pop()?.toLowerCase();
        switch (filterType) {
          case 'pdf':
            return extension === 'pdf';
          case 'image':
            return ['jpg', 'jpeg', 'png', 'gif'].includes(extension);
          case 'document':
            return ['doc', 'docx', 'txt'].includes(extension);
          case 'spreadsheet':
            return ['xls', 'xlsx', 'csv'].includes(extension);
          default:
            return true;
        }
      });
    }
    
    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return (a.filename || '').localeCompare(b.filename || '');
        case 'size':
          return (b.size || 0) - (a.size || 0);
        case 'date':
        default:
          return new Date(b.created_at || 0) - new Date(a.created_at || 0);
      }
    });
    
    return filtered;
  }, [attachments, searchTerm, filterType, sortBy]);

  // Manejar subida de archivo
  const handleUpload = useCallback(async () => {
    if (!selectedFile || !reportId) return;

    setIsUploading(true);
    try {
      await uploadDocument.mutateAsync({
        file: selectedFile,
        incidentId: reportId, // Usar reportId como incidentId para la lógica existente
        documentType: reportType,
        description,
        isPublic,
      });
      
      setShowUploadModal(false);
      setSelectedFile(null);
      setDescription('');
      setIsPublic(false);
      
      refetchAttachments();
      if (onAttachmentUploaded) {
        onAttachmentUploaded();
      }
    } catch (error) {
      console.error('Error uploading attachment:', error);
    }
  }, [selectedFile, reportId, reportType, description, isPublic, uploadDocument, onAttachmentUploaded, refetchAttachments]);

  // Manejar eliminación de archivo
  const handleDeleteAttachment = useCallback(async (attachmentId) => {
    try {
      await deleteDocument.mutateAsync({
        incidentId: reportId,
        documentType: reportType,
        attachmentId,
      });
      
      refetchAttachments();
      if (onAttachmentDeleted) {
        onAttachmentDeleted();
      }
    } catch (error) {
      console.error('Error deleting attachment:', error);
    }
  }, [deleteDocument, reportId, reportType, refetchAttachments, onAttachmentDeleted]);

  // Manejar descarga de archivo
  const handleDownloadAttachment = useCallback(async (attachment) => {
    try {
      await downloadDocument(reportId, reportType, attachment.id);
    } catch (error) {
      console.error('Error downloading attachment:', error);
    }
  }, [downloadDocument, reportId, reportType]);

  // Manejar visualización de archivo
  const handleViewAttachment = useCallback((attachment) => {
    try {
      openDocument(reportId, reportType, attachment.id);
    } catch (error) {
      console.error('Error viewing attachment:', error);
    }
  }, [openDocument, reportId, reportType]);

  // Utilidades
  const getFileIcon = useCallback((filename) => {
    const extension = filename?.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <DocumentTextIcon className="h-5 w-5 text-red-500" />;
      case 'doc':
      case 'docx':
        return <DocumentIcon className="h-5 w-5 text-blue-500" />;
      case 'xls':
      case 'xlsx':
        return <DocumentIcon className="h-5 w-5 text-green-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <DocumentIcon className="h-5 w-5 text-purple-500" />;
      default:
        return <DocumentIcon className="h-5 w-5 text-gray-500" />;
    }
  }, []);

  const formatFileSize = useCallback((bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  const formatDate = useCallback((dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }, []);

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <PaperClipIcon className="h-5 w-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">
              Documentos Adjuntos
            </h3>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            <CloudArrowUpIcon className="h-4 w-4 mr-2" />
            Adjuntar Documento
          </button>
        </div>
      </div>

      {/* Controles de búsqueda y filtros */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Búsqueda */}
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar documentos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          {/* Filtros */}
          <div className="flex gap-2">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">Todos los tipos</option>
              <option value="pdf">PDF</option>
              <option value="image">Imágenes</option>
              <option value="document">Documentos</option>
              <option value="spreadsheet">Hojas de cálculo</option>
            </select>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="date">Fecha</option>
              <option value="name">Nombre</option>
              <option value="size">Tamaño</option>
            </select>
          </div>
        </div>
      </div>

      {/* Lista de documentos */}
      <div className="p-6">
        {attachmentsLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-500">Cargando documentos...</p>
          </div>
        ) : attachmentsError ? (
          <div className="text-center py-8">
            <ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-4 text-red-400" />
            <p className="text-red-600">Error al cargar documentos</p>
            <button
              onClick={() => refetchAttachments()}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Reintentar
            </button>
          </div>
        ) : filteredAttachments.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No hay documentos adjuntos</p>
            <p className="text-sm">Adjunta documentos para respaldar el reporte</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredAttachments.map((attachment) => (
              <div
                key={attachment.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  {getFileIcon(attachment.filename)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {attachment.title || attachment.filename}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        {formatDate(attachment.created_at)}
                      </span>
                      <span className="flex items-center">
                        <UserIcon className="h-4 w-4 mr-1" />
                        {attachment.created_by}
                      </span>
                      <span>{formatFileSize(attachment.size)}</span>
                    </div>
                    {attachment.description && (
                      <p className="text-xs text-gray-600 mt-1 truncate">
                        {attachment.description}
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleViewAttachment(attachment)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Ver documento"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDownloadAttachment(attachment)}
                    className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                    title="Descargar documento"
                  >
                    <DocumentArrowDownIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteAttachment(attachment.id)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                    title="Eliminar documento"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal de subida */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Adjuntar Documento
                </h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="px-6 py-4">
              {/* Área de drag and drop */}
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                  dragActive
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {selectedFile ? (
                  <div className="space-y-2">
                    <CheckCircleIcon className="h-8 w-8 text-green-500 mx-auto" />
                    <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <CloudArrowUpIcon className="h-8 w-8 text-gray-400 mx-auto" />
                    <p className="text-sm text-gray-600">
                      Arrastra un archivo aquí o haz clic para seleccionar
                    </p>
                    <input
                      type="file"
                      onChange={(e) => handleFileSelect(e.target.files[0])}
                      className="hidden"
                      id="file-upload"
                      accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png"
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
                    >
                      Seleccionar Archivo
                    </label>
                  </div>
                )}
              </div>

              {/* Descripción */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descripción (opcional)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Describe el contenido del documento..."
                />
              </div>

              {/* Visibilidad */}
              <div className="mt-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    Documento público (visible para todos)
                  </span>
                </label>
              </div>

              {/* Barra de progreso */}
              {isUploading && (
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                    <span>Subiendo...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Botones */}
            <div className="px-6 py-4 bg-gray-50 rounded-b-lg flex justify-end space-x-3">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Cancelar
              </button>
              <button
                onClick={handleUpload}
                disabled={!selectedFile || isUploading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? 'Subiendo...' : 'Adjuntar Documento'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportAttachments;

