<<<<<<< HEAD
import React, { useState, useCallback, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  DocumentTextIcon,
  DocumentIcon,
  EyeIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentArrowDownIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  XMarkIcon,
  PlusIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  DocumentDuplicateIcon,
  ArchiveBoxIcon,
  ChartBarIcon,
  GlobeAltIcon,
  LockClosedIcon,
} from '@heroicons/react/24/outline';
import { useNotifications } from '../hooks/useNotifications';
import { api } from '../services/api';
import DocumentManager from '../components/DocumentManager';
import DocumentViewer from '../components/DocumentViewer';
import IncidentClosureForm from '../components/IncidentClosureForm';

/**
 * Página central de trazabilidad documental
 * Centro de gestión y visualización de todos los documentos del sistema
 */
const Documents = () => {
  const { showSuccess, showError } = useNotifications();
  const queryClient = useQueryClient();

  // Estados principales
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterIncident, setFilterIncident] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [viewMode, setViewMode] = useState('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [showClosureModal, setShowClosureModal] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);

  // Función helper para extraer documentos de diferentes formatos de respuesta
    const extractDocuments = (data, source) => {
    if (!data) return [];
    
    let documents = [];
    if (Array.isArray(data)) {
      documents = data;
    } else if (data.results && Array.isArray(data.results)) {
      documents = data.results;
    } else if (typeof data === 'object') {
      documents = [data];
    }

    // Determinar el tipo de documento basado en la fuente y metadatos
    return documents.map(doc => ({
      ...doc,
      document_type: determineDocumentType(doc, source)
    }));
  };

  const determineDocumentType = (doc, source) => {
    // Por fuente
    if (source === 'visit-reports') return 'Reporte de Visita';
    if (source === 'quality-reports' && doc.report_type === 'internal') return 'Reporte de Calidad Interno';
    if (source === 'quality-reports' && doc.report_type === 'client') return 'Reporte de Calidad para Cliente';
    if (source === 'supplier-reports' && doc.is_response) return 'Respuesta del Proveedor';
    if (source === 'supplier-reports') return 'Reporte para Proveedor';
    
    // Por metadatos
    if (doc.visit_date || doc.technician) return 'Reporte de Visita';
    if (doc.quality_analysis && doc.report_type === 'internal') return 'Reporte de Calidad Interno';
    if (doc.quality_analysis && doc.report_type === 'client') return 'Reporte de Calidad para Cliente';
    if (doc.supplier_feedback || doc.is_supplier_response) return 'Respuesta del Proveedor';
    if (doc.supplier_name && !doc.is_supplier_response) return 'Reporte para Proveedor';
    
    // Por tipo explícito
    return doc.document_type || doc.type || 'Documento General';
  };

  // Obtener todos los documentos de todas las fuentes
  const { 
    data: allDocuments = [], 
    isLoading: documentsLoading, 
    error: documentsError,
    refetch: refetchDocuments 
  } = useQuery({
    queryKey: ['all-documents-complete'],
    queryFn: async () => {
      try {
        // Obtener documentos de todas las fuentes en paralelo
        const [
          documentsResponse,
          visitReportsResponse,
          supplierReportsResponse,
          qualityReportsResponse,
          labReportsResponse,
          sharedDocumentsResponse,
          realFilesResponse
        ] = await Promise.all([
          api.get('/documents/').catch(() => ({ data: [] })),
          api.get('/documents/visit-reports/').catch(() => ({ data: [] })),
          api.get('/documents/supplier-reports/').catch(() => ({ data: [] })),
          api.get('/documents/quality-reports/').catch(() => ({ data: [] })),
          api.get('/documents/lab-reports/').catch(() => ({ data: [] })),
          api.get('/documents/shared/').catch(() => ({ data: [] })),
          api.get('/documents/real-files/').catch(() => ({ data: [] }))
        ]);

        console.log('=== DEBUGGING DOCUMENT QUERIES ===');
        console.log('Documents response:', documentsResponse.data); // Debug
        console.log('Visit reports response:', visitReportsResponse.data); // Debug
        console.log('Supplier reports response:', supplierReportsResponse.data); // Debug
        console.log('Quality reports response:', qualityReportsResponse.data); // Debug
        console.log('Lab reports response:', labReportsResponse.data); // Debug
        console.log('Shared documents response:', sharedDocumentsResponse.data); // Debug
        console.log('Real files response:', realFilesResponse.data); // Debug
        

        // Extraer documentos de cada respuesta
        const documents = extractDocuments(documentsResponse.data, 'Documents');
        const visitReports = extractDocuments(visitReportsResponse.data, 'Visit Reports');
        const supplierReports = extractDocuments(supplierReportsResponse.data, 'Supplier Reports');
        const qualityReports = extractDocuments(qualityReportsResponse.data, 'Quality Reports');
        const labReports = extractDocuments(labReportsResponse.data, 'Lab Reports');
        const sharedDocs = extractDocuments(sharedDocumentsResponse.data, 'Shared Documents');
        const realFiles = extractDocuments(realFilesResponse.data, 'Real Files');

        // Combinar todos los documentos extraídos
        const allDocs = [
          ...documents,
          ...visitReports,
          ...supplierReports,
          ...qualityReports,
          ...labReports,
          ...sharedDocs,
          ...realFiles
        ];

        console.log('=== FINAL EXTRACTION RESULTS ===');
        console.log('Documents extracted:', documents.length);
        console.log('Visit reports extracted:', visitReports.length);
        console.log('Supplier reports extracted:', supplierReports.length);
        console.log('Quality reports extracted:', qualityReports.length);
        console.log('Lab reports extracted:', labReports.length);
        console.log('Shared docs extracted:', sharedDocs.length);
        console.log('Real files extracted:', realFiles.length);
        console.log('Total combined documents:', allDocs.length);
        console.log('All documents combined:', allDocs); // Debug
        return allDocs;
      } catch (error) {
        console.error('Error fetching all documents:', error);
        return [];
      }
    },
  });

  // Obtener incidencias
  const { 
    data: incidents = [], 
    isLoading: incidentsLoading 
  } = useQuery({
    queryKey: ['incidents-for-documents'],
    queryFn: async () => {
      const response = await api.get('/incidents/');
      return response.data || [];
    },
  });

  // Obtener documentos adjuntos de incidencias
  const { 
    data: incidentAttachments = [], 
    isLoading: attachmentsLoading 
  } = useQuery({
    queryKey: ['incident-attachments-all'],
    queryFn: async () => {
      try {
        // Obtener todas las incidencias primero
        const incidentsResponse = await api.get('/incidents/');
        const incidentsData = incidentsResponse.data || {};
        
        // Extraer incidencias del objeto de respuesta
        const incidents = incidentsData.results || incidentsData || [];
        
        // Verificar que incidents sea un array
        if (!Array.isArray(incidents)) {
          console.log('Incidents response is not an array:', incidents);
          return [];
        }
        
        // Obtener adjuntos de cada incidencia
        const allAttachments = [];
        for (const incident of incidents) {
          try {
            const attachmentsResponse = await api.get(`/documents/incident-attachments/${incident.id}/`);
            if (attachmentsResponse.data && Array.isArray(attachmentsResponse.data)) {
              allAttachments.push(...attachmentsResponse.data.map(attachment => ({
                ...attachment,
                document_type: 'incident_attachment',
                incident_id: incident.id,
                incident_code: incident.code
              })));
            }
          } catch (error) {
            console.log(`No attachments for incident ${incident.id}:`, error);
          }
        }
        
        console.log('Incident attachments:', allAttachments); // Debug
        return allAttachments;
      } catch (error) {
        console.error('Error fetching incident attachments:', error);
        return [];
      }
    },
  });

  // Query de respaldo para obtener documentos de manera alternativa
  const { 
    data: alternativeDocuments = [], 
    isLoading: alternativeLoading 
  } = useQuery({
    queryKey: ['alternative-documents'],
    queryFn: async () => {
      try {
        console.log('=== TRYING ALTERNATIVE ENDPOINTS ===');
        
        // Intentar diferentes endpoints alternativos
        const alternativeEndpoints = [
          '/documents/real-files/',
          '/documents/shared/',
          '/documents/statistics/',
          '/documents/dashboard/'
        ];
        
        const results = [];
        for (const endpoint of alternativeEndpoints) {
          try {
            const response = await api.get(endpoint);
            console.log(`✅ ${endpoint} working:`, response.data);
            
            // Usar la misma función de extracción
            const extracted = extractDocuments(response.data, endpoint);
            results.push(...extracted);
          } catch (error) {
            console.log(`❌ ${endpoint} failed:`, error.message);
          }
        }
        
        console.log('Alternative documents found:', results);
        return results;
      } catch (error) {
        console.error('Error fetching alternative documents:', error);
        return [];
      }
    },
  });

  // Combinar todos los documentos incluyendo adjuntos
  const combinedDocuments = useMemo(() => {
    const baseDocs = Array.isArray(allDocuments) ? allDocuments : [];
    const attachments = Array.isArray(incidentAttachments) ? incidentAttachments : [];
    const alternative = Array.isArray(alternativeDocuments) ? alternativeDocuments : [];
    
    const combined = [...baseDocs, ...attachments, ...alternative];
    console.log('=== FINAL COMBINED DOCUMENTS ===');
    console.log('Base documents:', baseDocs.length);
    console.log('Attachments:', attachments.length);
    console.log('Alternative documents:', alternative.length);
    console.log('Total combined:', combined.length);
    console.log('Combined documents with attachments:', combined); // Debug
    return combined;
  }, [allDocuments, incidentAttachments, alternativeDocuments]);

  // Organizar documentos por incidencia y mejorar datos
  const documentsByIncident = useMemo(() => {
    const grouped = {};
    
    combinedDocuments.forEach(doc => {
      // Mejorar datos del documento
      const enhancedDoc = {
        ...doc,
        // Título mejorado
        title: doc.title || doc.name || doc.filename || doc.document_name || 'Documento sin título',
        // Tipo mejorado
        document_type: doc.document_type || doc.type || doc.report_type || 'Documento',
        // Estado mejorado
        status: doc.status || doc.state || 'draft',
        // Tamaño mejorado
        size: doc.size || doc.file_size || doc.fileSize || 0,
        // Fecha mejorada
        created_at: doc.created_at || doc.created_date || doc.date_created || new Date().toISOString(),
        // Usuario mejorado
        created_by: doc.created_by || doc.uploaded_by || doc.user || 'Sistema',
        // Código de incidencia mejorado
        incident_code: doc.incident_code || doc.incident?.code || doc.related_incident?.code || 'Sin Incidencia',
        // ID mejorado
        id: doc.id || doc.document_id || doc.file_id || Math.random().toString(36).substr(2, 9)
      };
      
      // Obtener el código de incidencia del documento
      const incidentCode = enhancedDoc.incident_code;
      
      if (!grouped[incidentCode]) {
        grouped[incidentCode] = {
          incidentCode,
          documents: [],
          count: 0
        };
      }
      
      grouped[incidentCode].documents.push(enhancedDoc);
      grouped[incidentCode].count++;
    });
    
    console.log('Documents organized by incident with enhanced data:', grouped);
    return grouped;
  }, [combinedDocuments]);

  // Calcular estadísticas dinámicamente basándose en los documentos reales
  const documentStats = useMemo(() => {
    if (!Array.isArray(combinedDocuments)) return {};
    
    const stats = {
      total_documents: combinedDocuments.length,
      visit_reports: combinedDocuments.filter(doc => doc.document_type === 'visit_report' || doc.type === 'visit_report').length,
      supplier_reports: combinedDocuments.filter(doc => doc.document_type === 'supplier_report' || doc.type === 'supplier_report').length,
      quality_reports: combinedDocuments.filter(doc => doc.document_type === 'quality_report' || doc.type === 'quality_report').length,
      lab_reports: combinedDocuments.filter(doc => doc.document_type === 'lab_report' || doc.type === 'lab_report').length,
      incident_attachments: combinedDocuments.filter(doc => doc.document_type === 'incident_attachment' || doc.type === 'incident_attachment').length
    };
    
    console.log('Calculated document stats:', stats); // Debug
    return stats;
  }, [combinedDocuments]);

  // Filtrar y ordenar documentos
  const filteredDocuments = useMemo(() => {
    let filtered = Array.isArray(combinedDocuments) ? combinedDocuments : [];

    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.incident_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.filename?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtrar por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(doc => doc.document_type === filterType);
    }

    // Filtrar por estado
    if (filterStatus !== 'all') {
      filtered = filtered.filter(doc => doc.status === filterStatus);
    }

    // Filtrar por incidencia
    if (filterIncident !== 'all') {
      filtered = filtered.filter(doc => doc.incident_id === parseInt(filterIncident));
    }

    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'type':
          return (a.document_type || '').localeCompare(b.document_type || '');
        case 'incident':
          return (a.incident_code || '').localeCompare(b.incident_code || '');
        case 'size':
          return (b.size || 0) - (a.size || 0);
        case 'date':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

    return filtered;
  }, [combinedDocuments, searchTerm, filterType, filterStatus, filterIncident, sortBy]);

  // Mutación para eliminar documento
  const deleteDocumentMutation = useMutation({
    mutationFn: async (documentId) => {
      return api.delete(`/documents/${documentId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['all-documents']);
      showSuccess('Documento eliminado exitosamente');
    },
    onError: (error) => {
      console.error('Error deleting document:', error);
      showError('Error al eliminar el documento');
    },
  });

  // Manejar visualización de documento
  const handleViewDocument = useCallback((document) => {
    try {
      console.log('Opening document:', document);
      
      // Obtener información del documento
      const documentId = document.id || document.document_id;
      const documentType = document.document_type || document.type || 'document';
      const incidentId = document.incident_id || document.incident?.id;
      const filename = document.filename || document.title || 'document';
      
      // Construir rutas posibles del archivo en el sistema de archivos
      const basePath = 'C:/Users/Jesus Diaz/postventa-system/backend/documents';
      const possiblePaths = [];
      
      // Mapear tipo de documento a carpetas del sistema de archivos
      let folderName = '';
      if (documentType === 'Reporte de Visita' || documentType === 'visit_report' || documentType === 'visit-reports') {
        folderName = 'visit_reports';
      } else if (documentType === 'Reporte de Calidad' || documentType === 'quality_report' || documentType === 'quality-reports') {
        folderName = 'quality_reports';
      } else if (documentType === 'Reporte de Proveedor' || documentType === 'supplier_report' || documentType === 'supplier-reports') {
        folderName = 'supplier_reports';
      } else if (documentType === 'Reporte de Laboratorio' || documentType === 'lab_report' || documentType === 'lab-reports') {
        folderName = 'lab_reports';
      } else if (documentType === 'Adjunto de Incidencia' || documentType === 'incident_attachment' || documentType === 'incident-attachments') {
        folderName = 'incident_attachments';
      } else {
        folderName = 'shared';
      }
      
      // Generar rutas posibles
      if (incidentId) {
        possiblePaths.push(
          `${basePath}/${folderName}/incident_${incidentId}/${filename}`,
          `${basePath}/${folderName}/incident_${incidentId}/${folderName}_${incidentId}_${filename}`,
          `${basePath}/${folderName}/incident_${incidentId}/${folderName}_${incidentId}_*_${filename}`
        );
      }
      
      possiblePaths.push(
        `${basePath}/${folderName}/${filename}`,
        `${basePath}/real_files/${filename}`,
        `${basePath}/shared/${filename}`
      );
      
      console.log('Possible file paths:', possiblePaths);
      
      // Intentar abrir el archivo con diferentes rutas
      for (const filePath of possiblePaths) {
        try {
          // Convertir ruta a URL de archivo
          const fileUrl = `file:///${filePath.replace(/\\/g, '/')}`;
          console.log('Trying file path:', fileUrl);
          
          // Usar window.open directamente para evitar problemas con document.createElement
          window.open(fileUrl, '_blank');
          
          console.log('File opened successfully from:', filePath);
          return;
        } catch (fileError) {
          console.log('Path failed, trying next:', fileError);
        }
      }
      
      // Si no se puede abrir directamente, mostrar información del archivo
      console.log('Document info for manual opening:');
      console.log('- Type:', documentType);
      console.log('- Folder:', folderName);
      console.log('- Filename:', filename);
      console.log('- Incident ID:', incidentId);
      console.log('- Base path:', basePath);
      console.log('- Possible paths:', possiblePaths);
      
      // Mostrar mensaje con información para abrir manualmente
      showError(`No se pudo abrir automáticamente. Busque el archivo en: ${basePath}/${folderName}/`);
    } catch (error) {
      console.error('Error opening document:', error);
      showError('Error al abrir el documento');
    }
  }, [showError]);

  // Manejar descarga de documento
  const handleDownloadDocument = useCallback(async (document) => {
    try {
      const response = await api.get(`/documents/${document.id}/download/`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = document.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      } catch (error) {
      console.error('Error downloading document:', error);
      showError('Error al descargar el documento');
    }
  }, [showError]);

  // Manejar eliminación de documento
  const handleDeleteDocument = useCallback((document) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este documento?')) {
      deleteDocumentMutation.mutate(document.id);
    }
  }, [deleteDocumentMutation]);

  // Manejar selección de documentos
  const handleDocumentSelection = useCallback((documentId, isSelected) => {
    setSelectedDocuments(prev => 
      isSelected 
        ? [...prev, documentId]
        : prev.filter(id => id !== documentId)
    );
  }, []);

  // Seleccionar todos los documentos
  const handleSelectAll = useCallback(() => {
    setSelectedDocuments(filteredDocuments.map(doc => doc.id));
  }, [filteredDocuments]);

  // Limpiar selección
  const handleClearSelection = useCallback(() => {
    setSelectedDocuments([]);
  }, []);

  // Acciones en lote
  const handleBulkDownload = useCallback(async () => {
    for (const documentId of selectedDocuments) {
      const document = combinedDocuments.find(d => d.id === documentId);
      if (document) {
        await handleDownloadDocument(document);
        // Pequeña pausa entre descargas
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
    setSelectedDocuments([]);
    setShowBulkActions(false);
  }, [selectedDocuments, combinedDocuments, handleDownloadDocument]);

  const handleBulkDelete = useCallback(() => {
    if (window.confirm(`¿Estás seguro de que quieres eliminar ${selectedDocuments.length} documentos?`)) {
      selectedDocuments.forEach(documentId => {
        deleteDocumentMutation.mutate(documentId);
      });
      setSelectedDocuments([]);
      setShowBulkActions(false);
    }
  }, [selectedDocuments, deleteDocumentMutation]);

  // Formatear fecha
  const formatDate = useCallback((dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

  // Formatear tamaño de archivo
  const formatFileSize = useCallback((bytes) => {
    if (!bytes || bytes === 0 || isNaN(bytes)) return 'Tamaño no disponible';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }, []);

  // Obtener icono según tipo de documento
  const getDocumentIcon = useCallback((documentType) => {
    switch (documentType) {
      case 'visit_report':
        return '📋';
      case 'supplier_report':
        return '🏢';
      case 'lab_report':
        return '🧪';
      case 'quality_report':
        return '✅';
      case 'incident_attachment':
        return '📎';
      default:
        return '📄';
    }
  }, []);

  // Obtener información mejorada del documento
  const getDocumentInfo = useCallback((document) => {
    console.log('Processing document for info:', document);
    
    // Identificar el tipo de documento de manera más precisa
    let documentType = document.document_type || document.type || document.report_type || 'Documento';
    
    // Detectar tipo basado en la URL o ruta del archivo
    const filename = document.filename || document.title || document.name || '';
    const filePath = document.file_path || document.path || '';
    
    // Detectar tipo basado en el nombre del archivo o ruta
    if (filename.includes('visit_report') || filename.includes('reporte_visita') || 
        filePath.includes('visit_reports') || documentType === 'visit_report' || 
        documentType === 'visit-reports' || documentType === 'reporte_visita') {
      documentType = 'Reporte de Visita';
    } else if (filename.includes('quality_report') || filename.includes('reporte_calidad') || 
               filePath.includes('quality_reports') || documentType === 'quality_report' || 
               documentType === 'quality-reports' || documentType === 'reporte_calidad') {
      documentType = 'Reporte de Calidad';
    } else if (filename.includes('supplier_report') || filename.includes('reporte_proveedor') || 
               filePath.includes('supplier_reports') || documentType === 'supplier_report' || 
               documentType === 'supplier-reports' || documentType === 'reporte_proveedor') {
      documentType = 'Reporte de Proveedor';
    } else if (filename.includes('lab_report') || filename.includes('reporte_laboratorio') || 
               filePath.includes('lab_reports') || documentType === 'lab_report' || 
               documentType === 'lab-reports' || documentType === 'reporte_laboratorio') {
      documentType = 'Reporte de Laboratorio';
    } else if (filename.includes('attachment') || filename.includes('adjunto') || 
               filePath.includes('incident_attachments') || documentType === 'incident_attachment' || 
               documentType === 'incident-attachments' || documentType === 'adjunto_incidencia') {
      documentType = 'Adjunto de Incidencia';
    }
    
    // Extraer nombre de archivo más inteligente
    let title = document.title || document.name || document.filename || document.document_name || 'Documento sin título';
    
    // Si el título es genérico, intentar extraer del filename
    if (title === 'Documento sin título' && filename) {
      title = filename;
    }
    
    // Si aún es genérico, intentar extraer del path
    if (title === 'Documento sin título' && filePath) {
      const pathParts = filePath.split('/');
      title = pathParts[pathParts.length - 1] || 'Documento sin título';
    }
    
    const result = {
      title: title,
      type: documentType,
      status: document.status || document.state || 'draft',
      size: document.size || document.file_size || document.fileSize || 0,
      date: document.created_at || document.created_date || document.date_created || new Date().toISOString(),
      user: document.created_by || document.uploaded_by || document.user || 'Sistema',
      incident: document.incident_code || document.incident?.code || document.related_incident?.code || 'Sin Incidencia',
      id: document.id || document.document_id || document.file_id || Math.random().toString(36).substr(2, 9),
      filename: filename,
      filePath: filePath
    };
    
    console.log('Document info result:', result);
    return result;
  }, []);

  // Obtener color del estado
  const getStatusColor = useCallback((status) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Mejorado */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 mb-8 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="bg-white/20 backdrop-blur-sm rounded-xl p-3 mr-4">
                  <DocumentTextIcon className="h-8 w-8 text-white" />
                </div>
              <div>
                  <h1 className="text-3xl font-bold text-white">
                    Centro de Trazabilidad Documental
                </h1>
                  <p className="text-blue-100 text-lg mt-1">
                    Gestión centralizada de todos los documentos del sistema
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`inline-flex items-center px-6 py-3 text-sm font-semibold rounded-xl transition-all duration-200 ${
                    showFilters 
                      ? 'bg-white/20 text-white border border-white/30 backdrop-blur-sm' 
                      : 'bg-white/10 text-white border border-white/20 hover:bg-white/20 backdrop-blur-sm'
                  }`}
                >
                  <FunnelIcon className="h-5 w-5 mr-2" />
                  Filtros Avanzados
                </button>
                <button
                  onClick={() => refetchDocuments()}
                  className="inline-flex items-center px-6 py-3 text-sm font-semibold text-blue-600 bg-white rounded-xl hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <ArrowPathIcon className="h-5 w-5 mr-2" />
                  Actualizar Datos
                </button>
              
            </div>
          </div>
        </div>

          {/* Estadísticas */}
          {documentStats && typeof documentStats === 'object' && !Array.isArray(documentStats) && (
            <div className="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                <div className="text-center bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-blue-600">
                    {documentStats.total_documents || 0}
                  </div>
                  <div className="text-sm text-gray-600">Total Documentos</div>
                </div>
                <div className="text-center bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-green-600">
                    {documentStats.visit_reports || 0}
                  </div>
                  <div className="text-sm text-gray-600">Reportes de Visita</div>
                </div>
                <div className="text-center bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-orange-600">
                    {documentStats.supplier_reports || 0}
                  </div>
                  <div className="text-sm text-gray-600">Reportes de Proveedor</div>
                </div>
                <div className="text-center bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-purple-600">
                    {documentStats.quality_reports || 0}
                  </div>
                  <div className="text-sm text-gray-600">Reportes de Calidad</div>
                </div>
                <div className="text-center bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-teal-600">
                    {documentStats.lab_reports || 0}
                  </div>
                  <div className="text-sm text-gray-600">Reportes de Laboratorio</div>
                </div>
                <div className="text-center bg-white rounded-lg p-4 shadow-sm">
                  <div className="text-2xl font-bold text-gray-600">
                    {documentStats.incident_attachments || 0}
                  </div>
                  <div className="text-sm text-gray-600">Adjuntos de Incidencia</div>
                </div>
              </div>
          </div>
          )}

          {/* Filtros Mejorados */}
          {showFilters && (
            <div className="px-8 py-6 bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-200">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Filtros Avanzados</h3>
                <p className="text-sm text-gray-600">Filtra y organiza los documentos según tus necesidades</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Búsqueda Mejorada */}
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">
                    🔍 Buscar Documentos
                  </label>
                <div className="relative">
                    <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Título, descripción, código..."
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  />
                </div>
              </div>

                {/* Filtro por tipo mejorado */}
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">
                    📄 Tipo de Documento
                </label>
                <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  >
                    <option value="all">📋 Todos los tipos</option>
                    <option value="visit_report">🏢 Reportes de Visita</option>
                    <option value="supplier_report">🏭 Reportes de Proveedor</option>
                    <option value="lab_report">🧪 Reportes de Laboratorio</option>
                    <option value="quality_report">✅ Reportes de Calidad</option>
                    <option value="incident_attachment">📎 Adjuntos de Incidencia</option>
                </select>
              </div>

                {/* Filtro por estado mejorado */}
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">
                    📊 Estado del Documento
                </label>
                <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  >
                    <option value="all">🔄 Todos los estados</option>
                    <option value="draft">📝 Borrador</option>
                    <option value="pending">⏳ Pendiente</option>
                    <option value="approved">✅ Aprobado</option>
                    <option value="rejected">❌ Rechazado</option>
                </select>
              </div>

                {/* Ordenar por mejorado */}
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-700">
                    🔄 Ordenar por
                </label>
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  >
                    <option value="date">📅 Fecha (más reciente)</option>
                    <option value="title">🔤 Título (A-Z)</option>
                    <option value="type">📄 Tipo</option>
                    <option value="incident">🔢 Código de incidencia</option>
                    <option value="size">💾 Tamaño</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

        {/* Acciones en lote mejoradas */}
        {selectedDocuments.length > 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6 mb-8 shadow-lg">
            <div className="flex items-center justify-between">
          <div className="flex items-center">
                <div className="bg-blue-100 rounded-full p-2 mr-3">
                  <CheckCircleIcon className="h-6 w-6 text-blue-600" />
            </div>
                <div>
                  <span className="text-lg font-semibold text-blue-900">
                    {selectedDocuments.length} documento{selectedDocuments.length !== 1 ? 's' : ''} seleccionado{selectedDocuments.length !== 1 ? 's' : ''}
                  </span>
                  <p className="text-sm text-blue-700">Selecciona las acciones que deseas realizar</p>
          </div>
        </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleBulkDownload}
                  className="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
                  Descargar Seleccionados
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <TrashIcon className="h-5 w-5 mr-2" />
                  Eliminar Seleccionados
                </button>
                <button
                  onClick={handleClearSelection}
                  className="inline-flex items-center px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  <XMarkIcon className="h-5 w-5 mr-2" />
                  Cancelar Selección
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Lista de documentos mejorada */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
          {documentsLoading ? (
            <div className="p-8">
              <div className="animate-pulse space-y-6">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center space-x-6 p-6 border border-gray-100 rounded-xl">
                    <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
                    <div className="flex-1 space-y-3">
                      <div className="h-5 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                    </div>
                    <div className="w-24 h-8 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            </div>
          ) : filteredDocuments.length === 0 ? (
            <div className="p-12 text-center bg-gradient-to-br from-gray-50 to-blue-50">
              <div className="bg-white rounded-full p-6 w-24 h-24 mx-auto mb-6 shadow-lg">
                <DocumentTextIcon className="h-12 w-12 text-gray-400" />
            </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                No hay documentos disponibles
              </h3>
              <p className="text-gray-600 text-lg mb-6">
                Los documentos aparecerán aquí cuando se suban desde las páginas de reportes
              </p>
              <div className="bg-blue-50 rounded-xl p-4 max-w-md mx-auto">
                <p className="text-sm text-blue-800">
                  💡 <strong>Tip:</strong> Ve a las páginas de reportes para adjuntar documentos y verás cómo aparecen aquí automáticamente
                </p>
              </div>
            </div>
          ) : (
            <div className="divide-y divide-gray-100">
              {Object.entries(documentsByIncident).map(([incidentCode, incidentData]) => (
                <div key={incidentCode} className="p-6">
                  {/* Header de la incidencia */}
                  <div className="mb-6 pb-4 border-b-2 border-indigo-200 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                          <DocumentIcon className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">
                            📋 Incidencia: {incidentCode}
                          </h3>
                          <p className="text-sm text-gray-600">
                            {incidentData.count} documento{incidentData.count !== 1 ? 's' : ''} asociado{incidentData.count !== 1 ? 's' : ''}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-indigo-100 text-indigo-800">
                          📄 {incidentData.count} documento{incidentData.count !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Documentos de la incidencia */}
                  <div className="space-y-4">
                    {incidentData.documents.map((document, index) => (
                      <div key={`${document.id || index}-${incidentCode}`} className="p-4 bg-gray-50 rounded-xl hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-200 border-l-4 border-transparent hover:border-blue-400">
                  <div className="flex items-start space-x-6">
                    {/* Checkbox para selección mejorado */}
                    <div className="flex-shrink-0 pt-2">
                      <input
                        type="checkbox"
                        checked={selectedDocuments.includes(document.id)}
                        onChange={(e) => handleDocumentSelection(document.id, e.target.checked)}
                        className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded-lg"
                      />
        </div>

                    {/* Icono del documento mejorado */}
                    <div className="flex-shrink-0">
                      <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl flex items-center justify-center shadow-lg">
                        <span className="text-2xl">{getDocumentIcon(document.document_type)}</span>
              </div>
            </div>
            
                    {/* Información del documento mejorada */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="text-lg font-semibold text-gray-900 mb-1">
                            {getDocumentInfo(document).title}
                          </h4>
                          {document.description && (
                            <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                              {document.description}
                    </p>
                  )}
                </div>
                        <div className="flex items-center space-x-3 ml-4">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(document.status)}`}>
                            {document.status || 'Sin estado'}
                          </span>
                          {document.is_public ? (
                            <div className="flex items-center text-green-600" title="Público">
                              <GlobeAltIcon className="h-5 w-5" />
                            </div>
                          ) : (
                            <div className="flex items-center text-gray-400" title="Privado">
                              <LockClosedIcon className="h-5 w-5" />
                            </div>
                          )}
                        </div>
                </div>

                      {/* Metadatos mejorados */}
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                        <div className="flex items-center text-gray-600">
                          <DocumentTextIcon className="h-4 w-4 mr-2 text-blue-500" />
                          <span className="font-medium">{getDocumentInfo(document).type}</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <BuildingOfficeIcon className="h-4 w-4 mr-2 text-green-500" />
                          <span className="font-medium">{getDocumentInfo(document).incident}</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <CalendarIcon className="h-4 w-4 mr-2 text-purple-500" />
                          <span className="font-medium">{formatDate(getDocumentInfo(document).date)}</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <UserIcon className="h-4 w-4 mr-2 text-orange-500" />
                          <span className="font-medium">{getDocumentInfo(document).user}</span>
                </div>
                        <div className="flex items-center text-gray-600">
                          <DocumentTextIcon className="h-4 w-4 mr-2 text-teal-500" />
                          <span className="font-medium">{formatFileSize(getDocumentInfo(document).size)}</span>
                </div>
                </div>
              </div>

                    {/* Acciones mejoradas */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleViewDocument(document)}
                        className="p-3 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all duration-200 hover:shadow-lg"
                        title="Ver documento"
                      >
                        <EyeIcon className="h-5 w-5" />
                      </button>
                <button
                        onClick={() => handleDownloadDocument(document)}
                        className="p-3 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-xl transition-all duration-200 hover:shadow-lg"
                        title="Descargar documento"
                      >
                        <DocumentArrowDownIcon className="h-5 w-5" />
                </button>
                <button
                        onClick={() => handleDeleteDocument(document)}
                        className="p-3 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all duration-200 hover:shadow-lg"
                        title="Eliminar documento"
                      >
                        <TrashIcon className="h-5 w-5" />
                </button>
              </div>
          </div>
        </div>
                      ))}
                  </div>
                </div>
              ))}
        </div>
      )}
        </div>

        {/* Modal de cierre de incidencia */}
        {showClosureModal && selectedIncident && (
          <IncidentClosureForm
            incidentId={selectedIncident.id}
            incidentCode={selectedIncident.code}
            onClose={() => {
              setShowClosureModal(false);
              setSelectedIncident(null);
            }}
            onSuccess={() => {
              setShowClosureModal(false);
              setSelectedIncident(null);
              refetchDocuments();
            }}
            isOpen={showClosureModal}
          />
        )}
=======
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNotifications } from '../hooks/useNotifications';
import PageHeader from '../components/PageHeader';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  CalendarIcon,
  UserIcon,
  BuildingOfficeIcon,
  TagIcon,
  PaperClipIcon,
  DocumentIcon,
  ChartBarIcon,
  ArrowPathIcon,
  PlusIcon,
  CloudArrowUpIcon,
  DocumentMagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

const Documents = () => {
  const { showSuccess, showError } = useNotifications();
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    incidentCode: '',
    client: '',
    obra: '',
    category: '',
    subcategory: '',
    dateFrom: '',
    dateTo: '',
    documentType: '',
    status: ''
  });
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  // Query para obtener todas las incidencias con sus documentos
  const { data: incidentsData, isLoading: incidentsLoading, refetch: refetchIncidents } = useQuery({
    queryKey: ['incidents-documents', filters],
    queryFn: async () => {
      try {
        const response = await fetch(`/api/incidents/?search=${searchTerm}&estado=&prioridad=`);
        if (!response.ok) throw new Error('Error al cargar incidencias');
        return response.json();
      } catch (error) {
        showError('Error al cargar incidencias: ' + error.message);
        throw error;
      }
    },
    enabled: true,
  });

  // Query para obtener documentos por incidencia
  const { data: documentsData, isLoading: documentsLoading } = useQuery({
    queryKey: ['documents-by-incident', selectedIncident?.id],
    queryFn: async () => {
      if (!selectedIncident?.id) return null;
      
      try {
        const [documentsRes, visitReportsRes, qualityReportsRes, supplierReportsRes, labReportsRes] = await Promise.all([
          fetch(`/api/documents/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/visit-reports/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/quality-reports/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/supplier-reports/?incident_id=${selectedIncident.id}`),
          fetch(`/api/documents/lab-reports/?incident_id=${selectedIncident.id}`)
        ]);

        const [documents, visitReports, qualityReports, supplierReports, labReports] = await Promise.all([
          documentsRes.ok ? documentsRes.json() : { results: [] },
          visitReportsRes.ok ? visitReportsRes.json() : { results: [] },
          qualityReportsRes.ok ? qualityReportsRes.json() : { results: [] },
          supplierReportsRes.ok ? supplierReportsRes.json() : { results: [] },
          labReportsRes.ok ? labReportsRes.json() : { results: [] }
        ]);

        return {
          documents: documents.results || documents.data || documents || [],
          visitReports: visitReports.results || visitReports.data || visitReports || [],
          qualityReports: qualityReports.results || qualityReports.data || qualityReports || [],
          supplierReports: supplierReports.results || supplierReports.data || supplierReports || [],
          labReports: labReports.results || labReports.data || labReports || []
        };
      } catch (error) {
        showError('Error al cargar documentos: ' + error.message);
        return null;
      }
    },
    enabled: !!selectedIncident?.id,
  });

  // Procesar datos de incidencias
  const incidents = incidentsData?.data?.results || incidentsData?.results || incidentsData || [];
  
  // Filtrar incidencias basado en los filtros
  const filteredIncidents = incidents.filter(incident => {
    const matchesSearch = !searchTerm || 
      (incident.code && incident.code.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (incident.cliente && incident.cliente.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (incident.obra && incident.obra.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilters = 
      (!filters.incidentCode || (incident.code && incident.code.includes(filters.incidentCode))) &&
      (!filters.client || (incident.cliente && incident.cliente.toLowerCase().includes(filters.client.toLowerCase()))) &&
      (!filters.obra || (incident.obra && incident.obra.toLowerCase().includes(filters.obra.toLowerCase()))) &&
      (!filters.category || (incident.categoria && incident.categoria.name === filters.category)) &&
      (!filters.subcategory || (incident.subcategoria && incident.subcategoria.toLowerCase().includes(filters.subcategory.toLowerCase()))) &&
      (!filters.dateFrom || new Date(incident.fecha_reporte) >= new Date(filters.dateFrom)) &&
      (!filters.dateTo || new Date(incident.fecha_reporte) <= new Date(filters.dateTo)) &&
      (!filters.status || incident.estado === filters.status);

    return matchesSearch && matchesFilters;
  });

  // Combinar todos los documentos de una incidencia
  const getAllDocumentsForIncident = (incidentId) => {
    if (!documentsData || selectedIncident?.id !== incidentId) return [];
    
    const allDocs = [
      ...documentsData.documents.map(doc => ({ ...doc, type: 'document', typeLabel: 'Documento' })),
      ...documentsData.visitReports.map(doc => ({ ...doc, type: 'visit_report', typeLabel: 'Reporte de Visita' })),
      ...documentsData.qualityReports.map(doc => ({ ...doc, type: 'quality_report', typeLabel: 'Reporte de Calidad' })),
      ...documentsData.supplierReports.map(doc => ({ ...doc, type: 'supplier_report', typeLabel: 'Reporte de Proveedor' })),
      ...documentsData.labReports.map(doc => ({ ...doc, type: 'lab_report', typeLabel: 'Reporte de Laboratorio' }))
    ];
    
    return allDocs;
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      incidentCode: '',
      client: '',
      obra: '',
      category: '',
      subcategory: '',
      dateFrom: '',
      dateTo: '',
      documentType: '',
      status: ''
    });
    setSearchTerm('');
  };

  const downloadDocument = async (document) => {
    try {
      const response = await fetch(`/api/documents/${document.id}/download/`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = document.title || document.name || 'documento';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showSuccess('Documento descargado exitosamente');
      } else {
        showError('Error al descargar el documento');
      }
    } catch (error) {
      showError('Error al descargar el documento: ' + error.message);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'abierto': return 'bg-red-100 text-red-800';
      case 'en_proceso': return 'bg-yellow-100 text-yellow-800';
      case 'cerrado': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'alta': return 'bg-red-100 text-red-800';
      case 'media': return 'bg-yellow-100 text-yellow-800';
      case 'baja': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <PageHeader
        title="Trazabilidad de Documentos"
        subtitle="Sistema completo de gestión y trazabilidad de documentos por incidencia"
        icon={DocumentMagnifyingGlassIcon}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros y Búsqueda */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* Búsqueda */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por código, cliente, obra..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Botones */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filtros Avanzados
              </button>
              
              <button
                onClick={() => refetchIncidents()}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Actualizar
              </button>
            </div>
          </div>

          {/* Filtros Avanzados */}
          {showFilters && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Código de Incidencia
                </label>
                <input
                  type="text"
                  value={filters.incidentCode}
                  onChange={(e) => handleFilterChange('incidentCode', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Ej: INC-2025-001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cliente
                </label>
                <input
                  type="text"
                  value={filters.client}
                  onChange={(e) => handleFilterChange('client', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nombre del cliente"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Obra
                </label>
                <input
                  type="text"
                  value={filters.obra}
                  onChange={(e) => handleFilterChange('obra', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Nombre de la obra"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estado
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Todos los estados</option>
                  <option value="abierto">Abierto</option>
                  <option value="en_proceso">En Proceso</option>
                  <option value="cerrado">Cerrado</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha Desde
                </label>
                <input
                  type="date"
                  value={filters.dateFrom}
                  onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fecha Hasta
                </label>
                <input
                  type="date"
                  value={filters.dateTo}
                  onChange={(e) => handleFilterChange('dateTo', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                >
                  Limpiar Filtros
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Estadísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Incidencias</p>
                <p className="text-2xl font-bold text-gray-900">{filteredIncidents.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <DocumentIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Documentos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredIncidents.reduce((total, incident) => {
                    const docs = getAllDocumentsForIncident(incident.id);
                    return total + docs.length;
                  }, 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <ChartBarIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Abiertas</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredIncidents.filter(incident => incident.estado === 'abierto').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <PaperClipIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Con Adjuntos</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredIncidents.filter(incident => {
                    const docs = getAllDocumentsForIncident(incident.id);
                    return docs.length > 0;
                  }).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Lista de Incidencias */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Incidencias y Documentos ({filteredIncidents.length})
            </h3>
          </div>

          {incidentsLoading ? (
            <div className="p-8 text-center">
              <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
              <p className="text-gray-600">Cargando incidencias...</p>
            </div>
          ) : filteredIncidents.length === 0 ? (
            <div className="p-8 text-center">
              <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No se encontraron incidencias con los filtros aplicados</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredIncidents.map((incident) => {
                const documents = getAllDocumentsForIncident(incident.id);
                const isSelected = selectedIncident?.id === incident.id;
                
                return (
                  <div key={incident.id} className="p-6 hover:bg-gray-50 transition-colors duration-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <button
                            onClick={() => setSelectedIncident(isSelected ? null : incident)}
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              isSelected 
                                ? 'bg-blue-100 text-blue-800' 
                                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                            }`}
                          >
                            {isSelected ? 'Ocultar Documentos' : 'Ver Documentos'}
                          </button>
                          
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(incident.estado)}`}>
                            {incident.estado}
                          </span>
                          
                          {incident.prioridad && (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(incident.prioridad)}`}>
                              {incident.prioridad}
                            </span>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-1">
                              {incident.code || `INC-${incident.id}`}
                            </h4>
                            <p className="text-sm text-gray-600">
                              <BuildingOfficeIcon className="h-4 w-4 inline mr-1" />
                              {incident.cliente || 'Sin cliente'}
                            </p>
                          </div>

                          <div>
                            <p className="text-sm text-gray-600">
                              <BuildingOfficeIcon className="h-4 w-4 inline mr-1" />
                              {incident.obra || 'Sin obra'}
                            </p>
                            <p className="text-sm text-gray-600">
                              <TagIcon className="h-4 w-4 inline mr-1" />
                              {incident.categoria?.name || 'Sin categoría'}
                            </p>
                          </div>

                          <div>
                            <p className="text-sm text-gray-600">
                              <CalendarIcon className="h-4 w-4 inline mr-1" />
                              {new Date(incident.fecha_reporte).toLocaleDateString()}
                            </p>
                            <p className="text-sm text-gray-600">
                              <UserIcon className="h-4 w-4 inline mr-1" />
                              {incident.provider || 'Sin proveedor'}
                            </p>
                          </div>
                        </div>

                        <p className="text-gray-700 text-sm mb-4">
                          {incident.descripcion || 'Sin descripción'}
                        </p>

                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <DocumentIcon className="h-4 w-4 mr-1" />
                            {documents.length} documentos
                          </span>
                          {incident.sku && (
                            <span className="flex items-center">
                              <TagIcon className="h-4 w-4 mr-1" />
                              SKU: {incident.sku}
                            </span>
                          )}
                          {incident.lote && (
                            <span className="flex items-center">
                              <TagIcon className="h-4 w-4 mr-1" />
                              Lote: {incident.lote}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Documentos de la Incidencia */}
                    {isSelected && (
                      <div className="mt-6 pt-6 border-t border-gray-200">
                        {documentsLoading ? (
                          <div className="text-center py-4">
                            <ArrowPathIcon className="h-6 w-6 animate-spin text-blue-600 mx-auto mb-2" />
                            <p className="text-gray-600">Cargando documentos...</p>
                          </div>
                        ) : documents.length === 0 ? (
                          <div className="text-center py-8">
                            <PaperClipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-600">No hay documentos adjuntos para esta incidencia</p>
                          </div>
                        ) : (
                          <div>
                            <h5 className="font-semibold text-gray-900 mb-4">Documentos Adjuntos</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                              {documents.map((doc, index) => (
                                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                                  <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center">
                                      <DocumentIcon className="h-5 w-5 text-blue-600 mr-2" />
                                      <div>
                                        <p className="font-medium text-gray-900 text-sm">
                                          {doc.title || doc.name || `Documento ${index + 1}`}
                                        </p>
                                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                          {doc.typeLabel}
                                        </span>
                                      </div>
                                    </div>
                                  </div>

                                  {doc.description && (
                                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                                      {doc.description}
                                    </p>
                                  )}

                                  <div className="flex items-center justify-between">
                                    <div className="text-xs text-gray-500">
                                      {doc.created_at && (
                                        <span>
                                          {new Date(doc.created_at).toLocaleDateString()}
                                        </span>
                                      )}
                                    </div>
                                    <button
                                      onClick={() => downloadDocument(doc)}
                                      className="inline-flex items-center px-3 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                      <DocumentArrowDownIcon className="h-3 w-3 mr-1" />
                                      Descargar
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
>>>>>>> 674c244 (tus cambios)
      </div>
    </div>
  );
};

export default Documents;