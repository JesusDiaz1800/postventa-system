import React, { useState, useCallback } from 'react';
import {
  EyeIcon,
  DocumentArrowDownIcon,
  XMarkIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

/**
 * Componente unificado para visualización de documentos
 * Maneja la apertura de documentos en el navegador de manera profesional
 */
const DocumentViewerUnified = ({ 
  documentType, 
  incidentId, 
  filename, 
  title = "Documento",
  onClose,
  className = ""
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Manejar apertura de documento
  const handleOpenDocument = useCallback(async () => {
    if (!filename || !incidentId || !documentType) {
      setError('Información del documento incompleta');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Codificar el nombre del archivo para manejar caracteres especiales
      const encodedFilename = encodeURIComponent(filename);
      
      // Construir URL del documento
      const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}/api/documents/open/${documentType}/${incidentId}/${encodedFilename}`;
      
      // Abrir documento en nueva pestaña
      const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
      
      if (!newWindow) {
        throw new Error('No se pudo abrir la ventana. Verifica que los pop-ups estén permitidos.');
      }
      
      // Verificar si la ventana se cerró inmediatamente (indicando error)
      setTimeout(() => {
        if (newWindow.closed) {
          setError('Error al abrir el documento. Verifica que el archivo existe y es accesible.');
        }
      }, 1000);
      
    } catch (error) {
      console.error('Error opening document:', error);
      setError(`Error al abrir el documento: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [documentType, incidentId, filename]);

  // Manejar descarga de documento
  const handleDownloadDocument = useCallback(async () => {
    if (!filename || !incidentId || !documentType) {
      setError('Información del documento incompleta');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const encodedFilename = encodeURIComponent(filename);
      const { API_ORIGIN } = await import('../services/api');
      const url = `${API_ORIGIN}/api/documents/open/${documentType}/${incidentId}/${encodedFilename}`;
      
      // Crear enlace de descarga
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
    } catch (error) {
      console.error('Error downloading document:', error);
      setError(`Error al descargar el documento: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [documentType, incidentId, filename]);

  return (
    <div className={`bg-white rounded-lg shadow-lg max-w-md w-full mx-4 ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <DocumentTextIcon className="h-6 w-6 text-blue-600 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
              <p className="text-sm text-gray-500 truncate">{filename}</p>
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      {/* Contenido */}
      <div className="px-6 py-4">
        {error ? (
          <div className="text-center py-4">
            <ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-4 text-red-400" />
            <p className="text-red-600 text-sm mb-2">Error al acceder al documento</p>
            <p className="text-gray-500 text-xs">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-3 px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
            >
              Reintentar
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-center">
              <DocumentTextIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-600 text-sm">
                {isLoading ? 'Abriendo documento...' : 'Haz clic en el botón para abrir el documento'}
              </p>
            </div>

            {/* Botones de acción */}
            <div className="flex space-x-3">
              <button
                onClick={handleOpenDocument}
                disabled={isLoading}
                className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Abriendo...
                  </>
                ) : (
                  <>
                    <EyeIcon className="h-4 w-4 mr-2" />
                    Ver Documento
                  </>
                )}
              </button>
              
              <button
                onClick={handleDownloadDocument}
                disabled={isLoading}
                className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                Descargar
              </button>
            </div>

            {/* Información adicional */}
            <div className="text-xs text-gray-500 text-center">
              <p>El documento se abrirá en una nueva pestaña</p>
              <p>Formato soportado: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewerUnified;
