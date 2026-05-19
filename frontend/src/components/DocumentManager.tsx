import React, { useState, useCallback } from 'react';
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
} from '@heroicons/react/24/outline';
import useDocumentManager from '../hooks/useDocumentManager';

/**
 * Componente profesional para gestión de documentos adjuntos
 * Maneja subida, visualización, descarga y eliminación de documentos
 */
const DocumentManager = ({ 
  incidentId, 
  documentType, 
  onDocumentUploaded, 
  onDocumentDeleted,
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

  // Manejar subida de archivo
  const handleUpload = useCallback(async () => {
    if (!selectedFile || !incidentId) return;

    setIsUploading(true);
    try {
      await uploadDocument.mutateAsync({
        file: selectedFile,
        incidentId,
        documentType,
        description,
        isPublic,
      });
      
      setShowUploadModal(false);
      setSelectedFile(null);
      setDescription('');
      setIsPublic(false);
      
      if (onDocumentUploaded) {
        onDocumentUploaded();
      }
    } catch (error) {
      console.error('Error uploading document:', error);
    }
  }, [selectedFile, incidentId, documentType, description, isPublic, uploadDocument, onDocumentUploaded]);

  // Manejar eliminación de documento
  const handleDelete = useCallback(async (filename) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este documento?')) {
      return;
    }

    try {
      await deleteDocument.mutateAsync({
        incidentId,
        documentType,
        filename,
      });
      
      if (onDocumentDeleted) {
        onDocumentDeleted();
      }
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  }, [deleteDocument, incidentId, documentType, onDocumentDeleted]);

  // Manejar descarga de documento
  const handleDownload = useCallback(async (filename) => {
    try {
      await downloadDocument(incidentId, documentType, filename);
    } catch (error) {
      console.error('Error downloading document:', error);
    }
  }, [downloadDocument, incidentId, documentType]);

  // Manejar visualización de documento
  const handleView = useCallback((filename) => {
    openDocument(incidentId, documentType, filename);
  }, [openDocument, incidentId, documentType]);

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <DocumentTextIcon className="h-5 w-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">
              Documentos Adjuntos
            </h3>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            <CloudArrowUpIcon className="h-4 w-4 mr-2" />
            Subir Documento
          </button>
        </div>
      </div>

      {/* Lista de documentos */}
      <div className="p-6">
        <div className="text-center text-gray-500 py-8">
          <DocumentTextIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No hay documentos adjuntos</p>
          <p className="text-sm">Sube documentos para comenzar</p>
        </div>
      </div>

      {/* Modal de subida */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Subir Documento
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
                {isUploading ? 'Subiendo...' : 'Subir Documento'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentManager;
