import React, { useState } from 'react';
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ChartBarIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { useWorkflowDashboard, useWorkflowApprovals, useWorkflows } from '../hooks/useWorkflows';

const WorkflowDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  const { dashboard, isLoading } = useWorkflowDashboard();
  const { pendingApprovals, overdueApprovals } = useWorkflowApprovals();
  const { overdueWorkflows } = useWorkflows();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-indigo-600" />
        <span className="ml-2 text-gray-600">Cargando dashboard...</span>
      </div>
    );
  }

  const stats = dashboard?.stats || {};
  const myPendingApprovals = dashboard?.my_pending_approvals || [];
  const myActiveWorkflows = dashboard?.my_active_workflows || [];
  const recentWorkflows = dashboard?.recent_workflows || [];
  const overdueWorkflowsData = dashboard?.overdue_workflows || [];
  const upcomingDeadlines = dashboard?.upcoming_deadlines || [];

  const tabs = [
    { id: 'overview', name: 'Resumen', icon: ChartBarIcon },
    { id: 'pending', name: 'Pendientes', icon: ClockIcon },
    { id: 'active', name: 'Activos', icon: ArrowPathIcon },
    { id: 'overdue', name: 'Vencidos', icon: ExclamationTriangleIcon },
  ];

  const getStatusColor = (status) => {
    const colors = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'in_progress': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'rejected': 'bg-red-100 text-red-800',
      'cancelled': 'bg-gray-100 text-gray-800',
      'timeout': 'bg-orange-100 text-orange-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'pending': ClockIcon,
      'in_progress': ArrowPathIcon,
      'completed': CheckCircleIcon,
      'rejected': XCircleIcon,
      'cancelled': XCircleIcon,
      'timeout': ExclamationTriangleIcon,
    };
    return icons[status] || ClockIcon;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Sin fecha';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDuration = (duration) => {
    if (!duration) return 'N/A';
    // Convertir duración a formato legible
    return duration;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard de Workflows</h1>
            <p className="text-gray-600 mt-1">Gestión y seguimiento de procesos de aprobación</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">Última actualización</p>
              <p className="text-sm font-medium text-gray-900">{formatDate(new Date().toISOString())}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Workflows</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_workflows || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowPathIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Activos</p>
              <p className="text-2xl font-bold text-gray-900">{stats.active_workflows || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Pendientes de Aprobación</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pending_approvals || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Vencidos</p>
              <p className="text-2xl font-bold text-gray-900">{stats.overdue_approvals || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Tab Overview */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Estadísticas adicionales */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Completados</h3>
                  <p className="text-2xl font-bold text-green-600">{stats.completed_workflows || 0}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Rechazados</h3>
                  <p className="text-2xl font-bold text-red-600">{stats.rejected_workflows || 0}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Tiempo Promedio</h3>
                  <p className="text-2xl font-bold text-blue-600">{formatDuration(stats.average_completion_time)}</p>
                </div>
              </div>

              {/* Workflows recientes */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Workflows Recientes</h3>
                <div className="space-y-3">
                  {recentWorkflows.slice(0, 5).map((workflow) => {
                    const StatusIcon = getStatusIcon(workflow.status);
                    return (
                      <div key={workflow.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <StatusIcon className="h-5 w-5 text-gray-400" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{workflow.template?.name}</p>
                            <p className="text-xs text-gray-500">
                              {workflow.related_incident?.title || workflow.related_document?.title || 'Sin objeto relacionado'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(workflow.status)}`}>
                            {workflow.status_display}
                          </span>
                          <span className="text-xs text-gray-500">{formatDate(workflow.started_at)}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Tab Pendientes */}
          {activeTab === 'pending' && (
            <div className="space-y-4">
              {myPendingApprovals.length === 0 ? (
                <div className="text-center py-8">
                  <ClockIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No hay aprobaciones pendientes</p>
                </div>
              ) : (
                myPendingApprovals.map((approval) => (
                  <div key={approval.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-gray-900">
                          {approval.instance?.template?.name}
                        </h4>
                        <p className="text-sm text-gray-600">
                          Paso: {approval.step?.name}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Asignado: {formatDate(approval.assigned_at)}
                        </p>
                      </div>
                      <div className="flex items-center space-x-3">
                        {approval.due_date && (
                          <span className="text-xs text-gray-500">
                            Vence: {formatDate(approval.due_date)}
                          </span>
                        )}
                        <button className="bg-indigo-600 text-white px-3 py-1 rounded-md text-sm hover:bg-indigo-700">
                          Revisar
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Tab Activos */}
          {activeTab === 'active' && (
            <div className="space-y-4">
              {myActiveWorkflows.length === 0 ? (
                <div className="text-center py-8">
                  <ArrowPathIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No hay workflows activos</p>
                </div>
              ) : (
                myActiveWorkflows.map((workflow) => (
                  <div key={workflow.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-gray-900">
                          {workflow.template?.name}
                        </h4>
                        <p className="text-sm text-gray-600">
                          Paso actual: {workflow.current_step?.name}
                        </p>
                        <div className="mt-2">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-indigo-600 h-2 rounded-full" 
                              style={{ width: `${workflow.progress_percentage || 0}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {workflow.progress_percentage || 0}% completado
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-xs text-gray-500">
                          Iniciado: {formatDate(workflow.started_at)}
                        </span>
                        <button className="bg-green-600 text-white px-3 py-1 rounded-md text-sm hover:bg-green-700">
                          Ver Detalles
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Tab Vencidos */}
          {activeTab === 'overdue' && (
            <div className="space-y-4">
              {overdueWorkflowsData.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircleIcon className="h-12 w-12 text-green-400 mx-auto mb-4" />
                  <p className="text-gray-500">No hay workflows vencidos</p>
                </div>
              ) : (
                overdueWorkflowsData.map((workflow) => (
                  <div key={workflow.id} className="border border-red-200 rounded-lg p-4 bg-red-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="text-sm font-medium text-red-900">
                          {workflow.template?.name}
                        </h4>
                        <p className="text-sm text-red-700">
                          Paso actual: {workflow.current_step?.name}
                        </p>
                        <p className="text-xs text-red-600 mt-1">
                          Vencido desde: {formatDate(workflow.due_date)}
                        </p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Vencido
                        </span>
                        <button className="bg-red-600 text-white px-3 py-1 rounded-md text-sm hover:bg-red-700">
                          Urgente
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Próximas fechas límite */}
      {upcomingDeadlines.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Próximas Fechas Límite</h3>
          <div className="space-y-3">
            {upcomingDeadlines.slice(0, 5).map((workflow) => (
              <div key={workflow.id} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-center space-x-3">
                  <ClockIcon className="h-5 w-5 text-yellow-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{workflow.template?.name}</p>
                    <p className="text-xs text-gray-600">
                      Paso: {workflow.current_step?.name}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-yellow-800">
                    {formatDate(workflow.due_date)}
                  </p>
                  <p className="text-xs text-yellow-600">Próximo a vencer</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowDashboard;
