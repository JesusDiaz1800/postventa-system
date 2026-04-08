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
  TagIcon,
  DocumentIcon,
  PhotoIcon,
  VideoCameraIcon,
  SpeakerWaveIcon,
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
  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'image':
        return <PhotoIcon className="h-6 w-6 text-green-500" />;
      case 'video':
        return <VideoCameraIcon className="h-6 w-6 text-blue-500" />;
      case 'audio':
        return <SpeakerWaveIcon className="h-6 w-6 text-purple-500" />;
      case 'visit_report':
        return <DocumentTextIcon className="h-6 w-6 text-blue-600" />;
      case 'lab_report':
        return <DocumentTextIcon className="h-6 w-6 text-green-600" />;
      case 'supplier_report':
        return <DocumentTextIcon className="h-6 w-6 text-purple-600" />;
      case 'quality_report':
        return <DocumentTextIcon className="h-6 w-6 text-orange-600" />;
      default:
        return <DocumentIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'abierto': return 'bg-green-500';
      case 'cerrado': return 'bg-gray-500';
      case 'en_proceso': return 'bg-yellow-500';
      case 'laboratorio': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusTextColor = (status) => {
    switch (status) {
      case 'abierto': return 'text-green-700 bg-green-100';
      case 'cerrado': return 'text-gray-700 bg-gray-100';
      case 'en_proceso': return 'text-yellow-700 bg-yellow-100';
      case 'laboratorio': return 'text-purple-700 bg-purple-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const truncateText = (text, maxLength = 30) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header de la incidencia mejorado */}
      <div className="px-6 py-5 bg-gradient-to-r from-blue-600 to-blue-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`w-4 h-4 rounded-full ${getStatusColor(incident.estado)} shadow-sm`}></div>
            <div>
              <h3 className="text-xl font-bold text-white">
                {incident.code}
              </h3>
              <p className="text-blue-100 text-sm mt-1">
                {truncateText(incident.cliente, 40)}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusTextColor(incident.estado)} shadow-sm`}>
              {incident.estado.replace('_', ' ').toUpperCase()}
            </span>
            <span className="text-blue-100 text-sm">
              {documents.length} documento{documents.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>
      </div>

      {/* Contenido de documentos */}
      <div className={viewMode === 'grid' ? 'document-grid p-6' : 'divide-y divide-gray-200'}>
        {documents.map((document) => {
          const documentId = document.id || `${document.type}-${document.incident_id}-${document.filename}`;
          const isSelected = selectedDocuments.includes(documentId);

          return (
            <div
              key={documentId}
              className={`${
                viewMode === 'grid'
                  ? 'group relative border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all duration-200 hover:border-blue-300 bg-white document-card'
                  : 'p-4 hover:bg-gray-50 transition-colors'
              } ${isSelected ? 'ring-2 ring-blue-500 bg-blue-50 border-blue-300' : ''}`}
            >
              {/* Checkbox */}
              <div className="absolute top-3 left-3 z-10">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggleSelection(documentId)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded shadow-sm"
                />
              </div>

              {viewMode === 'grid' ? (
                // Vista en cuadrícula mejorada
                <div className="space-y-3">
                  {/* Icono y tipo */}
                  <div className="flex items-center justify-center pt-2">
                    <div className="p-3 rounded-xl bg-gray-50 group-hover:bg-blue-50 transition-colors">
                      {getFileIcon(document.type)}
                    </div>
                  </div>

                  {/* Título truncado */}
                  <div className="text-center">
                    <h4 className="text-sm font-semibold text-gray-900 line-clamp-2 leading-tight">
                      {truncateText(document.filename || document.title, 25)}
                    </h4>
                  </div>

                  {/* Información del documento */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-center text-xs text-gray-500">
                      <TagIcon className="h-3 w-3 mr-1" />
                      <span className="truncate">
                        {document.document_type_display || document.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                    
                    {document.created_at && (
                      <div className="flex items-center justify-center text-xs text-gray-500">
                        <CalendarIcon className="h-3 w-3 mr-1" />
                        <span>{new Date(document.created_at).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>

                  {/* Botones de acción */}
                  <div className="flex items-center justify-center space-x-2 pt-2">
                    <button
                      onClick={() => onViewDocument(document)}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
                      title="Ver documento"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => onDownloadDocument(document)}
                      className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all duration-200"
                      title="Descargar documento"
                    >
                      <ArrowDownTrayIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => onDeleteDocument(document)}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
                      title="Eliminar documento"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ) : (
                // Vista en lista
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        {getFileIcon(document.type)}
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {document.filename || document.title}
                        </h4>
                      </div>
                      <div className="mt-2 space-y-1">
                        <div className="flex items-center text-xs text-gray-500">
                          <TagIcon className="h-4 w-4 mr-1" />
                          {document.document_type_display || document.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </div>
                        {document.created_by?.username && (
                          <div className="flex items-center text-xs text-gray-500">
                            <UserIcon className="h-4 w-4 mr-1" />
                            {document.created_by.first_name} {document.created_by.last_name} ({document.created_by.username})
                          </div>
                        )}
                        {document.created_at && (
                          <div className="flex items-center text-xs text-gray-500">
                            <CalendarIcon className="h-4 w-4 mr-1" />
                            {new Date(document.created_at).toLocaleDateString()}
                          </div>
                        )}
                        {document.size_human && (
                          <div className="flex items-center text-xs text-gray-500">
                            <ClockIcon className="h-4 w-4 mr-1" />
                            {document.size_human}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => onViewDocument(document)}
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      title="Ver documento"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => onDownloadDocument(document)}
                      className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                      title="Descargar documento"
                    >
                      <ArrowDownTrayIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => onDeleteDocument(document)}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      title="Eliminar documento"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DocumentsByIncident;