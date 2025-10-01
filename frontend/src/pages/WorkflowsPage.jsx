import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import ErrorBoundary from '../components/ErrorBoundary';
import {
  DocumentDuplicateIcon,
  PlusIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  BeakerIcon,
  TruckIcon,
} from '@heroicons/react/24/outline';

const WorkflowsPage = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);

  const workflows = [
    {
      id: 'incident-management',
      name: 'Gestión de Incidencias',
      description: 'Flujo completo desde la creación hasta la resolución de incidencias',
      icon: ExclamationTriangleIcon,
      color: 'red',
      steps: [
        { name: 'Crear Incidencia', status: 'completed', href: '/incidents/new' },
        { name: 'Asignar Responsable', status: 'pending', href: '/incidents' },
        { name: 'Visita Técnica', status: 'pending', href: '/documents' },
        { name: 'Análisis de Laboratorio', status: 'pending', href: '/documents' },
        { name: 'Informe al Proveedor', status: 'pending', href: '/documents' },
        { name: 'Resolución', status: 'pending', href: '/incidents' },
      ]
    },
    {
      id: 'document-traceability',
      name: 'Trazabilidad Documental',
      description: 'Seguimiento completo de documentos desde la incidencia hasta el proveedor',
      icon: DocumentTextIcon,
      color: 'blue',
      steps: [
        { name: 'Reporte de Visita', status: 'completed', href: '/documents' },
        { name: 'Informe de Laboratorio', status: 'pending', href: '/documents' },
        { name: 'Informe para Proveedor', status: 'pending', href: '/documents' },
        { name: 'Generación de PDFs', status: 'pending', href: '/documents' },
        { name: 'Archivo y Seguimiento', status: 'pending', href: '/documents' },
      ]
    },
    {
      id: 'quality-control',
      name: 'Control de Calidad',
      description: 'Proceso de análisis y control de calidad de productos',
      icon: BeakerIcon,
      color: 'green',
      steps: [
        { name: 'Recepción de Muestra', status: 'completed', href: '/incidents/new' },
        { name: 'Análisis Inicial', status: 'pending', href: '/ai' },
        { name: 'Pruebas de Laboratorio', status: 'pending', href: '/documents' },
        { name: 'Evaluación de Resultados', status: 'pending', href: '/ai' },
        { name: 'Informe Final', status: 'pending', href: '/documents' },
      ]
    },
    {
      id: 'supplier-communication',
      name: 'Comunicación con Proveedores',
      description: 'Gestión de comunicaciones y reportes técnicos a proveedores',
      icon: TruckIcon,
      color: 'purple',
      steps: [
        { name: 'Identificación del Problema', status: 'completed', href: '/incidents' },
        { name: 'Recopilación de Evidencias', status: 'pending', href: '/incidents' },
        { name: 'Análisis Técnico', status: 'pending', href: '/ai' },
        { name: 'Redacción del Informe', status: 'pending', href: '/documents' },
        { name: 'Envío al Proveedor', status: 'pending', href: '/documents' },
        { name: 'Seguimiento de Respuesta', status: 'pending', href: '/incidents' },
      ]
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
      case 'in-progress':
        return <ExclamationTriangleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'in-progress':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getWorkflowColor = (color) => {
    switch (color) {
      case 'red':
        return 'from-red-500 to-red-600';
      case 'blue':
        return 'from-blue-500 to-blue-600';
      case 'green':
        return 'from-green-500 to-green-600';
      case 'purple':
        return 'from-purple-500 to-purple-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        <PageHeader
          title="Workflows"
          subtitle="Gestión de procesos y flujos de trabajo"
          icon={DocumentDuplicateIcon}
          showLogo={true}
        >
          <Link
            to="/incidents/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Nueva Incidencia
          </Link>
        </PageHeader>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {workflows.map((workflow) => (
          <div
            key={workflow.id}
            className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300"
          >
            {/* Header */}
            <div className={`bg-gradient-to-r ${getWorkflowColor(workflow.color)} p-6`}>
              <div className="flex items-center space-x-3">
                <workflow.icon className="h-8 w-8 text-white" />
                <div>
                  <h3 className="text-lg font-semibold text-white">{workflow.name}</h3>
                  <p className="text-white/80 text-sm">{workflow.description}</p>
                </div>
              </div>
            </div>

            {/* Steps */}
            <div className="p-6">
              <div className="space-y-3">
                {workflow.steps.map((step, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {getStatusIcon(step.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${getStatusColor(step.status)} px-3 py-1 rounded-full border inline-block`}>
                        {step.name}
                      </p>
                    </div>
                    {step.href && (
                      <Link
                        to={step.href}
                        className="flex-shrink-0 text-blue-600 hover:text-blue-800 transition-colors"
                        title="Ir a esta sección"
                      >
                        <ArrowRightIcon className="h-4 w-4" />
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">
                  {workflow.steps.filter(step => step.status === 'completed').length} de {workflow.steps.length} pasos completados
                </span>
                <Link
                  to="/documents"
                  className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Ver Documentos →
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Acciones Rápidas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/incidents/new"
            className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
          >
            <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
            <div>
              <p className="font-medium text-gray-900">Nueva Incidencia</p>
              <p className="text-sm text-gray-500">Crear nueva incidencia</p>
            </div>
          </Link>

          <Link
            to="/documents"
            className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
          >
            <ClipboardDocumentListIcon className="h-6 w-6 text-blue-500" />
            <div>
              <p className="font-medium text-gray-900">Reporte de Visita</p>
              <p className="text-sm text-gray-500">Crear reporte técnico</p>
            </div>
          </Link>

          <Link
            to="/documents"
            className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-all duration-200"
          >
            <BeakerIcon className="h-6 w-6 text-green-500" />
            <div>
              <p className="font-medium text-gray-900">Informe de Lab</p>
              <p className="text-sm text-gray-500">Crear informe de laboratorio</p>
            </div>
          </Link>

          <Link
            to="/documents"
            className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all duration-200"
          >
            <TruckIcon className="h-6 w-6 text-purple-500" />
            <div>
              <p className="font-medium text-gray-900">Informe Proveedor</p>
              <p className="text-sm text-gray-500">Crear informe para proveedor</p>
            </div>
          </Link>
        </div>
      </div>
      </div>
    </ErrorBoundary>
  );
};

export default WorkflowsPage;
