import { useQuery } from '@tanstack/react-query';
import { usersAPI } from '../services/api';

/**
 * Hook para manejar permisos del usuario actual
 */
export const usePermissions = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['user-permissions'],
    queryFn: () => usersAPI.getPermissions(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000, // 10 minutos
    retry: 1,
  });

  // Handle nested response structure
  const actualData = data?.data || data;
  const permissions = actualData?.permissions || {};
  const accessiblePages = actualData?.accessible_pages || [];
  const user = actualData?.user || null;
  

  const hasPermission = (permission) => {
    return permissions[permission] === true;
  };

  const canAccessPage = (page) => {
    return accessiblePages.includes(page);
  };

  const canManageUsers = () => hasPermission('can_manage_users');
  const canManageIncidents = () => hasPermission('can_manage_incidents');
  const canViewReports = () => hasPermission('can_view_reports');
  const canManageWorkflows = () => hasPermission('can_manage_workflows');
  const canManageDocuments = () => hasPermission('can_manage_documents');
  const canAccessAdmin = () => hasPermission('can_access_admin');
  const canExportData = () => hasPermission('can_export_data');
  const canViewAuditLogs = () => hasPermission('can_view_audit_logs');
  const canManageSystemSettings = () => hasPermission('can_manage_system_settings');

  return {
    user,
    permissions,
    accessiblePages,
    isLoading,
    error,
    refetch,
    hasPermission,
    canAccessPage,
    canManageUsers,
    canManageIncidents,
    canViewReports,
    canManageWorkflows,
    canManageDocuments,
    canAccessAdmin,
    canExportData,
    canViewAuditLogs,
    canManageSystemSettings,
  };
};

/**
 * Hook para verificar si el usuario puede acceder a una página específica
 */
export const usePageAccess = (pageName) => {
  const { canAccessPage, isLoading } = usePermissions();
  
  return {
    canAccess: canAccessPage(pageName),
    isLoading,
  };
};

/**
 * Hook para verificar un permiso específico
 */
export const usePermission = (permissionName) => {
  const { hasPermission, isLoading } = usePermissions();
  
  return {
    hasPermission: hasPermission(permissionName),
    isLoading,
  };
};
