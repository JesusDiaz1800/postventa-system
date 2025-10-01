import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import {
  EyeIcon,
  PencilIcon,
  TrashIcon,
  DocumentArrowDownIcon,
  ClipboardDocumentListIcon,
  BeakerIcon,
  TruckIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

const TraceabilityOverview = () => {
  const [searchTerm, setSearchTerm] = useState('');

  // Query para obtener todas las incidencias
  const { data: incidents, isLoading: incidentsLoading } = useQuery({
    queryKey: ['incidents'],
    queryFn: () => api.get('/incidents/').then(res => res.data),
    onError: (error) => {
      console.error('Error fetching incidents:', error);
    }
  });

  // Query para obtener todos los documentos
  const { data: allDocuments, isLoading: documentsLoading } = useQuery({
    queryKey: ['allDocuments'],
    queryFn: async () => {
      try {
        const [visitReports, labReports, supplierReports] = await Promise.all([
          api.get('/documents/visit-reports/').then(res => res.data).catch(err => {
            console.error('Error fetching visit reports:', err);
            return { results: [] };
          }),
          api.get('/documents/lab-reports/').then(res => res.data).catch(err => {
            console.error('Error fetching lab reports:', err);
            return { results: [] };
          }),
          api.get('/documents/supplier-reports/').then(res => res.data).catch(err => {
            console.error('Error fetching supplier reports:', err);
            return { results: [] };
          }),
        ]);

        return {
          visitReports: visitReports?.results || visitReports?.data || visitReports || [],
          labReports: labReports?.results || labReports?.data || labReports || [],
          supplierReports: supplierReports?.results || supplierReports?.data || supplierReports || [],
        };
      } catch (error) {
        console.error('Error fetching all documents:', error);
        return {
          visitReports: [],
          labReports: [],
          supplierReports: [],
        };
      }
    },
    onError: (error) => {
      console.error('Error in allDocuments query:', error);
    }
  });

  // Combinar todos los documentos
  const allDocumentsList = useMemo(() => {
    if (!allDocuments) return [];
    
    const documents = [];
    
    // Agregar reportes de visita
    allDocuments.visitReports.forEach(report => {
      documents.push({
        ...report,
        type: 'visit-report',
        typeName: 'Reporte de Visita',
        typeIcon: ClipboardDocumentListIcon,
        typeColor: 'blue',
        incidentCode: report.related_incident?.code,
        clientName: report.related_incident?.cliente || report.client_name,
        provider: report.related_incident?.provider,
        product: report.related_incident?.sku,
        description: report.related_incident?.descripcion,
      });
    });
    
    // Agregar reportes de laboratorio
    allDocuments.labReports.forEach(report => {
      documents.push({
        ...report,
        type: 'lab-report',
        typeName: 'Reporte de Laboratorio',
        typeIcon: BeakerIcon,
        typeColor: 'purple',
        incidentCode: report.related_incident?.code,
        clientName: report.related_incident?.cliente || report.client,
        provider: report.related_incident?.provider,
        product: report.related_incident?.sku,
        description: report.related_incident?.descripcion,
      });
    });
    
    // Agregar reportes de proveedores
    allDocuments.supplierReports.forEach(report => {
      documents.push({
        ...report,
        type: 'supplier-report',
        typeName: 'Reporte de Proveedor',
        typeIcon: TruckIcon,
        typeColor: 'green',
        incidentCode: report.related_incident?.code,
        clientName: report.related_incident?.cliente,
        provider: report.related_incident?.provider,
        product: report.related_incident?.sku,
        description: report.related_incident?.descripcion,
      });
    });
    
    return documents;
  }, [allDocuments]);

  // Filtrar documentos por búsqueda
  const filteredDocuments = useMemo(() => {
    if (!searchTerm) return allDocumentsList;
    
    const term = searchTerm.toLowerCase();
    return allDocumentsList.filter(doc => 
      doc.report_number?.toLowerCase().includes(term) ||
      doc.incidentCode?.toLowerCase().includes(term) ||
      doc.clientName?.toLowerCase().includes(term) ||
      doc.provider?.toLowerCase().includes(term) ||
      doc.product?.toLowerCase().includes(term) ||
      doc.description?.toLowerCase().includes(term) ||
      doc.typeName?.toLowerCase().includes(term)
    );
  }, [allDocumentsList, searchTerm]);

  // Agrupar documentos por incidencia
  const documentsByIncident = useMemo(() => {
    const grouped = {};
    filteredDocuments.forEach(doc => {
      const incidentCode = doc.incidentCode || 'Sin Incidencia';
      if (!grouped[incidentCode]) {
        grouped[incidentCode] = {
          incidentCode,
          clientName: doc.clientName,
          provider: doc.provider,
          documents: []
        };
      }
      grouped[incidentCode].documents.push(doc);
    });
    return grouped;
  }, [filteredDocuments]);

  const handleOpenDocument = (document) => {
    console.log('=== OPENING DOCUMENT FROM TRACEABILITY ===');
    console.log('Document:', document);
    
    const incidentId = document.related_incident?.id || document.related_incident;
    
    // Intentar abrir archivo específico si está disponible
    if (document.pdf_path || document.document_path) {
      const specificFile = document.pdf_path || document.document_path;
      const fileUrl = `file:///${specificFile.replace(/\\/g, '/')}`;
      console.log('Trying specific file URL:', fileUrl);
      window.open(fileUrl, '_blank');
      return;
    }
    
    // Usar la URL de descarga del documento si está disponible
    if (document.download_url) {
      const apiUrl = `http://localhost:8000${document.download_url}`;
      console.log('Using API URL:', apiUrl);
      window.open(apiUrl, '_blank');
    } else {
      console.log('No download URL available for document');
      alert('No hay documento disponible para este reporte');
    }
  };

  const handleEditDocument = (document) => {
    let editUrl = '';
    if (document.type === 'visit-report') {
      editUrl = `/visit-reports/${document.id}/edit`;
    } else if (document.type === 'lab-report') {
      editUrl = `/lab-reports/${document.id}/edit`;
    } else if (document.type === 'supplier-report') {
      editUrl = `/supplier-reports/${document.id}/edit`;
    }
    window.open(editUrl, '_blank');
  };

  const handleDeleteDocument = (document) => {
    if (confirm(`¿Estás seguro de que quieres eliminar ${document.typeName} ${document.report_number}?`)) {
      console.log('Eliminar documento:', document.id);
    }
  };

  const handleViewIncident = (incidentCode) => {
    const incident = incidents?.results?.find(inc => inc.code === incidentCode);
    if (incident) {
      window.open(`/incidents/${incident.id}`, '_blank');
    }
  };

  if (incidentsLoading || documentsLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con búsqueda */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Trazabilidad Documental</h2>
          <div className="text-sm text-gray-600">
            {filteredDocuments.length} documentos encontrados
          </div>
        </div>
        
        {/* Búsqueda */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar por código, cliente, proveedor, producto, descripción..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Lista de documentos agrupados por incidencia */}
      <div className="space-y-6">
        {Object.entries(documentsByIncident).map(([incidentCode, incidentData]) => (
          <div key={incidentCode} className="bg-white rounded-lg shadow">
            {/* Header de la incidencia */}
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <ExclamationTriangleIcon className="h-8 w-8 text-orange-600" />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {incidentCode}
                    </h3>
                    <div className="text-sm text-gray-600">
                      Cliente: {incidentData.clientName || 'N/A'} • 
                      Proveedor: {incidentData.provider || 'N/A'}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleViewIncident(incidentCode)}
                    className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                  >
                    Ver Incidencia
                  </button>
                  <span className="text-sm text-gray-500">
                    {incidentData.documents.length} documentos
                  </span>
                </div>
              </div>
            </div>

            {/* Documentos de la incidencia */}
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {incidentData.documents.map((document) => {
                  const IconComponent = document.typeIcon;
                  const colorClasses = {
                    blue: 'bg-blue-50 text-blue-700 border-blue-200',
                    purple: 'bg-purple-50 text-purple-700 border-purple-200',
                    green: 'bg-green-50 text-green-700 border-green-200',
                  };
                  
                  return (
                    <div key={`${document.type}-${document.id}`} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <IconComponent className={`h-5 w-5 text-${document.typeColor}-600`} />
                          <span className="text-sm font-medium text-gray-900">
                            {document.report_number || `${document.type.toUpperCase()}-${document.id}`}
                          </span>
                        </div>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colorClasses[document.typeColor]}`}>
                          {document.typeName}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 mb-3">
                        <div>Cliente: {document.clientName || 'N/A'}</div>
                        <div>Producto: {document.product || 'N/A'}</div>
                        <div>Fecha: {new Date(document.created_at || document.visit_date || document.request_date || document.report_date).toLocaleDateString()}</div>
                      </div>
                      
                      {/* Botones de acción */}
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleOpenDocument(document)}
                          className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          title="Ver documento"
                        >
                          <EyeIcon className="h-4 w-4 mr-2" />
                          Ver
                        </button>
                        <button
                          onClick={() => handleEditDocument(document)}
                          className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          title="Editar documento"
                        >
                          <PencilIcon className="h-4 w-4 mr-2" />
                          Editar
                        </button>
                        <button
                          onClick={() => handleDeleteDocument(document)}
                          className="inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          title="Eliminar documento"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Mensaje si no hay documentos */}
      {filteredDocuments.length === 0 && (
        <div className="text-center py-12">
          <DocumentArrowDownIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No hay documentos</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'No se encontraron documentos que coincidan con tu búsqueda.' : 'No hay documentos registrados en el sistema.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default TraceabilityOverview;
