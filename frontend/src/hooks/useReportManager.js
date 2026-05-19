import { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';

/**
 * Hook optimizado para gestión de reportes
 * Maneja creación, actualización, escalamiento y cierre de reportes
 */
export const useReportManager = () => {
  const queryClient = useQueryClient();
  const [selectedReport, setSelectedReport] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showResponseModal, setShowResponseModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [showClosureModal, setShowClosureModal] = useState(false);

  // Obtener reportes por tipo
  const getReportsByType = useCallback((reportType) => {
    return useQuery({
      queryKey: [`${reportType}-reports`],
      queryFn: async () => {
        const response = await api.get(`/documents/${reportType}/`);
        return response.data || [];
      },
    });
  }, []);

  // Crear reporte
  const createReport = useMutation({
    mutationFn: async ({ reportType, reportData }) => {
      const response = await api.post(`/documents/${reportType}/`, reportData);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries([`${variables.reportType}-reports`]);
      queryClient.invalidateQueries(['incidents']);
    },
  });

  // Actualizar reporte
  const updateReport = useMutation({
    mutationFn: async ({ reportType, reportId, reportData }) => {
      const response = await api.patch(`/documents/${reportType}/${reportId}/`, reportData);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries([`${variables.reportType}-reports`]);
      queryClient.invalidateQueries(['incidents']);
    },
  });

  // Eliminar reporte
  const deleteReport = useMutation({
    mutationFn: async ({ reportType, reportId }) => {
      const response = await api.delete(`/documents/${reportType}/${reportId}/`);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries([`${variables.reportType}-reports`]);
      queryClient.invalidateQueries(['incidents']);
    },
  });

  // Escalar reporte
  const escalateReport = useMutation({
    mutationFn: async ({ reportType, reportId, escalationData }) => {
      const response = await api.post(`/documents/${reportType}/${reportId}/escalate/`, escalationData);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries([`${variables.reportType}-reports`]);
      queryClient.invalidateQueries(['incidents']);
    },
  });

  // Cerrar reporte
  const closeReport = useMutation({
    mutationFn: async ({ reportType, reportId, closureData }) => {
      const response = await api.post(`/documents/${reportType}/${reportId}/close/`, closureData);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries([`${variables.reportType}-reports`]);
      queryClient.invalidateQueries(['incidents']);
    },
  });

  // Generar documento del reporte
  const generateReportDocument = useMutation({
    mutationFn: async ({ reportType, reportId }) => {
      const response = await api.post(`/documents/generate/${reportType}/${reportId}/`);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries([`${variables.reportType}-reports`]);
    },
  });

  // Obtener estadísticas de reportes
  const getReportStatistics = useCallback((reportType) => {
    return useQuery({
      queryKey: [`${reportType}-statistics`],
      queryFn: async () => {
        const response = await api.get(`/documents/${reportType}/statistics/`);
        return response.data;
      },
    });
  }, []);

  // Manejar selección de reporte
  const handleSelectReport = useCallback((report) => {
    setSelectedReport(report);
  }, []);

  // Manejar creación de reporte
  const handleCreateReport = useCallback(async (reportData) => {
    try {
      await createReport.mutateAsync(reportData);
      setShowCreateModal(false);
      return true;
    } catch (error) {
      console.error('Error creating report:', error);
      return false;
    }
  }, [createReport]);

  // Manejar actualización de reporte
  const handleUpdateReport = useCallback(async (reportId, reportData) => {
    try {
      await updateReport.mutateAsync({
        reportType: selectedReport?.type,
        reportId,
        reportData,
      });
      return true;
    } catch (error) {
      console.error('Error updating report:', error);
      return false;
    }
  }, [updateReport, selectedReport]);

  // Manejar eliminación de reporte
  const handleDeleteReport = useCallback(async (reportId) => {
    try {
      await deleteReport.mutateAsync({
        reportType: selectedReport?.type,
        reportId,
      });
      setSelectedReport(null);
      return true;
    } catch (error) {
      console.error('Error deleting report:', error);
      return false;
    }
  }, [deleteReport, selectedReport]);

  // Manejar escalamiento de reporte
  const handleEscalateReport = useCallback(async (escalationData) => {
    try {
      await escalateReport.mutateAsync({
        reportType: selectedReport?.type,
        reportId: selectedReport?.id,
        escalationData,
      });
      setShowEscalateModal(false);
      return true;
    } catch (error) {
      console.error('Error escalating report:', error);
      return false;
    }
  }, [escalateReport, selectedReport]);

  // Manejar cierre de reporte
  const handleCloseReport = useCallback(async (closureData) => {
    try {
      await closeReport.mutateAsync({
        reportType: selectedReport?.type,
        reportId: selectedReport?.id,
        closureData,
      });
      setShowClosureModal(false);
      setSelectedReport(null);
      return true;
    } catch (error) {
      console.error('Error closing report:', error);
      return false;
    }
  }, [closeReport, selectedReport]);

  // Manejar generación de documento
  const handleGenerateDocument = useCallback(async () => {
    try {
      await generateReportDocument.mutateAsync({
        reportType: selectedReport?.type,
        reportId: selectedReport?.id,
      });
      return true;
    } catch (error) {
      console.error('Error generating document:', error);
      return false;
    }
  }, [generateReportDocument, selectedReport]);

  // Utilidades para filtrado y búsqueda
  const filterReports = useCallback((reports, filters) => {
    let filtered = Array.isArray(reports) ? reports : [];
    
    // Filtrar por término de búsqueda
    if (filters.searchTerm) {
      filtered = filtered.filter(report =>
        report.title?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        report.description?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        report.incident_code?.toLowerCase().includes(filters.searchTerm.toLowerCase())
      );
    }
    
    // Filtrar por estado
    if (filters.status && filters.status !== 'all') {
      filtered = filtered.filter(report => report.status === filters.status);
    }
    
    // Filtrar por fecha
    if (filters.dateFrom) {
      filtered = filtered.filter(report => 
        new Date(report.created_at) >= new Date(filters.dateFrom)
      );
    }
    
    if (filters.dateTo) {
      filtered = filtered.filter(report => 
        new Date(report.created_at) <= new Date(filters.dateTo)
      );
    }
    
    // Ordenar
    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'status':
          return (a.status || '').localeCompare(b.status || '');
        case 'date':
        default:
          return new Date(b.created_at || 0) - new Date(a.created_at || 0);
      }
    });
    
    return filtered;
  }, []);

  // Obtener estadísticas de reportes
  const getReportStats = useCallback((reports) => {
    const stats = {
      total: reports.length,
      pending: 0,
      inProgress: 0,
      completed: 0,
      overdue: 0,
    };
    
    reports.forEach(report => {
      switch (report.status) {
        case 'pending':
          stats.pending++;
          break;
        case 'in_progress':
          stats.inProgress++;
          break;
        case 'completed':
          stats.completed++;
          break;
        case 'overdue':
          stats.overdue++;
          break;
      }
    });
    
    return stats;
  }, []);

  return {
    // Estados
    selectedReport,
    showCreateModal,
    showResponseModal,
    showEscalateModal,
    showClosureModal,
    
    // Setters
    setSelectedReport,
    setShowCreateModal,
    setShowResponseModal,
    setShowEscalateModal,
    setShowClosureModal,
    
    // Queries
    getReportsByType,
    getReportStatistics,
    
    // Mutations
    createReport,
    updateReport,
    deleteReport,
    escalateReport,
    closeReport,
    generateReportDocument,
    
    // Handlers
    handleSelectReport,
    handleCreateReport,
    handleUpdateReport,
    handleDeleteReport,
    handleEscalateReport,
    handleCloseReport,
    handleGenerateDocument,
    
    // Utilidades
    filterReports,
    getReportStats,
  };
};

export default useReportManager;
