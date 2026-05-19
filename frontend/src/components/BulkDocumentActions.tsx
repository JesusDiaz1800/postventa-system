import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import {
  TrashIcon,
  DocumentArrowDownIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const BulkDocumentActions = ({ 
  selectedDocuments, 
  documents, 
  onClearSelection, 
  onSuccess 
}) => {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [showConfirmDownload, setShowConfirmDownload] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  
  const queryClient = useQueryClient();

  // Mutación para eliminar documentos
  const deleteDocumentsMutation = useMutation({
    mutationFn: async (documentsToDelete) => {
      const deletePromises = documentsToDelete.map(doc => 
        api.delete(`/documents/delete/${doc.type}/${doc.incident_id}/${doc.filename}/`)
      );
      return Promise.all(deletePromises);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['shared-documents']);
      queryClient.invalidateQueries(['db-documents']);
      onSuccess('Documentos eliminados exitosamente');
      onClearSelection();
    },
    onError: (error) => {
      console.error('Error eliminando documentos:', error);
      onSuccess('Error al eliminar algunos documentos');
    },
  });

  // Función para descargar documentos seleccionados
  const handleBulkDownload = async () => {
    setActionLoading(true);
    try {
      const selectedDocs = documents.filter(doc => 
        selectedDocuments.includes(doc.id || `${doc.type}-${doc.incident_id}-${doc.filename}`)
      );

      for (const doc of selectedDocs) {
        try {
          const response = await api.get(
            `/documents/open/${doc.type.replace('_', '-')}/${doc.incident_id}/${doc.filename}/`,
            { responseType: 'blob' }
          );
          
          const blob = new Blob([response.data]);
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = doc.filename;
          link.click();
          window.URL.revokeObjectURL(url);
          
          // Pequeña pausa entre descargas
          await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
          console.error(`Error descargando ${doc.filename}:`, error);
        }
      }
      
      onSuccess(`${selectedDocs.length} documentos descargados`);
    } catch (error) {
      console.error('Error en descarga masiva:', error);
      onSuccess('Error al descargar algunos documentos');
    } finally {
      setActionLoading(false);
      setShowConfirmDownload(false);
    }
  };

  // Función para eliminar documentos seleccionados
  const handleBulkDelete = async () => {
    setActionLoading(true);
    try {
      const selectedDocs = documents.filter(doc => 
        selectedDocuments.includes(doc.id || `${doc.type}-${doc.incident_id}-${doc.filename}`)
      );

      await deleteDocumentsMutation.mutateAsync(selectedDocs);
    } catch (error) {
      console.error('Error en eliminación masiva:', error);
    } finally {
      setActionLoading(false);
      setShowConfirmDelete(false);
    }
  };

  if (selectedDocuments.length === 0) return null;

  const selectedDocs = documents.filter(doc => 
    selectedDocuments.includes(doc.id || `${doc.type}-${doc.incident_id}-${doc.filename}`)
  );

  return (
    <>
      {/* Barra de acciones masivas */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <CheckCircleIcon className="h-5 w-5 text-blue-600 mr-2" />
              <span className="text-sm font-medium text-blue-900">
                {selectedDocuments.length} documento(s) seleccionado(s)
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowConfirmDownload(true)}
                disabled={actionLoading}
                className="flex items-center px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                {actionLoading ? 'Descargando...' : 'Descargar Seleccionados'}
              </button>
              
              <button
                onClick={() => setShowConfirmDelete(true)}
                disabled={actionLoading}
                className="flex items-center px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <TrashIcon className="h-4 w-4 mr-2" />
                {actionLoading ? 'Eliminando...' : 'Eliminar Seleccionados'}
              </button>
              
              <button
                onClick={onClearSelection}
                className="flex items-center px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
              >
                <XMarkIcon className="h-4 w-4 mr-2" />
                Deseleccionar
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de confirmación para descarga */}
      {showConfirmDownload && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center p-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setShowConfirmDownload(false)}></div>
            
            <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <DocumentArrowDownIcon className="h-6 w-6 text-green-600 mr-3" />
                  <h3 className="text-lg font-medium text-gray-900">
                    Descargar Documentos
                  </h3>
                </div>
                
                <p className="text-sm text-gray-600 mb-4">
                  Se descargarán {selectedDocuments.length} documentos. 
                  Esto puede tomar unos momentos.
                </p>
                
                <div className="max-h-32 overflow-y-auto mb-4">
                  <ul className="text-sm text-gray-500 space-y-1">
                    {selectedDocs.slice(0, 5).map((doc, index) => (
                      <li key={index} className="truncate">
                        • {doc.filename}
                      </li>
                    ))}
                    {selectedDocs.length > 5 && (
                      <li className="text-gray-400">
                        ... y {selectedDocs.length - 5} más
                      </li>
                    )}
                  </ul>
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowConfirmDownload(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleBulkDownload}
                    disabled={actionLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    {actionLoading ? 'Descargando...' : 'Descargar'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de confirmación para eliminación */}
      {showConfirmDelete && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center p-4">
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => setShowConfirmDelete(false)}></div>
            
            <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mr-3" />
                  <h3 className="text-lg font-medium text-gray-900">
                    Eliminar Documentos
                  </h3>
                </div>
                
                <p className="text-sm text-gray-600 mb-4">
                  <strong>¿Estás seguro de que quieres eliminar {selectedDocuments.length} documentos?</strong>
                  <br />
                  Esta acción no se puede deshacer.
                </p>
                
                <div className="max-h-32 overflow-y-auto mb-4">
                  <ul className="text-sm text-gray-500 space-y-1">
                    {selectedDocs.slice(0, 5).map((doc, index) => (
                      <li key={index} className="truncate">
                        • {doc.filename}
                      </li>
                    ))}
                    {selectedDocs.length > 5 && (
                      <li className="text-gray-400">
                        ... y {selectedDocs.length - 5} más
                      </li>
                    )}
                  </ul>
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowConfirmDelete(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleBulkDelete}
                    disabled={actionLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
                  >
                    {actionLoading ? 'Eliminando...' : 'Eliminar'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BulkDocumentActions;
