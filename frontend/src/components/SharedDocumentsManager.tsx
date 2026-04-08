import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  DocumentTextIcon, 
  ArrowDownTrayIcon, 
  EyeIcon, 
  TrashIcon,
  FolderIcon,
  DocumentIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';

const SharedDocumentsManager = () => {
  const [selectedType, setSelectedType] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  // Obtener documentos compartidos
  const { data: documents, isLoading, error, refetch } = useQuery({
    queryKey: ['shared-documents', selectedType],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const params = selectedType ? `?type=${selectedType}` : '';
      const response = await fetch(`/api/documents/shared/${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) throw new Error('Error al cargar documentos compartidos');
      return response.json();
    },
  });

  // Mutación para eliminar documento
  const deleteDocumentMutation = useMutation({
    mutationFn: async ({ documentType, filename }) => {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/documents/shared/${documentType}/${filename}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al eliminar documento');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['shared-documents']);
      showSuccess('Documento eliminado exitosamente');
      setShowDeleteModal(false);
      setDocumentToDelete(null);
    },
    onError: (error) => {
      showError('Error al eliminar documento: ' + error.message);
    },
  });

  const handleDelete = (document) => {
    setDocumentToDelete(document);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = () => {
    if (documentToDelete) {
      deleteDocumentMutation.mutate({
        documentType: documentToDelete.type,
        filename: documentToDelete.filename
      });
    }
  };

  const handleDownload = (document) => {
    const token = localStorage.getItem('access_token');
    const url = `/api/documents/shared/${document.type}/${document.filename}/download/`;
    
    // Crear enlace temporal para descarga
    const link = document.createElement('a');
    link.href = url;
    link.download = document.filename;
    link.style.display = 'none';
    
    // Agregar headers de autorización
    fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    .then(response => response.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      link.href = url;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    })
    .catch(error => {
      showError('Error al descargar documento: ' + error.message);
    });
  };

  const handleView = (document) => {
    const token = localStorage.getItem('access_token');
    const url = `/api/documents/shared/${document.type}/${document.filename}/view/`;
    
    // Abrir en nueva ventana
    window.open(url, '_blank');
  };

  const getDocumentTypeIcon = (type) => {
    switch (type) {
      case 'visit_reports':
        return <DocumentTextIcon className="h-5 w-5 text-blue-600" />;
      case 'lab_reports':
        return <DocumentIcon className="h-5 w-5 text-green-600" />;
      case 'supplier_reports':
        return <DocumentArrowDownIcon className="h-5 w-5 text-purple-600" />;
      default:
        return <FolderIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const getDocumentTypeName = (type) => {
    switch (type) {
      case 'visit_reports':
        return 'Reportes de Visita';
      case 'lab_reports':
        return 'Informes de Laboratorio';
      case 'supplier_reports':
        return 'Informes para Proveedores';
      default:
        return type;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error al cargar documentos</h3>
        <p className="text-gray-600">{error.message}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con filtros */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Documentos Compartidos</h3>
          <p className="text-sm text-gray-500">Gestión de documentos generados en la carpeta compartida</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos los tipos</option>
            <option value="visit_reports">Reportes de Visita</option>
            <option value="lab_reports">Informes de Laboratorio</option>
            <option value="supplier_reports">Informes para Proveedores</option>
          </select>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Actualizar
          </button>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-blue-900">Reportes de Visita</p>
              <p className="text-2xl font-bold text-blue-600">
                {documents?.documents?.filter(d => d.type === 'visit_reports').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <DocumentIcon className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-green-900">Informes de Laboratorio</p>
              <p className="text-2xl font-bold text-green-600">
                {documents?.documents?.filter(d => d.type === 'lab_reports').length || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center">
            <DocumentArrowDownIcon className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-purple-900">Informes para Proveedores</p>
              <p className="text-2xl font-bold text-purple-600">
                {documents?.documents?.filter(d => d.type === 'supplier_reports').length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de documentos */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {documents?.documents?.map((document) => (
            <li key={`${document.type}-${document.filename}`}>
              <div className="px-4 py-4 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    {getDocumentTypeIcon(document.type)}
                  </div>
                  <div className="ml-4">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {document.filename}
                      </p>
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {getDocumentTypeName(document.type)}
                      </span>
                    </div>
                    <div className="mt-1 text-sm text-gray-500">
                      <p>Tamaño: {formatFileSize(document.size)}</p>
                      <p>Modificado: {formatDate(document.modified)}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleView(document)}
                    className="text-blue-600 hover:text-blue-900"
                    title="Ver documento"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDownload(document)}
                    className="text-green-600 hover:text-green-900"
                    title="Descargar documento"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(document)}
                    className="text-red-600 hover:text-red-900"
                    title="Eliminar documento"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Modal de Confirmación de Eliminación */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <TrashIcon className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mt-4">
                ¿Eliminar documento?
              </h3>
              <div className="mt-2">
                <p className="text-sm text-gray-500">
                  ¿Estás seguro de que deseas eliminar el documento {documentToDelete?.filename}? 
                  Esta acción no se puede deshacer.
                </p>
              </div>
              <div className="flex justify-center space-x-3 mt-4">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setDocumentToDelete(null);
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  disabled={deleteDocumentMutation.isPending}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
                >
                  {deleteDocumentMutation.isPending ? 'Eliminando...' : 'Eliminar'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SharedDocumentsManager;
