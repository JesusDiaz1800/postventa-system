import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
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
        const [documentsRes, visitReportsRes, qualityReportsRes, supplierReportsRes, labReportsRes, attachmentsRes] = await Promise.all([
          fetch(`/api/documents/?incident_id=${incidentId}`),
          fetch(`/api/documents/visit-reports/?incident_id=${incidentId}`),
          fetch(`/api/documents/quality-reports/?incident_id=${incidentId}`),
          fetch(`/api/documents/supplier-reports/?incident_id=${incidentId}`),
          fetch(`/api/documents/lab-reports/?incident_id=${incidentId}`),
          fetch(`/api/documents/attachments/incident/${incidentId}/`)  // ← ENDPOINT CORRECTO
        ]);

        const [documents, visitReports, qualityReports, supplierReports, labReports, attachments] = await Promise.all([
          documentsRes.ok ? documentsRes.json() : { results: [] },
          visitReportsRes.ok ? visitReportsRes.json() : { results: [] },
          qualityReportsRes.ok ? qualityReportsRes.json() : { results: [] },
          supplierReportsRes.ok ? supplierReportsRes.json() : { results: [] },
          labReportsRes.ok ? labReportsRes.json() : { results: [] },
          attachmentsRes.ok ? attachmentsRes.json() : { attachments: [] }
        ]);

        // DEBUG: Ver qué attachments se están cargando
        console.log('🔍 Attachments cargados para incidencia', incidentId, ':', attachments);

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
          })),
          // NUEVO: Agregar archivos adjuntos (DocumentAttachment)
          ...(attachments.attachments || []).map(att => ({
            ...att,
            id: `attachment-${att.id}`,
            type: 'attachment',
            typeLabel: att.document_type_display || 'Archivo Adjunto',
            typeColor: 'bg-orange-100 text-orange-800',
            title: att.filename,
            name: att.filename,
            description: att.description,
            created_at: att.uploaded_at
          }))
        ];

        console.log('📄 Total documentos combinados:', allDocs.length);
        console.log('📎 Attachments en la lista:', allDocs.filter(d => d.type === 'attachment').length);

        return allDocs;
      } catch (error) {
        console.error('Error loading documents:', error);
        return [];
      }
    },
    enabled: !!incidentId,
    // Eliminar staleTime para evitar cache
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
    // console.log('View document:', document);
  };

  if (documentsLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <ArrowPathIcon className="h-5 w-5 animate-spin text-blue-600 mr-2" />
        <span className="text-sm text-gray-600">Cargando documentos...</span>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-gray-500">
        <PaperClipIcon className="h-12 w-12 mb-4" />
        <p className="text-sm">No hay documentos adjuntos para esta incidencia</p>
      </div>
    );
  }

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
    </div>
  );
};

export default IncidentDocuments;
