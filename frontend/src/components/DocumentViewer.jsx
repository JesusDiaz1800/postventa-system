import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import {
  XMarkIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const DocumentViewer = ({ isOpen, onClose, document, onError }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [documentUrl, setDocumentUrl] = useState(null);

  useEffect(() => {
    if (isOpen && document) {
      loadDocument();
    }
  }, [isOpen, document]);

  const loadDocument = async () => {
    if (!document) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(
        `/documents/open/${document.type.replace('_', '-')}/${document.incident_id}/${document.filename}/`,
        { responseType: 'blob' }
      );
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      setDocumentUrl(url);
    } catch (error) {
      console.error('Error cargando documento:', error);
      setError('Error al cargar el documento. Verifique que el archivo existe.');
      if (onError) onError(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (documentUrl) {
      const link = document.createElement('a');
      link.href = documentUrl;
      link.download = document.filename;
      link.click();
    }
  };

  const handleClose = () => {
    if (documentUrl) {
      window.URL.revokeObjectURL(documentUrl);
      setDocumentUrl(null);
    }
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50" onClick={handleClose}></div>
        
        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <DocumentArrowDownIcon className="h-6 w-6 text-blue-600" />
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  {document?.filename}
                </h3>
                <p className="text-sm text-gray-500">
                  {document?.incident_code} - {document?.type?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleDownload}
                disabled={!documentUrl}
                className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                Descargar
              </button>
              
              <button
                onClick={handleClose}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-auto">
            {loading && (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <ArrowPathIcon className="h-8 w-8 text-blue-600 animate-spin mx-auto mb-4" />
                  <p className="text-gray-600">Cargando documento...</p>
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar el documento</h3>
                  <p className="text-gray-600 mb-4">{error}</p>
                  <button
                    onClick={loadDocument}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 mx-auto"
                  >
                    <ArrowPathIcon className="h-4 w-4 mr-2" />
                    Reintentar
                  </button>
                </div>
              </div>
            )}

            {documentUrl && !loading && !error && (
              <div className="w-full h-full">
                <iframe
                  src={documentUrl}
                  className="w-full h-full min-h-[500px] border border-gray-200 rounded-lg"
                  title={document?.filename}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
