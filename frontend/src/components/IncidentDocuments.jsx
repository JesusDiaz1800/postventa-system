import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
<<<<<<< HEAD
import { api } from '../services/api';
import {
  EyeIcon,
  DocumentArrowDownIcon,
  ClipboardDocumentListIcon,
  BeakerIcon,
  TruckIcon,
} from '@heroicons/react/24/outline';

const IncidentDocuments = ({ incidentId, incidentCode }) => {
  const [selectedDocumentType, setSelectedDocumentType] = useState('all');

  // Query para obtener todos los documentos de la incidencia
  const { data: documents, isLoading, error } = useQuery({
    queryKey: ['incidentDocuments', incidentId],
    queryFn: () => api.get(`/documents/incident/${incidentId}/documents/`).then(res => res.data),
    enabled: !!incidentId
  });

  const handleOpenDocument = (document) => {
    const apiUrl = document.download_url;
    window.open(apiUrl, '_blank');
  };

  const handleGeneratePDF = async (documentType, documentId) => {
    const { API_ORIGIN } = await import('../services/api');
    const generateUrl = `${API_ORIGIN}/api/documents/generate/${documentType}/${documentId}/`;
    window.open(generateUrl, '_blank');
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
=======
import {
  DocumentIcon,
  DocumentArrowDownIcon,
  PaperClipIcon,
  EyeIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

const IncidentDocuments = ({ incidentId, onDownloadSuccess, onDownloadError }) => {
  const [selectedDocument, setSelectedDocument] = useState(null);

  // Query para obtener todos los documentos de una incidencia
  const { data: documentsData, isLoading: documentsLoading, refetch } = useQuery({
    queryKey: ['incident-documents', incidentId],
    queryFn: async () => {
      if (!incidentId) return null;
      
      try {
        const [documentsRes, visitReportsRes, qualityReportsRes, supplierReportsRes, labReportsRes] = await Promise.all([
          fetch(`/api/documents/?incident_id=${incidentId}`),
          fetch(`/api/documents/visit-reports/?incident_id=${incidentId}`),
          fetch(`/api/documents/quality-reports/?incident_id=${incidentId}`),
          fetch(`/api/documents/supplier-reports/?incident_id=${incidentId}`),
          fetch(`/api/documents/lab-reports/?incident_id=${incidentId}`)
        ]);

        const [documents, visitReports, qualityReports, supplierReports, labReports] = await Promise.all([
          documentsRes.ok ? documentsRes.json() : { results: [] },
          visitReportsRes.ok ? visitReportsRes.json() : { results: [] },
          qualityReportsRes.ok ? qualityReportsRes.json() : { results: [] },
          supplierReportsRes.ok ? supplierReportsRes.json() : { results: [] },
          labReportsRes.ok ? labReportsRes.json() : { results: [] }
        ]);

        // Combinar todos los documentos con su tipo
        const allDocs = [
          ...(documents.results || documents.data || documents || []).map(doc => ({ 
            ...doc, 
            type: 'document', 
            typeLabel: 'Documento',
            typeColor: 'bg-blue-100 text-blue-800'
          })),
          ...(visitReports.results || visitReports.data || visitReports || []).map(doc => ({ 
            ...doc, 
            type: 'visit_report', 
            typeLabel: 'Reporte de Visita',
            typeColor: 'bg-green-100 text-green-800'
          })),
          ...(qualityReports.results || qualityReports.data || qualityReports || []).map(doc => ({ 
            ...doc, 
            type: 'quality_report', 
            typeLabel: 'Reporte de Calidad',
            typeColor: 'bg-yellow-100 text-yellow-800'
          })),
          ...(supplierReports.results || supplierReports.data || supplierReports || []).map(doc => ({ 
            ...doc, 
            type: 'supplier_report', 
            typeLabel: 'Reporte de Proveedor',
            typeColor: 'bg-purple-100 text-purple-800'
          })),
          ...(labReports.results || labReports.data || labReports || []).map(doc => ({ 
            ...doc, 
            type: 'lab_report', 
            typeLabel: 'Reporte de Laboratorio',
            typeColor: 'bg-red-100 text-red-800'
          }))
        ];

        return allDocs;
      } catch (error) {
        console.error('Error loading documents:', error);
        return [];
      }
    },
    enabled: !!incidentId,
    staleTime: 30000, // 30 segundos
  });

  const documents = documentsData || [];

  const downloadDocument = async (document) => {
    try {
      const response = await fetch(`/api/documents/${document.id}/download/`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = document.title || document.name || `documento_${document.id}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        if (onDownloadSuccess) {
          onDownloadSuccess(`Documento ${document.title || document.name} descargado exitosamente`);
        }
      } else {
        throw new Error('Error al descargar el documento');
      }
    } catch (error) {
      console.error('Download error:', error);
      if (onDownloadError) {
        onDownloadError(`Error al descargar el documento: ${error.message}`);
      }
    }
  };

  const viewDocument = (document) => {
    setSelectedDocument(document);
    // Aquí podrías implementar un visor de documentos
    console.log('View document:', document);
  };

  if (documentsLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <ArrowPathIcon className="h-5 w-5 animate-spin text-blue-600 mr-2" />
        <span className="text-sm text-gray-600">Cargando documentos...</span>
>>>>>>> 674c244 (tus cambios)
      </div>
    );
  }

<<<<<<< HEAD
  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error cargando documentos</p>
=======
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-gray-500">
        <PaperClipIcon className="h-12 w-12 mb-4" />
        <p className="text-sm">No hay documentos adjuntos para esta incidencia</p>
>>>>>>> 674c244 (tus cambios)
      </div>
    );
  }

<<<<<<< HEAD
  const allDocuments = documents?.documents || [];

  const filteredDocuments = selectedDocumentType === 'all' 
    ? allDocuments 
    : allDocuments.filter(doc => doc.type === selectedDocumentType);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            Documentos de la Incidencia {incidentCode}
          </h3>
          <p className="text-sm text-gray-600">
            Total: {allDocuments.length} documentos
          </p>
        </div>
        
        {/* Filtro por tipo */}
        <select
          value={selectedDocumentType}
          onChange={(e) => setSelectedDocumentType(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="all">Todos los Documentos</option>
          <option value="visit-report">Reportes de Visita</option>
          <option value="lab-report">Reportes de Laboratorio</option>
          <option value="supplier-report">Reportes de Proveedor</option>
        </select>
      </div>

      {/* Lista de documentos */}
      {filteredDocuments.length === 0 ? (
        <div className="text-center py-12">
          <DocumentArrowDownIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No hay documentos</h3>
          <p className="mt-1 text-sm text-gray-500">
            No se encontraron documentos para esta incidencia.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map((document) => (
            <div key={`${document.type}-${document.id}`} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    {document.type === 'visit-report' && (
                      <ClipboardDocumentListIcon className="h-5 w-5 text-blue-600" />
                    )}
                    {document.type === 'lab-report' && (
                      <BeakerIcon className="h-5 w-5 text-purple-600" />
                    )}
                    {document.type === 'supplier-report' && (
                      <TruckIcon className="h-5 w-5 text-green-600" />
                    )}
                    <span className="text-sm font-medium text-gray-900">
                      {document.report_number || `${document.type.toUpperCase()}-${document.id}`}
                    </span>
                  </div>
                  
                  <div className="text-xs text-gray-500 mb-2">
                    {document.type_name}
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    {document.size_human} • {new Date(document.modified_at * 1000).toLocaleDateString()}
                  </div>
                  
                  {document.status && (
                    <div className="mt-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        document.status === 'completed' ? 'bg-green-100 text-green-800' :
                        document.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {document.status}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="mt-4 flex space-x-2">
                <button
                  onClick={() => handleOpenDocument(document)}
                  className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <EyeIcon className="h-4 w-4 mr-2" />
                  Ver
                </button>
                <button
                  onClick={() => handleGeneratePDF(document.type, document.id)}
                  className="flex-1 inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
                  PDF
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
=======
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-900">
          Documentos Adjuntos ({documents.length})
        </h4>
        <button
          onClick={() => refetch()}
          className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
        >
          <ArrowPathIcon className="h-3 w-3 mr-1" />
          Actualizar
        </button>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {documents.map((doc, index) => (
          <div key={doc.id || index} className="border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <DocumentIcon className="h-4 w-4 text-gray-500 flex-shrink-0" />
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {doc.title || doc.name || `Documento ${index + 1}`}
                  </p>
                </div>
                
                <div className="flex items-center gap-2 mb-2">
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${doc.typeColor}`}>
                    {doc.typeLabel}
                  </span>
                  {doc.created_at && (
                    <span className="text-xs text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  )}
                </div>

                {doc.description && (
                  <p className="text-xs text-gray-600 line-clamp-2">
                    {doc.description}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-1 ml-3">
                <button
                  onClick={() => viewDocument(doc)}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Ver documento"
                >
                  <EyeIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => downloadDocument(doc)}
                  className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Descargar documento"
                >
                  <DocumentArrowDownIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
>>>>>>> 674c244 (tus cambios)
    </div>
  );
};

<<<<<<< HEAD
export default IncidentDocuments;
=======
export default IncidentDocuments;
>>>>>>> 674c244 (tus cambios)
