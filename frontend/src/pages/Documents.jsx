import React, { useState, useMemo } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNotifications } from '../hooks/useNotifications';
import { incidentsAPI, api } from '../services/api';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  DocumentTextIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  ArrowPathIcon,
  XMarkIcon,
  FolderOpenIcon,
  FolderIcon,
  DocumentIcon,
  ClipboardDocumentListIcon,
  PhotoIcon,
  PaperClipIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  BeakerIcon,
  TruckIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

const Documents = () => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useNotifications();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    dateFrom: '',
    dateTo: '',
  });

  // State for collapsible image folders
  const [expandedFolders, setExpandedFolders] = useState({
    incident_images: false,
    visit_images: false
  });

  // Toggle folder expansion
  const toggleFolder = (folderType) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderType]: !prev[folderType]
    }));
  };

  // Fetch incidents with authentication
  const { data: incidentsData, isLoading, error, refetch } = useQuery({
    queryKey: ['documents-incidents', filters],
    queryFn: async () => {
      const response = await incidentsAPI.list({ page_size: 100 });
      return response.data?.results || response.data || [];
    },
    staleTime: 30000,
  });

  // Fetch documents for selected incident (all document types)
  const { data: allDocsData, isLoading: loadingDocs } = useQuery({
    queryKey: ['incident-all-documents', selectedIncident?.id],
    queryFn: async () => {
      if (!selectedIncident?.id) return { attachments: [], visitReports: [], reportImages: [], qualityReports: [], supplierReports: [] };

      try {
        // Fetch incident attachments
        const attachmentsRes = await api.get(`/documents/attachments/incident/${selectedIncident.id}/`);
        const attachments = attachmentsRes.data?.attachments ||
          (Array.isArray(attachmentsRes.data) ? attachmentsRes.data :
            (attachmentsRes.data?.results || []));

        // Fetch visit reports for this incident
        const visitReportsRes = await api.get(`/documents/visit-reports/?incident_id=${selectedIncident.id}`);
        const visitReports = Array.isArray(visitReportsRes.data) ? visitReportsRes.data :
          (visitReportsRes.data?.results || []);

        // Fetch quality reports for this incident (both client and internal)
        let qualityReports = [];
        try {
          const qualityRes = await api.get(`/documents/quality-reports/by-incident/${selectedIncident.id}/`);
          // Backend returns { success: true, reports: [...] }
          qualityReports = qualityRes.data?.reports ||
            (Array.isArray(qualityRes.data) ? qualityRes.data : []) ||
            [];
        } catch (e) {
          // Try alternative endpoint or fail silently
          try {
            // Fallback attempt
            const qualityRes = await api.get(`/documents/quality-reports/?incident_id=${selectedIncident.id}`);
            qualityReports = qualityRes.data?.results || (Array.isArray(qualityRes.data) ? qualityRes.data : []) || [];
          } catch (e2) { }
          console.warn('Error specific to quality reports fetch', e);
        }

        // Fetch supplier reports for this incident
        let supplierReports = [];
        try {
          const supplierRes = await api.get(`/documents/supplier-reports/?incident_id=${selectedIncident.id}`);
          supplierReports = Array.isArray(supplierRes.data) ? supplierRes.data : (supplierRes.data?.results || []);
        } catch (e) { }


        // Fetch report images for each visit report
        let reportImages = [];
        for (const report of visitReports) {
          try {
            const imagesRes = await api.get(`/documents/report-attachments/${report.id}/visit/`);
            const images = Array.isArray(imagesRes.data) ? imagesRes.data : (imagesRes.data?.results || []);
            reportImages = [...reportImages, ...images.map(img => ({
              ...img,
              reportId: report.id,
              reportNumber: report.order_number
            }))];
          } catch (e) { }
        }

        return { attachments, visitReports, reportImages, qualityReports, supplierReports };
      } catch (error) {
        console.error('Error fetching documents:', error);
        return { attachments: [], visitReports: [], reportImages: [], qualityReports: [], supplierReports: [] };
      }
    },
    enabled: !!selectedIncident?.id,
  });

  const incidents = incidentsData || [];
  const {
    attachments = [],
    visitReports = [],
    reportImages = [],
    qualityReports = [],
    supplierReports = []
  } = allDocsData || {};

  // Combine all documents into a single list with proper labels
  const allDocuments = useMemo(() => {
    const docs = [];

    // Add visit reports first (most important)
    visitReports.forEach((report, index) => {
      docs.push({
        id: `vr-${report.id}`,
        type: 'visit_report',
        typeLabel: 'Reporte de Visita',
        name: report.order_number || `RV-${index + 1}`,
        filename: report.pdf_path ? report.pdf_path.split(/[/\\]/).pop() : 'Reporte de Visita.pdf',
        created_at: report.created_at || report.visit_date,
        downloadUrl: `/documents/visit-reports/${report.id}/download/`,
        hasDocument: !!report.pdf_path || !!report.has_document,
        icon: 'report',
        reportId: report.id
      });
    });

    // Add quality reports (client and internal)
    qualityReports.forEach((report, index) => {
      const isClient = report.report_type === 'cliente';
      docs.push({
        id: `qr-${report.id}`,
        type: isClient ? 'quality_client' : 'quality_internal',
        typeLabel: isClient ? 'Calidad Cliente' : 'Calidad Interno',
        name: report.report_number || `QR-${index + 1}`,
        filename: report.pdf_path ? report.pdf_path.split(/[/\\]/).pop() : `Reporte Calidad.pdf`,
        created_at: report.created_at,
        downloadUrl: `/documents/quality-reports/${report.id}/download/`,
        hasDocument: !!report.pdf_path,
        icon: isClient ? 'quality_client' : 'quality_internal',
        reportId: report.id,
        status: report.status
      });
    });

    // Add supplier reports
    supplierReports.forEach((report, index) => {
      docs.push({
        id: `sr-${report.id}`,
        type: 'supplier_report',
        typeLabel: 'Reclamo Proveedor',
        name: report.report_number || `RCP-${index + 1}`,
        filename: report.pdf_path ? report.pdf_path.split(/[/\\]/).pop() : 'Reclamo Proveedor.pdf',
        created_at: report.created_at,
        downloadUrl: `/documents/supplier-reports/${report.id}/download/`,
        hasDocument: !!report.pdf_path,
        icon: 'supplier',
        reportId: report.id,
        status: report.status,
        supplierName: report.supplier_name
      });
    });


    // Add report images (from visit reports)
    reportImages.forEach((img, index) => {
      docs.push({
        id: `ri-${img.id}`,
        type: 'report_image',
        typeLabel: `Imagen (${img.reportNumber || 'RV'})`,
        name: img.description || img.filename || `Imagen-${index + 1}`,
        filename: img.filename,
        description: img.description,
        created_at: img.created_at,
        downloadUrl: `/documents/report-attachments/${img.reportId}/visit/${img.id}/view/`,
        hasDocument: true,
        icon: 'image',
        reportId: img.reportId
      });
    });

    // Add incident attachments
    attachments.forEach((att, index) => {
      const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(att.filename || att.name || '');

      // Check if this is a supplier response attachment based on document_type
      const isSupplierResponse = att.document_type === 'supplier_response';

      // Check if this is a closure attachment based on title or description
      const isClosureAttachment =
        (att.title && att.title.toLowerCase().includes('cierre')) ||
        (att.description && att.description.toLowerCase().includes('cierre'));

      let typeLabel = isImage ? 'Imagen' : 'Adjunto';
      if (isSupplierResponse) {
        typeLabel = 'Respuesta Proveedor';
      } else if (isClosureAttachment) {
        typeLabel = isImage ? 'Imagen Cierre' : 'Adjunto Cierre';
      }

      docs.push({
        id: `att-${att.id}`,
        type: isSupplierResponse ? 'supplier_response' : (isClosureAttachment ? 'closure_attachment' : (isImage ? 'image' : 'attachment')),
        typeLabel: typeLabel,
        name: att.description || att.filename || att.name || `Adjunto-${index + 1}`,
        title: att.title,
        description: att.description,
        filename: att.filename || att.name,
        created_at: att.created_at,
        downloadUrl: att.download_url || `/documents/attachments/incident/${selectedIncident?.id}/${att.id}/download/`,
        viewUrl: att.view_url || `/documents/attachments/incident/${selectedIncident?.id}/${att.id}/view/`,
        hasDocument: true,
        icon: isSupplierResponse ? 'supplier_response' : (isClosureAttachment ? 'closure' : (isImage ? 'image' : 'attachment'))
      });
    });

    return docs;
  }, [visitReports, attachments, reportImages, qualityReports, supplierReports, selectedIncident]);

  // Group images into collapsible folders (OPTIMIZED with useMemo)
  const combinedDocuments = useMemo(() => {
    const result = [];

    // Separate images from other documents
    const incidentImages = allDocuments.filter(d => d.type === 'image');
    const visitImages = allDocuments.filter(d => d.type === 'report_image');
    const otherDocs = allDocuments.filter(d => d.type !== 'image' && d.type !== 'report_image');

    // Add incident images folder if there are any
    if (incidentImages.length > 0) {
      result.push({
        id: 'folder-incident-images',
        type: 'folder',
        folderType: 'incident_images',
        name: '🖼️ Imágenes Incidencia',
        count: incidentImages.length,
        children: incidentImages,
        isExpanded: expandedFolders.incident_images
      });
    }

    // Add visit report images folder if there are any
    if (visitImages.length > 0) {
      result.push({
        id: 'folder-visit-images',
        type: 'folder',
        folderType: 'visit_images',
        name: '📸 Imágenes Reporte de Visita',
        count: visitImages.length,
        children: visitImages,
        isExpanded: expandedFolders.visit_images
      });
    }

    // Add all other documents (not grouped)
    result.push(...otherDocs);

    // Sort: folders first, then by date
    result.sort((a, b) => {
      if (a.type === 'folder' && b.type !== 'folder') return -1;
      if (a.type !== 'folder' && b.type === 'folder') return 1;

      const dateA = new Date(a.created_at || 0);
      const dateB = new Date(b.created_at || 0);
      return dateB - dateA;
    });

    return result;
  }, [allDocuments, expandedFolders]);


  // Filter incidents
  const filteredIncidents = useMemo(() => {
    return incidents.filter(incident => {
      const matchesSearch = !searchTerm ||
        (incident.code && incident.code.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (incident.cliente && incident.cliente.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (incident.obra && incident.obra.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (incident.provider && incident.provider.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (incident.categoria && incident.categoria.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (incident.subcategoria && incident.subcategoria.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesStatus = !filters.status || incident.estado === filters.status;

      const matchesDateFrom = !filters.dateFrom ||
        new Date(incident.fecha_reporte) >= new Date(filters.dateFrom);

      const matchesDateTo = !filters.dateTo ||
        new Date(incident.fecha_reporte) <= new Date(filters.dateTo);

      return matchesSearch && matchesStatus && matchesDateFrom && matchesDateTo;
    });
  }, [incidents, searchTerm, filters]);

  const handleRefresh = () => {
    refetch();
    queryClient.invalidateQueries(['incident-all-documents']);
    showSuccess('Datos actualizados');
  };

  const clearFilters = () => {
    setFilters({ status: '', dateFrom: '', dateTo: '' });
    setSearchTerm('');
  };

  const handleViewDocument = async (doc) => {
    try {
      const response = await api.get(doc.downloadUrl, { responseType: 'blob' });

      // Determine MIME type
      const extension = (doc.filename || '').split('.').pop()?.toLowerCase();
      const mimeTypes = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      };

      const blob = new Blob([response.data], { type: mimeTypes[extension] || 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => window.URL.revokeObjectURL(url), 60000);
    } catch (error) {
      console.error('Error viewing document:', error);
      showError('Error al visualizar el documento');
    }
  };

  const handleDownloadDocument = async (doc) => {
    try {
      const response = await api.get(doc.downloadUrl, { responseType: 'blob' });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.filename || 'documento');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      showSuccess('Documento descargado');
    } catch (error) {
      showError('Error al descargar el documento');
    }
  };

  // Get stage info with icon and color (Standardized)
  const getStageInfo = (incident) => {
    // 1. Cerrado
    if (incident.estado === 'cerrado' || incident.estado === 'completed') {
      return {
        icon: <CheckCircleIcon className="h-4 w-4" />,
        color: 'text-gray-600 bg-gray-200',
        label: 'Cerrado',
        date: incident.closed_at || incident.updated_at
      };
    }

    // 2. En Proveedor
    if (incident.escalated_to_supplier || incident.estado === 'proveedor' || incident.estado === 'escalado_proveedor') {
      return {
        icon: <TruckIcon className="h-4 w-4" />,
        color: 'text-orange-600 bg-orange-100',
        label: 'En Proveedor',
        date: incident.escalation_date || incident.updated_at
      };
    }

    // 3. En Calidad (Cliente o Interno)
    if (incident.escalated_to_internal_quality || incident.escalated_to_quality || incident.estado === 'calidad' || incident.estado === 'escalado_calidad' || incident.estado === 'en_calidad') {
      return {
        icon: <BeakerIcon className="h-4 w-4" />,
        color: 'text-purple-600 bg-purple-100',
        label: 'En Calidad',
        date: incident.escalation_date || incident.updated_at
      };
    }

    // 4. En Reporte de Visita
    if (incident.estado === 'visit_report' || incident.estado === 'reporte_visita' || incident.estado === 'en_proceso') {
      return {
        icon: <ClipboardDocumentListIcon className="h-4 w-4" />,
        color: 'text-indigo-600 bg-indigo-100',
        label: 'En Reporte de Visita',
        date: incident.fecha_deteccion || incident.created_at
      };
    }

    // 5. Abierto (Default)
    return {
      icon: <ClockIcon className="h-4 w-4" />,
      color: 'text-blue-600 bg-blue-100',
      label: 'Abierto',
      date: incident.fecha_deteccion || incident.created_at
    };
  };

  const getDocumentIcon = (doc) => {
    if (doc.icon === 'report') {
      return <ClipboardDocumentListIcon className="h-5 w-5 text-blue-600" />;
    }
    if (doc.icon === 'quality_client') {
      return <BeakerIcon className="h-5 w-5 text-emerald-600" />;
    }
    if (doc.icon === 'quality_internal') {
      return <BeakerIcon className="h-5 w-5 text-indigo-600" />;
    }
    if (doc.icon === 'supplier') {
      return <TruckIcon className="h-5 w-5 text-orange-600" />;
    }
    if (doc.icon === 'lab') {
      return <BeakerIcon className="h-5 w-5 text-purple-600" />;
    }
    if (doc.icon === 'image') {
      return <PhotoIcon className="h-5 w-5 text-green-500" />;
    }
    const ext = (doc.filename || '').split('.').pop()?.toLowerCase();
    if (['pdf'].includes(ext)) return <DocumentTextIcon className="h-5 w-5 text-red-500" />;
    if (['doc', 'docx'].includes(ext)) return <DocumentIcon className="h-5 w-5 text-blue-500" />;
    return <PaperClipIcon className="h-5 w-5 text-gray-500" />;
  };

  const getTypeBadge = (doc) => {
    const colors = {
      'visit_report': 'bg-blue-100 text-blue-800 border-blue-200',
      'quality_client': 'bg-emerald-100 text-emerald-800 border-emerald-200',
      'quality_internal': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'supplier_report': 'bg-orange-100 text-orange-800 border-orange-200',
      'supplier_response': 'bg-orange-100 text-orange-800 border-orange-200',
      'report_image': 'bg-pink-100 text-pink-800 border-pink-200',
      'image': 'bg-green-100 text-green-800 border-green-200',
      'attachment': 'bg-gray-100 text-gray-800 border-gray-200',
      'closure_attachment': 'bg-teal-100 text-teal-800 border-teal-200',
    };
    return (
      <span className={`px-2 py-0.5 text-xs font-medium rounded border ${colors[doc.type] || colors.attachment}`}>
        {doc.typeLabel}
      </span>
    );
  };

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <p className="text-red-600">Error al cargar documentos: {error.message}</p>
          <button onClick={handleRefresh} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg">
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">📁 Trazabilidad de Documentos</h1>
            <p className="mt-2 text-lg text-gray-600">
              Centro de trazabilidad documental completo por incidencia
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-xl hover:bg-gray-50"
          >
            <ArrowPathIcon className="h-5 w-5 mr-2 text-gray-600" />
            Actualizar
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1 relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por código, cliente, obra, proveedor..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`inline-flex items-center px-4 py-3 rounded-xl border ${showFilters ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-gray-300'}`}
            >
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filtros
            </button>
            {(searchTerm || filters.status || filters.dateFrom || filters.dateTo) && (
              <button
                onClick={clearFilters}
                className="inline-flex items-center px-4 py-3 text-red-600 hover:text-red-800"
              >
                <XMarkIcon className="h-5 w-5 mr-1" />
                Limpiar
              </button>
            )}
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Estado</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                <option value="">Todos</option>
                <option value="abierto">Abierto</option>
                <option value="proveedor">Proveedor</option>
                <option value="cerrado">Cerrado</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Fecha desde</label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Fecha hasta</label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>
          </div>
        )}
      </div>

      {/* Main Content - Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Incidents List */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <h2 className="text-lg font-semibold text-white flex items-center">
              <ClipboardDocumentListIcon className="h-5 w-5 mr-2" />
              Incidencias ({filteredIncidents.length})
            </h2>
          </div>

          {isLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
              <p className="mt-4 text-gray-500">Cargando incidencias...</p>
            </div>
          ) : filteredIncidents.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <FolderOpenIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>No se encontraron incidencias</p>
            </div>
          ) : (
            <div className="max-h-[600px] overflow-y-auto divide-y divide-gray-100">
              {filteredIncidents.map((incident) => {
                const stageInfo = getStageInfo(incident);
                return (
                  <div
                    key={incident.id}
                    onClick={() => setSelectedIncident(incident)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${selectedIncident?.id === incident.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                      }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{incident.code}</p>
                        <p className="text-sm text-gray-800 mt-1 font-medium">
                          {incident.cliente} {incident.obra ? `• ${incident.obra}` : ''}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">Prov: {incident.provider || '-'}</p>
                        {(incident.categoria || incident.subcategoria) && (
                          <div className="mt-1">
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700">
                              {incident.categoria || '-'}
                              {incident.subcategoria ? ` / ${incident.subcategoria}` : ''}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${stageInfo.color}`}>
                          {stageInfo.icon}
                          <span className="ml-1">{stageInfo.label}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                          Desde: {stageInfo.date ? new Date(stageInfo.date).toLocaleDateString('es-ES') : new Date(incident.fecha_deteccion || incident.created_at).toLocaleDateString('es-ES')}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Documents Panel */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4">
            <h2 className="text-lg font-semibold text-white flex items-center">
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Documentos {selectedIncident ? `- ${selectedIncident.code}` : ''}
            </h2>
          </div>

          {!selectedIncident ? (
            <div className="p-8 text-center text-gray-500">
              <DocumentIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Selecciona una incidencia para ver sus documentos</p>
            </div>
          ) : loadingDocs ? (
            <div className="p-8 text-center">
              <div className="animate-spin h-8 w-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto"></div>
              <p className="mt-4 text-gray-500">Cargando documentos...</p>
            </div>
          ) : (
            <>
              {/* Document List */}
              {combinedDocuments.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <FolderOpenIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No hay documentos para esta incidencia</p>
                </div>
              ) : (
                <div className="max-h-[350px] overflow-y-auto divide-y divide-gray-100">
                  {combinedDocuments.map((doc) => {
                    // Render folder row
                    if (doc.type === 'folder') {
                      return (
                        <React.Fragment key={doc.id}>
                          {/* Folder Header */}
                          <div
                            onClick={() => toggleFolder(doc.folderType)}
                            className="p-4 hover:bg-slate-50/70 cursor-pointer bg-slate-50/30 transition-all duration-200"
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="p-2 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                                  {doc.isExpanded ? (
                                    <FolderOpenIcon className="h-5 w-5 text-blue-600" />
                                  ) : (
                                    <FolderIcon className="h-5 w-5 text-blue-500" />
                                  )}
                                </div>
                                <div>
                                  <div className="flex items-center gap-2">
                                    <p className="font-semibold text-gray-900">{doc.name}</p>
                                    <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-blue-100 text-blue-700 border border-blue-200">
                                      {doc.count}
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-500 mt-0.5">
                                    Click para {doc.isExpanded ? 'colapsar' : 'expandir'}
                                  </p>
                                </div>
                              </div>
                              <ChevronRightIcon
                                className={`h-5 w-5 text-gray-400 transition-transform duration-200 ${doc.isExpanded ? 'rotate-90' : ''}`}
                              />
                            </div>
                          </div>

                          {/* Folder Children (with smooth animation) */}
                          {doc.isExpanded && doc.children.map((child) => (
                            <div
                              key={child.id}
                              className="pl-12 pr-4 py-3 hover:bg-gray-50 border-l-2 border-blue-200"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                  <div className="p-2 bg-gray-100 rounded-lg">
                                    {getDocumentIcon(child)}
                                  </div>
                                  <div>
                                    <div className="flex items-center gap-2">
                                      <p className="font-medium text-gray-900 text-sm">{child.name}</p>
                                      {getTypeBadge(child)}
                                    </div>
                                    <p className="text-xs text-gray-500 mt-1">
                                      {child.filename}
                                    </p>
                                    {child.created_at && (
                                      <p className="text-xs text-gray-400">
                                        {new Date(child.created_at).toLocaleDateString('es-ES')}
                                      </p>
                                    )}
                                  </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                  {child.hasDocument && (
                                    <>
                                      <button
                                        onClick={() => handleViewDocument(child)}
                                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                        title="Ver"
                                      >
                                        <EyeIcon className="h-4 w-4" />
                                      </button>
                                      <button
                                        onClick={() => handleDownloadDocument(child)}
                                        className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                        title="Descargar"
                                      >
                                        <DocumentArrowDownIcon className="h-4 w-4" />
                                      </button>
                                    </>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </React.Fragment>
                      );
                    }

                    // Render regular document row
                    return (
                      <div key={doc.id} className="p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="p-2 bg-gray-100 rounded-lg">
                              {getDocumentIcon(doc)}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <p className="font-medium text-gray-900">{doc.name}</p>
                                {getTypeBadge(doc)}
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                {doc.filename}
                              </p>
                              {doc.created_at && (
                                <p className="text-xs text-gray-400">
                                  {new Date(doc.created_at).toLocaleDateString('es-ES')}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {doc.hasDocument && (
                              <>
                                <button
                                  onClick={() => handleViewDocument(doc)}
                                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                  title="Ver"
                                >
                                  <EyeIcon className="h-5 w-5" />
                                </button>
                                <button
                                  onClick={() => handleDownloadDocument(doc)}
                                  className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                  title="Descargar"
                                >
                                  <DocumentArrowDownIcon className="h-5 w-5" />
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Incident Info Card with Stages */}
              <div className="border-t bg-gray-50 p-4">
                <h3 className="font-semibold text-gray-900 mb-3">📋 Trazabilidad de la Incidencia</h3>

                {/* Stage Timeline */}
                <div className="mb-4">
                  <div className="flex items-center space-x-2 mb-2">
                    {(() => {
                      const stageInfo = getStageInfo(selectedIncident);
                      return (
                        <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium ${stageInfo.color}`}>
                          {stageInfo.icon}
                          <span className="ml-2">Etapa actual: {stageInfo.label}</span>
                        </div>
                      );
                    })()}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-500">Cliente:</span>
                    <p className="font-medium">{selectedIncident.cliente || '-'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Obra:</span>
                    <p className="font-medium">{selectedIncident.obra || '-'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Proveedor:</span>
                    <p className="font-medium">{selectedIncident.provider || '-'}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Categoría:</span>
                    <p className="font-medium text-xs mt-0.5">
                      {selectedIncident.categoria || '-'}
                      {selectedIncident.subcategoria ? ` / ${selectedIncident.subcategoria}` : ''}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Fecha Detección:</span>
                    <p className="font-medium">
                      {selectedIncident.fecha_deteccion ? new Date(selectedIncident.fecha_deteccion).toLocaleDateString('es-ES') : '-'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Documentos:</span>
                    <p className="font-medium">{allDocuments.length}</p>
                  </div>

                  {selectedIncident.escalation_date && (
                    <div className="col-span-2">
                      <span className="text-gray-500">Fecha Escalamiento:</span>
                      <p className="font-medium">
                        {new Date(selectedIncident.escalation_date).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                  )}

                  {selectedIncident.estado === 'cerrado' && (
                    <>
                      <div className="col-span-2">
                        <span className="text-gray-500">Fecha Cierre:</span>
                        <p
                          className="font-medium cursor-help"
                          title={selectedIncident.closure_summary || 'Sin resumen'}
                        >
                          {selectedIncident.fecha_cierre ? new Date(selectedIncident.fecha_cierre).toLocaleDateString('es-ES') :
                            selectedIncident.closed_at ? new Date(selectedIncident.closed_at).toLocaleDateString('es-ES') : '-'}
                        </p>
                      </div>
                      {selectedIncident.motivo_cierre && (
                        <div className="col-span-2">
                          <span className="text-gray-500">Motivo de Cierre:</span>
                          <p className="font-medium text-green-700 bg-green-50 px-2 py-1 rounded mt-1">
                            {selectedIncident.motivo_cierre}
                          </p>
                        </div>
                      )}
                      {selectedIncident.closure_summary && (
                        <div className="col-span-2 mt-1">
                          <span className="text-gray-500 text-xs">Resumen de Cierre:</span>
                          <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded mt-1 border border-gray-100">
                            {selectedIncident.closure_summary}
                          </p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Documents;