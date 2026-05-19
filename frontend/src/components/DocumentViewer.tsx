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
    if (!bytes || bytes === 0) return '0 KB';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  // Formatear fecha
  const formatDate = useCallback((dateString) => {
    if (!dateString) return 'Sin fecha';
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

  // Obtener icono según tipo de archivo
  const getFileIcon = useCallback((filename) => {
    if (!filename) return '📄';
    const extension = filename.split('.').pop()?.toLowerCase();
    const icons = {
      pdf: '📄', doc: '📝', docx: '📝', xls: '📊', xlsx: '📊',
      ppt: '📈', pptx: '📈', jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️',
      txt: '📄', zip: '🗜️', rar: '🗜️',
    };
    return icons[extension] || '📄';
  }, []);

  // Manejar visualización
  const handleView = useCallback((document) => {
    if (onView) onView(document);
  }, [onView]);

  // Manejar descarga
  const handleDownload = useCallback((document) => {
    if (onDownload) onDownload(document);
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
            {[1, 2, 3].map((i) => (
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

  if (!documents || documents.length === 0) {
    return null;
  }

  return (
    <>
      <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
        <div className="divide-y divide-gray-200">
          {documents.map((doc, index) => (
            <div key={doc.id || index} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-4">
                {/* Icono */}
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span className="text-lg">{getFileIcon(doc.filename)}</span>
                  </div>
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex-col">
                    <div className="flex items-center">
                      <h4 className="text-sm font-medium text-gray-900 truncate">{doc.description || doc.filename || doc.title}</h4>
                      {doc.is_public ? (
                        <GlobeAltIcon className="h-4 w-4 text-green-500 ml-2 flex-shrink-0" title="Público" />
                      ) : (
                        <LockClosedIcon className="h-4 w-4 text-gray-400 ml-2 flex-shrink-0" title="Privado" />
                      )}
                    </div>
                    {doc.description && doc.description !== doc.filename && (
                      <p className="text-xs text-gray-500 truncate mt-0.5">{doc.filename}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                    <span className="flex items-center">
                      <CalendarIcon className="h-3 w-3 mr-1" />
                      {formatDate(doc.created_at)}
                    </span>
                    <span className="flex items-center">
                      <UserIcon className="h-3 w-3 mr-1" />
                      {doc.created_by || 'Sistema'}
                    </span>
                    <span className="flex items-center">
                      <DocumentTextIcon className="h-3 w-3 mr-1" />
                      {formatFileSize(doc.size)}
                    </span>
                  </div>
                </div>

                {/* Acciones */}
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleView(doc)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg"
                    title="Ver"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDownload(doc)}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg"
                    title="Descargar"
                  >
                    <DocumentArrowDownIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(doc)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
                    title="Eliminar"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal confirmación */}
      {showDeleteConfirm && selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Confirmar Eliminación</h3>
              <button onClick={() => setShowDeleteConfirm(false)} className="text-gray-400 hover:text-gray-600">
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="px-6 py-4">
              <p className="text-sm text-gray-900">¿Eliminar <strong>{selectedDocument.filename}</strong>?</p>
              <p className="text-xs text-gray-500 mt-1">Esta acción no se puede deshacer</p>
            </div>
            <div className="px-6 py-4 bg-gray-50 rounded-b-lg flex justify-end space-x-3">
              <button onClick={() => setShowDeleteConfirm(false)} className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
                Cancelar
              </button>
              <button onClick={confirmDelete} className="px-4 py-2 text-sm text-white bg-red-600 rounded-md hover:bg-red-700">
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