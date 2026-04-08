import React, { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  BuildingOfficeIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';
import { api } from '../services/api';
import { useNotifications } from '../hooks/useNotifications';

/**
 * Componente especializado para gestión de adjuntos en reportes de proveedores
 * Maneja dos tipos de documentos: "reporte_para_proveedor" y "respuesta_de_proveedor"
 */
const SupplierReportAttachments = ({ 
  reportId, 
  onAttachmentUploaded, 
  onAttachmentDeleted,
  className = "" 
}) => {
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [documentType, setDocumentType] = useState('reporte_para_proveedor');
  const [isPublic, setIsPublic] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Obtener adjuntos del reporte de proveedor
  const { 
    data: attachments = [], 
    isLoading: attachmentsLoading, 
    error: attachmentsError,
    refetch: refetchAttachments 
  } = useQuery({
    queryKey: ['supplier-report-attachments', reportId],
    queryFn: async () => {
      if (!reportId) return [];
      try {
        const response = await api.get(`/documents/supplier-reports/${reportId}/attachments/`);
        return response.data.attachments || [];
      } catch (error) {
        console.error('Error fetching supplier report attachments:', error);
        return [];
      }
    },
    enabled: !!reportId,
  });

  // Mutación para subir documento
  const uploadAttachmentMutation = useMutation({
    mutationFn: async ({ file, documentType, description, isPublic }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      formData.append('description', description);
      formData.append('is_public', isPublic);
      formData.append('report_id', reportId);

      const response = await api.post('/documents/supplier-reports/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });

      return response.data;
    },
    onSuccess: () => {
      showSuccess('Documento adjuntado exitosamente');
      refetchAttachments();
      if (onAttachmentUploaded) {
        onAttachmentUploaded();
      }
    },
    onError: (error) => {
      console.error('Error uploading attachment:', error);
      showError('Error al adjuntar el documento');
    },
  });

  // Mutación para eliminar documento
  const deleteAttachmentMutation = useMutation({
    mutationFn: async (attachmentId) => {
      await api.delete(`/documents/supplier-reports/attachments/${attachmentId}/`);
    },
    onSuccess: () => {
      showSuccess('Documento eliminado exitosamente');
      refetchAttachments();
      if (onAttachmentDeleted) {
        onAttachmentDeleted();
      }
    },
    onError: (error) => {
      console.error('Error deleting attachment:', error);
      showError('Error al eliminar el documento');
    },
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
    
    // Filtrar por tipo de documento
    if (filterType !== 'all') {
      filtered = filtered.filter(attachment => attachment.document_type === filterType);
    }
    
    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return (a.filename || '').localeCompare(b.filename || '');
        case 'type':
          return (a.document_type || '').localeCompare(b.document_type || '');
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
    setUploadProgress(0);
    
    try {
      await uploadAttachmentMutation.mutateAsync({
        file: selectedFile,
        documentType,
        description,
        isPublic,
      });
      
      setShowUploadModal(false);
      setSelectedFile(null);
      setDescription('');
      setIsPublic(false);
      setDocumentType('reporte_para_proveedor');
    } catch (error) {
      console.error('Error uploading attachment:', error);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [selectedFile, reportId, documentType, description, isPublic, uploadAttachmentMutation]);

  // Manejar eliminación de archivo
  const handleDeleteAttachment = useCallback(async (attachmentId) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este documento?')) {
      await deleteAttachmentMutation.mutateAsync(attachmentId);
    }
  }, [deleteAttachmentMutation]);

  // Manejar descarga de archivo
  const handleDownloadAttachment = useCallback(async (attachment) => {
    try {
      const response = await api.get(`/documents/supplier-reports/attachments/${attachment.id}/download/`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', attachment.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading attachment:', error);
      showError('Error al descargar el documento');
    }
  }, [showError]);

  // Manejar visualización de archivo
  const handleViewAttachment = useCallback(async (attachment) => {
    try {
      const response = await api.get(`/documents/supplier-reports/attachments/${attachment.id}/view/`, {
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      window.open(url, '_blank');
    } catch (error) {
      console.error('Error viewing attachment:', error);
      showError('Error al visualizar el documento');
    }
  }, [showError]);

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

  const getDocumentTypeIcon = useCallback((type) => {
    switch (type) {
      case 'reporte_para_proveedor':
        return <BuildingOfficeIcon className="h-4 w-4 text-blue-500" />;
      case 'respuesta_de_proveedor':
        return <ChatBubbleLeftRightIcon className="h-4 w-4 text-green-500" />;
      default:
        return <DocumentIcon className="h-4 w-4 text-gray-500" />;
    }
  }, []);

  const getDocumentTypeLabel = useCallback((type) => {
    switch (type) {
      case 'reporte_para_proveedor':
        return 'Reporte para Proveedor';
      case 'respuesta_de_proveedor':
        return 'Respuesta de Proveedor';
      default:
        return type;
    }
  }, []);

  const getDocumentTypeColor = useCallback((type) => {
    switch (type) {
      case 'reporte_para_proveedor':
        return 'bg-blue-100 text-blue-800';
      case 'respuesta_de_proveedor':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
              Documentos de Proveedor
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
              <option value="reporte_para_proveedor">Reporte para Proveedor</option>
              <option value="respuesta_de_proveedor">Respuesta de Proveedor</option>
            </select>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="date">Fecha</option>
              <option value="name">Nombre</option>
              <option value="type">Tipo</option>
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
            <p className="text-sm">Adjunta documentos para respaldar el reporte de proveedor</p>
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
                    <div className="flex items-center space-x-2 mb-1">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {attachment.title || attachment.filename}
                      </p>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getDocumentTypeColor(attachment.document_type)}`}>
                        {getDocumentTypeIcon(attachment.document_type)}
                        <span className="ml-1">{getDocumentTypeLabel(attachment.document_type)}</span>
                      </span>
                    </div>
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
              {/* Tipo de documento */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Documento
                </label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="reporte_para_proveedor">Reporte para Proveedor</option>
                  <option value="respuesta_de_proveedor">Respuesta de Proveedor</option>
                </select>
              </div>

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

export default SupplierReportAttachments;
