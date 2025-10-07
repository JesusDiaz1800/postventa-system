import React, { useState, useCallback } from 'react';
import {
  EyeIcon,
  DocumentArrowDownIcon,
  TrashIcon,
  DocumentTextIcon,
  CalendarIcon,
  UserIcon,
  GlobeAltIcon,
  LockClosedIcon,
  XMarkIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

/**
 * Componente profesional para visualización y gestión de documentos
 * Muestra información detallada y acciones disponibles para cada documento
 */
const DocumentViewer = ({ 
  documents = [], 
  onView, 
  onDownload, 
  onDelete, 
  isLoading = false,
  className = "" 
}) => {
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

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
      case 'txt':
        return '📄';
      default:
        return '📄';
    }
  }, []);

  // Manejar visualización
  const handleView = useCallback((document) => {
    if (onView) {
      onView(document);
    }
  }, [onView]);

  // Manejar descarga
  const handleDownload = useCallback((document) => {
    if (onDownload) {
      onDownload(document);
    }
  }, [onDownload]);

  // Manejar eliminación
  const handleDelete = useCallback((document) => {
    setSelectedDocument(document);
    setShowDeleteConfirm(true);
  }, []);

  // Confirmar eliminación
  const confirmDelete = useCallback(() => {
    if (selectedDocument && onDelete) {
      onDelete(selectedDocument);
    }
    setShowDeleteConfirm(false);
    setSelectedDocument(null);
  }, [selectedDocument, onDelete]);

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
        <div className="p-6">
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
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
        <div className="p-6 text-center">
          <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay documentos
          </h3>
          <p className="text-gray-500">
            Los documentos aparecerán aquí cuando se suban
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Documentos ({documents.length})
          </h3>
        </div>

        <div className="divide-y divide-gray-200">
          {documents.map((document, index) => (
            <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start space-x-4">
                {/* Icono del archivo */}
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-lg">{getFileIcon(document.filename)}</span>
                  </div>
                </div>

                {/* Información del documento */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {document.filename}
                    </h4>
                    <div className="flex items-center space-x-2">
                      {document.is_public ? (
                        <GlobeAltIcon className="h-4 w-4 text-green-500" title="Público" />
                      ) : (
                        <LockClosedIcon className="h-4 w-4 text-gray-400" title="Privado" />
                      )}
                    </div>
                  </div>

                  {document.description && (
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                      {document.description}
                    </p>
                  )}

                  <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                    <div className="flex items-center">
                      <CalendarIcon className="h-3 w-3 mr-1" />
                      {formatDate(document.created_at)}
                    </div>
                    <div className="flex items-center">
                      <UserIcon className="h-3 w-3 mr-1" />
                      {document.uploaded_by || 'Sistema'}
                    </div>
                    <div className="flex items-center">
                      <DocumentTextIcon className="h-3 w-3 mr-1" />
                      {formatFileSize(document.size)}
                    </div>
                  </div>
                </div>

                {/* Acciones */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleView(document)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Ver documento"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDownload(document)}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Descargar documento"
                  >
                    <DocumentArrowDownIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(document)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Eliminar documento"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de confirmación de eliminación */}
      {showDeleteConfirm && selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Confirmar Eliminación
                </h3>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="px-6 py-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                  <TrashIcon className="h-5 w-5 text-red-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-900">
                    ¿Estás seguro de que quieres eliminar este documento?
                  </p>
                  <p className="text-sm font-medium text-gray-700 mt-1">
                    {selectedDocument.filename}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Esta acción no se puede deshacer
                  </p>
                </div>
              </div>
            </div>

            <div className="px-6 py-4 bg-gray-50 rounded-b-lg flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Cancelar
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DocumentViewer;