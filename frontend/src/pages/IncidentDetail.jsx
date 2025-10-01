import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { incidentsAPI } from '../services/api';
import { brandConfig } from '../config/brand';
import IncidentAttachments from '../components/IncidentAttachments';
import {
  ArrowLeftIcon,
  ExclamationTriangleIcon,
  UserIcon,
  BuildingOffice2Icon,
  CalendarIcon,
  ClockIcon,
  TagIcon,
  DocumentTextIcon,
  PhotoIcon,
  PencilIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  ShareIcon,
  PaperClipIcon,
} from '@heroicons/react/24/outline';

const IncidentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');

  const { data: incident, isLoading, error } = useQuery({
    queryKey: ['incident', id],
    queryFn: () => incidentsAPI.get(id),
  });

  const getStatusBadge = (estado) => {
    const statusClasses = {
      abierto: 'bg-blue-100 text-blue-800 border-blue-200',
      triage: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      inspeccion: 'bg-orange-100 text-orange-800 border-orange-200',
      laboratorio: 'bg-purple-100 text-purple-800 border-purple-200',
      propuesta: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      en_progreso: 'bg-cyan-100 text-cyan-800 border-cyan-200',
      cerrado: 'bg-green-100 text-green-800 border-green-200',
    };
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${statusClasses[estado] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {estado}
      </span>
    );
  };

  const getPriorityBadge = (prioridad) => {
    const priorityClasses = {
      baja: 'bg-gray-100 text-gray-800 border-gray-200',
      media: 'bg-blue-100 text-blue-800 border-blue-200',
      alta: 'bg-orange-100 text-orange-800 border-orange-200',
      critica: 'bg-red-100 text-red-800 border-red-200',
    };
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border ${priorityClasses[prioridad] || 'bg-gray-100 text-gray-800 border-gray-200'}`}>
        {prioridad}
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

  if (error || !incident) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error al cargar la incidencia</p>
        <button
          onClick={() => navigate('/incidents')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Volver a Incidencias
        </button>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Resumen', icon: EyeIcon },
    { id: 'timeline', name: 'Timeline', icon: ClockIcon },
    { id: 'documents', name: 'Documentos', icon: DocumentTextIcon },
    { id: 'images', name: 'Imágenes', icon: PhotoIcon },
    { id: 'attachments', name: 'Adjuntos', icon: PaperClipIcon },
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
                onClick={() => navigate('/incidents')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-white/60 rounded-lg transition-all duration-200"
              >
                <ArrowLeftIcon className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  {incident.code}
                </h1>
                <p className="mt-2 text-lg text-gray-600">
                  {incident.cliente} • {incident.provider}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {getStatusBadge(incident.estado)}
              {getPriorityBadge(incident.prioridad)}
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
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Incident Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Información General</h3>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <UserIcon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-500">Cliente</p>
                          <p className="font-medium text-gray-900">{incident.cliente}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <BuildingOffice2Icon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-500">Proveedor</p>
                          <p className="font-medium text-gray-900">{incident.provider}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <TagIcon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-500">SKU</p>
                          <p className="font-medium text-gray-900">{incident.sku}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CalendarIcon className="h-5 w-5 text-gray-400" />
                        <div>
                          <p className="text-sm text-gray-500">Fecha de Creación</p>
                          <p className="font-medium text-gray-900">
                            {new Date(incident.created_at).toLocaleDateString('es-ES')}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Descripción</h3>
                    <p className="text-gray-700 leading-relaxed">
                      {incident.descripcion || 'No hay descripción disponible.'}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between bg-gray-50 rounded-xl p-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Acciones</h3>
                    <p className="text-gray-600">Gestiona esta incidencia</p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200">
                      <PencilIcon className="h-4 w-4 mr-2" />
                      Editar
                    </button>
                    <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-200">
                      <ShareIcon className="h-4 w-4 mr-2" />
                      Compartir
                    </button>
                    <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-green-600 hover:bg-green-700 transition-colors duration-200">
                      <CheckCircleIcon className="h-4 w-4 mr-2" />
                      Resolver
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'timeline' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Timeline de Actividades</h3>
                <div className="bg-gray-50 rounded-xl p-6">
                  <p className="text-gray-600">Timeline de actividades en desarrollo...</p>
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Documentos Relacionados</h3>
                <div className="bg-gray-50 rounded-xl p-6">
                  <p className="text-gray-600">Documentos relacionados en desarrollo...</p>
                </div>
              </div>
            )}

            {activeTab === 'images' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Imágenes y Análisis</h3>
                <div className="bg-gray-50 rounded-xl p-6">
                  <p className="text-gray-600">Imágenes y análisis en desarrollo...</p>
                </div>
              </div>
            )}

            {activeTab === 'attachments' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Adjuntos de la Incidencia</h3>
                <IncidentAttachments incidentId={parseInt(id)} incidentCode={incident?.code} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IncidentDetail;
