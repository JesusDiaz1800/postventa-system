import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { documentsAPI } from '../services/api';
import { brandConfig } from '../config/brand';
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  PencilIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  EyeIcon,
  ClockIcon,
  UserIcon,
  TagIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const DocumentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('content');

  const { data: document, isLoading, error } = useQuery({
    queryKey: ['document', id],
    queryFn: () => documentsAPI.get(id),
  });

  const getStatusBadge = (status) => {
    const statusClasses = {
      draft: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      generated: 'bg-green-100 text-green-800 border-green-200',
      sent: 'bg-blue-100 text-blue-800 border-blue-200',
      archived: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    
    const statusNames = {
      draft: 'Borrador',
      generated: 'Generado',
      sent: 'Enviado',
      archived: 'Archivado',
    };
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${statusClasses[status] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {statusNames[status] || status}
      </span>
    );
  };

  const getTemplateBadge = (templateType) => {
    const templateClasses = {
      cliente_informe: 'bg-blue-100 text-blue-800 border-blue-200',
      proveedor_carta: 'bg-orange-100 text-orange-800 border-orange-200',
      lab_report: 'bg-purple-100 text-purple-800 border-purple-200',
    };
    
    const templateNames = {
      cliente_informe: 'Informe Cliente',
      proveedor_carta: 'Carta Proveedor',
      lab_report: 'Reporte Lab',
    };
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${templateClasses[templateType] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {templateNames[templateType] || templateType}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error al cargar el documento</p>
        <button
          onClick={() => navigate('/documents')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Volver a Documentos
        </button>
      </div>
    );
  }

  const tabs = [
    { id: 'content', name: 'Contenido', icon: DocumentTextIcon },
    { id: 'versions', name: 'Versiones', icon: ClockIcon },
    { id: 'history', name: 'Historial', icon: UserIcon },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-indigo-600/10 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/documents')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-white/60 rounded-lg transition-all duration-200"
              >
                <ArrowLeftIcon className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  {document.title || `Documento ${document.id}`}
                </h1>
                <p className="mt-2 text-lg text-gray-600">
                  {getTemplateBadge(document.template_type)} • {getStatusBadge(document.status)}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200">
                <PencilIcon className="h-4 w-4 mr-2" />
                Editar
              </button>
              <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-200">
                <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
                Descargar PDF
              </button>
              <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-green-600 hover:bg-green-700 transition-colors duration-200">
                <ShareIcon className="h-4 w-4 mr-2" />
                Compartir
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-purple-600/5 to-indigo-600/5 rounded-3xl blur-3xl"></div>
        <div className="relative bg-white/90 backdrop-blur-sm rounded-2xl border border-white/20 shadow-xl">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.name}</span>
                  </div>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'content' && (
              <div className="space-y-6">
                {/* Document Information */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Información del Documento</h3>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <TagIcon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-500">Tipo</p>
                          <p className="font-medium text-gray-900">{getTemplateBadge(document.template_type)}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <UserIcon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-500">Creado por</p>
                          <p className="font-medium text-gray-900">{document.created_by?.username || 'Sistema'}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <ClockIcon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-500">Fecha de creación</p>
                          <p className="font-medium text-gray-900">
                            {new Date(document.created_at).toLocaleDateString('es-ES')}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="md:col-span-2 bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Contenido del Documento</h3>
                    <div className="prose max-w-none">
                      <div className="bg-white rounded-lg p-6 border border-gray-200">
                        {document.content ? (
                          <div dangerouslySetInnerHTML={{ __html: document.content }} />
                        ) : (
                          <p className="text-gray-500 italic">No hay contenido disponible.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'versions' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Versiones del Documento</h3>
                <div className="bg-gray-50 rounded-xl p-6">
                  <p className="text-gray-600">Sistema de versiones en desarrollo...</p>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Historial de Cambios</h3>
                <div className="bg-gray-50 rounded-xl p-6">
                  <p className="text-gray-600">Historial de cambios en desarrollo...</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentDetail;
