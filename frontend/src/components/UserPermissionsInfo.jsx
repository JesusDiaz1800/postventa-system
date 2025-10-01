import React from 'react';
import { usePermissions } from '../hooks/usePermissions';
import { 
  UserIcon, 
  ShieldCheckIcon, 
  EyeIcon, 
  PencilIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CogIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

/**
 * Componente para mostrar información de permisos del usuario
 */
const UserPermissionsInfo = ({ showDetails = false }) => {
  const { 
    user, 
    permissions, 
    accessiblePages, 
    isLoading,
    canManageUsers,
    canManageIncidents,
    canViewReports,
    canManageWorkflows,
    canManageDocuments,
    canAccessAdmin,
    canExportData,
    canViewAuditLogs,
    canManageSystemSettings
  } = usePermissions();

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex items-center text-red-600">
        <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
        <span>Usuario no autenticado</span>
      </div>
    );
  }

  const permissionItems = [
    {
      key: 'can_manage_users',
      label: 'Gestionar Usuarios',
      icon: UserIcon,
      hasPermission: canManageUsers(),
      description: 'Crear, editar y eliminar usuarios del sistema'
    },
    {
      key: 'can_manage_incidents',
      label: 'Gestionar Incidencias',
      icon: PencilIcon,
      hasPermission: canManageIncidents(),
      description: 'Crear, editar y resolver incidencias'
    },
    {
      key: 'can_view_reports',
      label: 'Ver Reportes',
      icon: ChartBarIcon,
      hasPermission: canViewReports(),
      description: 'Acceder a reportes y estadísticas'
    },
    {
      key: 'can_manage_workflows',
      label: 'Gestionar Workflows',
      icon: CogIcon,
      hasPermission: canManageWorkflows(),
      description: 'Crear y modificar flujos de trabajo'
    },
    {
      key: 'can_manage_documents',
      label: 'Gestionar Documentos',
      icon: DocumentTextIcon,
      hasPermission: canManageDocuments(),
      description: 'Subir, editar y organizar documentos'
    },
    {
      key: 'can_access_admin',
      label: 'Acceso Admin',
      icon: ShieldCheckIcon,
      hasPermission: canAccessAdmin(),
      description: 'Acceder al panel de administración'
    },
    {
      key: 'can_export_data',
      label: 'Exportar Datos',
      icon: EyeIcon,
      hasPermission: canExportData(),
      description: 'Exportar datos del sistema'
    },
    {
      key: 'can_view_audit_logs',
      label: 'Ver Logs de Auditoría',
      icon: EyeIcon,
      hasPermission: canViewAuditLogs(),
      description: 'Revisar registros de actividad del sistema'
    },
    {
      key: 'can_manage_system_settings',
      label: 'Configuración del Sistema',
      icon: CogIcon,
      hasPermission: canManageSystemSettings(),
      description: 'Modificar configuraciones globales'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Información del usuario */}
      <div className="flex items-center mb-6">
        <div className="flex-shrink-0">
          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
            <UserIcon className="h-6 w-6 text-blue-600" />
          </div>
        </div>
        <div className="ml-4">
          <h3 className="text-lg font-medium text-gray-900">
            {user.username}
          </h3>
          <p className="text-sm text-gray-500">
            {user.role_display} • {user.is_active ? 'Activo' : 'Inactivo'}
          </p>
        </div>
      </div>

      {/* Páginas accesibles */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-900 mb-3">
          Páginas Accesibles
        </h4>
        <div className="flex flex-wrap gap-2">
          {accessiblePages.map((page) => (
            <span
              key={page}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
            >
              {page}
            </span>
          ))}
        </div>
      </div>

      {/* Permisos detallados */}
      {showDetails && (
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            Permisos Detallados
          </h4>
          <div className="space-y-3">
            {permissionItems.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.key}
                  className={`flex items-start p-3 rounded-lg border ${
                    item.hasPermission
                      ? 'bg-green-50 border-green-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <Icon
                    className={`h-5 w-5 mt-0.5 mr-3 ${
                      item.hasPermission ? 'text-green-600' : 'text-gray-400'
                    }`}
                  />
                  <div className="flex-1">
                    <div className="flex items-center">
                      <span
                        className={`text-sm font-medium ${
                          item.hasPermission ? 'text-green-900' : 'text-gray-500'
                        }`}
                      >
                        {item.label}
                      </span>
                      <span
                        className={`ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          item.hasPermission
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {item.hasPermission ? 'Permitido' : 'Denegado'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {item.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserPermissionsInfo;
