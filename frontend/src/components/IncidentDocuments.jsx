import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
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
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error cargando documentos</p>
      </div>
    );
  }

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
    </div>
  );
};

export default IncidentDocuments;
