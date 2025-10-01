import React from 'react';
import {
  DocumentTextIcon,
  EyeIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  BuildingOfficeIcon,
  CalendarIcon,
  UserIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

const DocumentsByIncident = ({ 
  incident, 
  documents, 
  viewMode, 
  selectedDocuments, 
  onToggleSelection, 
  onViewDocument, 
  onDownloadDocument, 
  onDeleteDocument 
}) => {
  const getDocumentIcon = (type) => {
    switch (type) {
      case 'visit_report':
        return <DocumentTextIcon className="h-8 w-8 text-blue-600" />;
      case 'lab_report':
        return <DocumentTextIcon className="h-8 w-8 text-green-600" />;
      case 'supplier_report':
        return <DocumentTextIcon className="h-8 w-8 text-purple-600" />;
      case 'quality_report':
        return <DocumentTextIcon className="h-8 w-8 text-orange-600" />;
      default:
        return <DocumentTextIcon className="h-8 w-8 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'abierto':
        return 'bg-green-100 text-green-800';
      case 'cerrado':
        return 'bg-gray-100 text-gray-800';
      case 'laboratorio':
        return 'bg-yellow-100 text-yellow-800';
      case 'proveedor':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'visit_report':
        return 'Reporte de Visita';
      case 'lab_report':
        return 'Reporte de Laboratorio';
      case 'supplier_report':
        return 'Reporte de Proveedor';
      case 'quality_report':
        return 'Reporte de Calidad';
      default:
        return 'Documento';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Header de la incidencia */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <BuildingOfficeIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{incident.code}</h3>
              <p className="text-sm text-gray-600">{incident.cliente}</p>
              <div className="flex items-center space-x-4 mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(incident.estado)}`}>
                  {incident.estado}
                </span>
                <span className="text-xs text-gray-500">
                  {documents.length} documento{documents.length !== 1 ? 's' : ''}
                </span>
                {incident.provider && (
                  <span className="text-xs text-gray-500">
                    Proveedor: {incident.provider}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Lista de documentos */}
      <div className="p-6">
        {documents.length === 0 ? (
          <div className="text-center py-8">
            <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-sm text-gray-500">No hay documentos para esta incidencia</p>
          </div>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-3'}>
            {documents.map((document) => {
              const documentId = document.id || `${document.type}-${incident.id}-${document.filename}`;
              const isSelected = selectedDocuments.includes(documentId);
              
              return (
                <div
                  key={documentId}
                  className={`${
                    viewMode === 'grid' 
                      ? 'border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow' 
                      : 'p-4 hover:bg-gray-50 rounded-lg border border-gray-100'
                  } ${isSelected ? 'bg-blue-50 border-blue-200' : ''}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => onToggleSelection(documentId)}
                        className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      
                      <div className="flex-shrink-0">
                        {getDocumentIcon(document.type)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <h4 className="text-sm font-medium text-gray-900 truncate">
                            {document.filename || document.title}
                          </h4>
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                            {getTypeLabel(document.type)}
                          </span>
                        </div>
                        
                        <div className="mt-2 space-y-1">
                          {document.report_number && (
                            <div className="flex items-center text-xs text-gray-500">
                              <DocumentTextIcon className="h-4 w-4 mr-1" />
                              N° {document.report_number}
                            </div>
                          )}
                          
                          {document.client_name && (
                            <div className="flex items-center text-xs text-gray-500">
                              <UserIcon className="h-4 w-4 mr-1" />
                              {document.client_name}
                            </div>
                          )}
                          
                          {document.created_at && (
                            <div className="flex items-center text-xs text-gray-500">
                              <CalendarIcon className="h-4 w-4 mr-1" />
                              {new Date(document.created_at).toLocaleDateString()}
                            </div>
                          )}
                          
                          {document.created_by && (
                            <div className="flex items-center text-xs text-gray-500">
                              <UserIcon className="h-4 w-4 mr-1" />
                              {document.created_by.username}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => onViewDocument(document)}
                        className="p-1 text-blue-600 hover:text-blue-900"
                        title="Ver documento"
                      >
                        <EyeIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onDownloadDocument(document)}
                        className="p-1 text-green-600 hover:text-green-900"
                        title="Descargar documento"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onDeleteDocument(document)}
                        className="p-1 text-red-600 hover:text-red-900"
                        title="Eliminar documento"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentsByIncident;
