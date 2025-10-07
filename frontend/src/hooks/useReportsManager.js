import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

/**
 * Hook personalizado para gestión completa de reportes
 * Maneja creación, edición, escalamiento y cierre de reportes
 */
export const useReportsManager = () => {
  const queryClient = useQueryClient();
  const [isGenerating, setIsGenerating] = useState(false);

  // Obtener reportes por tipo
  const getReportsByType = useCallback((reportType, incidentId = null) => {
    const endpoint = incidentId 
      ? `/documents/${reportType}/?incident_id=${incidentId}`
      : `/documents/${reportType}/`;
    return api.get(endpoint);
  }, []);

  // Crear reporte de calidad interna
  const createInternalQualityReport = useMutation({
    mutationFn: async ({ incidentId, reportData, attachments = [] }) => {
      const formData = new FormData();
      formData.append('incident_id', incidentId);
      formData.append('report_data', JSON.stringify(reportData));
      
      attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });

      const response = await api.post('/documents/quality-reports/internal/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['quality-reports']);
      queryClient.invalidateQueries(['incidents']);
    },
  });

  // Crear reporte de proveedor
  const createSupplierReport = useMutation({
    mutationFn: async ({ incidentId, reportData, supplierResponse = null, attachments = [] }) => {
      const formData = new FormData();
      formData.append('incident_id', incidentId);
      formData.append('report_data', JSON.stringify(reportData));
      
      if (supplierResponse) {
        formData.append('supplier_response', JSON.stringify(supplierResponse));
      }
      
      attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });

      const response = await api.post('/documents/supplier-reports/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['supplier-reports']);
      queryClient.invalidateQueries(['incidents']);
    },
  });

  // Escalar reporte interno
  const escalateInternalReport = useMutation({
    mutationFn: async ({ reportId, escalationData }) => {
      const response = await api.post(`/documents/quality-reports/${reportId}/escalate/`, escalationData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['quality-reports']);
    },
  });

  // Adjuntar respuesta del proveedor
  const attachSupplierResponse = useMutation({
    mutationFn: async ({ reportId, responseData, attachments = [] }) => {
      const formData = new FormData();
      formData.append('response_data', JSON.stringify(responseData));
      
      attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });

      const response = await api.post(`/documents/supplier-reports/${reportId}/attach-response/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['supplier-reports']);
    },
  });

  // Cerrar incidencia con resolución
  const closeIncident = useMutation({
    mutationFn: async ({ incidentId, resolutionData, finalActions, attachments = [] }) => {
      const formData = new FormData();
      formData.append('resolution_data', JSON.stringify(resolutionData));
      formData.append('final_actions', JSON.stringify(finalActions));
      
      attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });

      const response = await api.post(`/incidents/${incidentId}/close/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['incidents']);
      queryClient.invalidateQueries(['documents']);
    },
  });

  // Generar reporte automático
  const generateReport = useCallback(async (reportType, incidentId, templateData = {}) => {
    setIsGenerating(true);
    try {
      const response = await api.post(`/documents/generate/${reportType}/${incidentId}/`, templateData);
      return response.data;
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    } finally {
      setIsGenerating(false);
    }
  }, []);

  // Obtener plantillas de reportes
  const getReportTemplates = useCallback(async (reportType) => {
    const response = await api.get(`/documents/templates/?type=${reportType}`);
    return response.data;
  }, []);

  return {
    // Estados
    isGenerating,
    
    // Mutaciones
    createInternalQualityReport,
    createSupplierReport,
    escalateInternalReport,
    attachSupplierResponse,
    closeIncident,
    
    // Funciones
    getReportsByType,
    generateReport,
    getReportTemplates,
  };
};

export default useReportsManager;
