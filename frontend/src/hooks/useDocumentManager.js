import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

/**
 * Hook personalizado para gestión completa de documentos
 * Maneja subida, descarga, visualización y eliminación de documentos
 */
export const useDocumentManager = () => {
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  // Obtener documentos por tipo e incidencia
  const getDocumentsByIncident = useCallback((incidentId, documentType) => {
    if (documentType === 'incident_attachments') {
      return api.get(`/documents/incident-attachments/${incidentId}/`);
    } else if (['supplier_report', 'quality_report', 'lab_report'].includes(documentType)) {
      return api.get(`/documents/report-attachments/${incidentId}/${documentType}/`);
    }
    return api.get(`/documents/attachments/${documentType}/${incidentId}/`);
  }, []);

  // Subir documento adjunto
  const uploadDocument = useMutation({
    mutationFn: async ({ file, incidentId, documentType, description = '', isPublic = false }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', description);
      formData.append('is_public', isPublic);

      let endpoint;
      if (documentType === 'incident_attachments') {
        endpoint = `/documents/incident-attachments/${incidentId}/upload/`;
      } else if (['supplier_report', 'quality_report', 'lab_report'].includes(documentType)) {
        endpoint = `/documents/report-attachments/${incidentId}/${documentType}/upload/`;
      } else {
        formData.append('incident_id', incidentId);
        formData.append('document_type', documentType);
        endpoint = '/documents/attachments/upload/';
      }

      const response = await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries(['documents', variables.incidentId]);
      queryClient.invalidateQueries(['attachments', variables.incidentId]);
      setUploadProgress(0);
      setIsUploading(false);
    },
    onError: (error) => {
      console.error('Error uploading document:', error);
      setUploadProgress(0);
      setIsUploading(false);
    },
  });

  // Eliminar documento
  const deleteDocument = useMutation({
    mutationFn: async ({ incidentId, documentType, attachmentId }) => {
      if (documentType === 'incident_attachments') {
        return api.delete(`/documents/incident-attachments/${incidentId}/${attachmentId}/delete/`);
      } else if (['supplier_report', 'quality_report', 'lab_report'].includes(documentType)) {
        return api.delete(`/documents/report-attachments/${incidentId}/${documentType}/${attachmentId}/delete/`);
      }
      return api.delete(`/documents/attachments/${documentType}/${incidentId}/${attachmentId}/delete/`);
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['documents', variables.incidentId]);
      queryClient.invalidateQueries(['attachments', variables.incidentId]);
      queryClient.invalidateQueries(['incident-attachments', variables.incidentId]);
    },
  });

  // Descargar documento
  const downloadDocument = useCallback(async (incidentId, documentType, attachmentId) => {
    try {
      let endpoint;
      if (documentType === 'incident_attachments') {
        endpoint = `/documents/incident-attachments/${incidentId}/${attachmentId}/download/`;
      } else if (['supplier_report', 'quality_report', 'lab_report'].includes(documentType)) {
        endpoint = `/documents/report-attachments/${incidentId}/${documentType}/${attachmentId}/download/`;
      } else {
        endpoint = `/documents/attachments/${documentType}/${incidentId}/${attachmentId}/download/`;
      }
      
      const response = await api.get(endpoint, { responseType: 'blob' });
      
      // Crear URL del blob y descargar
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = attachmentId; // Usar el ID como nombre temporal
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading document:', error);
      throw error;
    }
  }, []);

  // Abrir documento en navegador
  const openDocument = useCallback(async (incidentId, documentType, attachmentId) => {
    let url;
    const { API_ORIGIN } = await import('../services/api');
    if (documentType === 'incident_attachments') {
      url = `${API_ORIGIN}/api/documents/incident-attachments/${incidentId}/${attachmentId}/view/`;
    } else if (['supplier_report', 'quality_report', 'lab_report'].includes(documentType)) {
      url = `${API_ORIGIN}/api/documents/report-attachments/${incidentId}/${documentType}/${attachmentId}/view/`;
    } else {
      url = `${API_ORIGIN}/api/documents/attachments/${documentType}/${incidentId}/${attachmentId}/view/`;
    }
    window.open(url, '_blank');
  }, []);

  // Obtener información del documento
  const getDocumentInfo = useCallback(async (incidentId, documentType, attachmentId) => {
    try {
      let endpoint;
      if (documentType === 'incident_attachments') {
        endpoint = `/documents/incident-attachments/${incidentId}/${attachmentId}/info/`;
      } else if (['supplier_report', 'quality_report', 'lab_report'].includes(documentType)) {
        endpoint = `/documents/report-attachments/${incidentId}/${documentType}/${attachmentId}/info/`;
      } else {
        endpoint = `/documents/attachments/${documentType}/${incidentId}/${attachmentId}/info/`;
      }
      
      const response = await api.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error getting document info:', error);
      throw error;
    }
  }, []);

  return {
    // Estados
    uploadProgress,
    isUploading,
    
    // Mutaciones
    uploadDocument,
    deleteDocument,
    
    // Funciones
    getDocumentsByIncident,
    downloadDocument,
    openDocument,
    getDocumentInfo,
    
    // Utilidades
    setIsUploading,
  };
};

export default useDocumentManager;
