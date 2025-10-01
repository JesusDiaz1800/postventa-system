import React, { useState } from 'react';
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
  XMarkIcon
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';

const IncidentAttachments = ({ incidentId, incidentCode }) => {
  console.log('=== INCIDENT ATTACHMENTS COMPONENT LOADED ===');
  console.log('Incident ID:', incidentId);
  console.log('Incident Code:', incidentCode);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(null);
  const [uploadDescription, setUploadDescription] = useState('');
  const [isPublic, setIsPublic] = useState(true);
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  // Función para obtener el token de autenticación
  const getAuthToken = () => {
    const authData = localStorage.getItem('postventa_auth');
    if (authData) {
      try {
        const parsed = JSON.parse(authData);
        return parsed.token;
      } catch (error) {
        console.warn('Error parsing auth data:', error);
      }
    }
    return localStorage.getItem('access_token');
  };

  // Función para ver archivo con autenticación
  const handleViewFile = async (attachmentId) => {
    try {
      const token = getAuthToken();
      if (!token) {
        showError('No se encontró token de autenticación');
        return;
      }

      const response = await api.get(`/incidents/${incidentId}/attachments/${attachmentId}/view/`, {
        responseType: 'blob'
      });
      
      // Obtener el tipo MIME del archivo
      const contentType = response.headers['content-type'] || 'application/octet-stream';
      
      // Crear blob con el tipo MIME correcto
      const blob = new Blob([response.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      
      // Abrir en nueva ventana
      const newWindow = window.open(url, '_blank');
      if (!newWindow) {
        showError('No se pudo abrir la ventana. Verifica que los pop-ups estén permitidos.');
      }
    } catch (error) {
      console.error('Error viewing file:', error);
      showError('Error al abrir el archivo');
    }
  };

  // Función para descargar archivo con autenticación
  const handleDownloadFile = async (attachmentId, fileName) => {
    try {
      const token = getAuthToken();
      if (!token) {
        showError('No se encontró token de autenticación');
        return;
      }

      const response = await api.get(`/incidents/${incidentId}/attachments/${attachmentId}/download/`, {
        responseType: 'blob'
      });
      
      // Obtener el tipo MIME del archivo
      const contentType = response.headers['content-type'] || 'application/octet-stream';
      
      // Crear blob con el tipo MIME correcto
      const blob = new Blob([response.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);
      
      // Crear enlace de descarga
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Limpiar URL después de un tiempo
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 1000);
      
    } catch (error) {
      console.error('Error downloading file:', error);
      showError('Error al descargar el archivo');
    }
  };

  // Obtener adjuntos de la incidencia
  const { data: attachments, isLoading, error } = useQuery({
    queryKey: ['incident-attachments', incidentId],
    queryFn: async () => {
      console.log('=== FETCHING INCIDENT ATTACHMENTS ===');
      console.log('Incident ID:', incidentId);
      
      try {
        const response = await api.get(`/incidents/${incidentId}/attachments/`);
        console.log('Response status:', response.status);
        console.log('Response data:', response.data);
        console.log('Attachments array:', response.data.attachments);
        return response.data.attachments || [];
      } catch (error) {
        console.error('Error fetching attachments:', error);
        console.error('Error response:', error.response?.data);
        throw new Error('Error al cargar adjuntos');
      }
    },
    enabled: !!incidentId,
  });

  // Mutación para subir archivo
  const uploadMutation = useMutation({
    mutationFn: async (formData) => {
      try {
        const response = await api.post(`/incidents/${incidentId}/attachments/upload/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        return response.data;
      } catch (error) {
        console.error('Upload error:', error);
        throw new Error(error.response?.data?.error || 'Error al subir archivo');
      }
    },
    onSuccess: (data) => {
      console.log('=== UPLOAD SUCCESS ===');
      console.log('Upload response:', data);
      showSuccess('Archivo subido exitosamente');
      console.log('Invalidating queries for incident:', incidentId);
      queryClient.invalidateQueries(['incident-attachments', incidentId]);
      setShowUploadModal(false);
      setUploadingFile(null);
      setUploadDescription('');
    },
    onError: (error) => {
      showError('Error al subir archivo: ' + error.message);
    },
  });

  // Mutación para eliminar archivo
  const deleteMutation = useMutation({
    mutationFn: async ({ attachmentId }) => {
      try {
        const response = await api.delete(`/incidents/${incidentId}/attachments/${attachmentId}/delete/`);
        return response.data;
      } catch (error) {
        console.error('Delete error:', error);
        throw new Error(error.response?.data?.error || 'Error al eliminar archivo');
      }
    },
    onSuccess: () => {
      showSuccess('Archivo eliminado exitosamente');
      queryClient.invalidateQueries(['incident-attachments', incidentId]);
    },
    onError: (error) => {
      showError('Error al eliminar archivo: ' + error.message);
    },
  });

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validar tamaño (máximo 50MB)
      const maxSize = 50 * 1024 * 1024; // 50MB
      if (file.size > maxSize) {
        showError('El archivo es demasiado grande. Máximo 50MB.');
        return;
      }
      setUploadingFile(file);
    }
  };

  const handleUpload = () => {
    if (!uploadingFile) return;

    const formData = new FormData();
    formData.append('file', uploadingFile);
    formData.append('title', `Documento adjunto - ${uploadingFile.name}`);
    formData.append('description', uploadDescription);
    formData.append('is_public', isPublic);

    uploadMutation.mutate(formData);
  };

  const handleDelete = (attachmentId) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este archivo?')) {
      deleteMutation.mutate({ attachmentId });
    }
  };

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'image':
        return <PhotoIcon className="h-5 w-5 text-green-600" />;
      case 'video':
        return <VideoCameraIcon className="h-5 w-5 text-blue-600" />;
      case 'audio':
        return <SpeakerWaveIcon className="h-5 w-5 text-purple-600" />;
      case 'document':
        return <DocumentIcon className="h-5 w-5 text-gray-600" />;
      default:
        return <PaperClipIcon className="h-5 w-5 text-gray-600" />;
    }
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
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4">
        <p className="text-red-600">Error al cargar adjuntos: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Adjuntos</h3>
        <button
          onClick={() => setShowUploadModal(true)}
          className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Subir Archivo
        </button>
      </div>

      {/* Lista de adjuntos */}
      {attachments && attachments.length > 0 ? (
        <div className="space-y-2">
          {attachments.map((attachment) => (
            <div
              key={attachment.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex items-center space-x-3">
                {getFileIcon(attachment.file_type || 'document')}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {attachment.file_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {attachment.file_size ? `${(attachment.file_size / 1024 / 1024).toFixed(2)} MB` : 'Tamaño desconocido'} • 
                    {new Date(attachment.uploaded_at).toLocaleDateString()}
                    {attachment.is_public && ' • Público'}
                  </p>
                  {attachment.description && (
                    <p className="text-xs text-gray-400 truncate">
                      {attachment.description}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleViewFile(attachment.id)}
                  className="p-1 text-blue-600 hover:text-blue-900"
                  title="Ver archivo"
                >
                  <EyeIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDownloadFile(attachment.id, attachment.file_name)}
                  className="p-1 text-green-600 hover:text-green-900"
                  title="Descargar archivo"
                >
                  <ArrowDownTrayIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(attachment.id)}
                  className="p-1 text-red-600 hover:text-red-900"
                  title="Eliminar archivo"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <PaperClipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-sm text-gray-500">No hay archivos adjuntos</p>
        </div>
      )}

      {/* Modal de subida */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Subir Archivo</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Seleccionar Archivo
                </label>
                <input
                  type="file"
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
                {uploadingFile && (
                  <p className="mt-2 text-sm text-gray-600">
                    Archivo seleccionado: {uploadingFile.name} ({(uploadingFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Descripción (opcional)
                </label>
                <textarea
                  value={uploadDescription}
                  onChange={(e) => setUploadDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe el contenido del archivo..."
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_public" className="ml-2 block text-sm text-gray-900">
                  Archivo público (visible para todos los usuarios)
                </label>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleUpload}
                disabled={!uploadingFile || uploadMutation.isPending}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploadMutation.isPending ? 'Subiendo...' : 'Subir Archivo'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentAttachments;
