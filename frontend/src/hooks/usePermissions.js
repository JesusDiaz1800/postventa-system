import { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';

/**
 * Hook para manejar permisos del usuario actual (Versión simplificada para evitar errores de contexto)
 */
/**
 * Hook para manejar permisos del usuario actual (Versión ultra-estable sin estado)
 */
export const usePermissions = () => {
  // Obtenemos los datos del usuario del localStorage con múltiples respaldos para robustez
  const authRaw = localStorage.getItem('postventa_auth');
  let user = null;
  
  if (authRaw) {
    try {
      const parsed = JSON.parse(authRaw);
      user = parsed.user || parsed;
    } catch (e) {
      console.error('Error parsing auth data in usePermissions:', e);
    }
  }

  // Si no está en postventa_auth, buscar en 'user' (respaldo legacy)
  if (!user) {
    const userStr = localStorage.getItem('user');
    user = userStr ? JSON.parse(userStr) : null;
  }

  const permissions = user?.permissions || {};
  const accessiblePages = user?.accessible_pages || [];

  const hasPermission = (permission) => {
    return permissions[permission] === true;
  };

  const canAccessPage = (page) => {
    return accessiblePages.includes(page);
  };

  const canManageUsers = () => hasPermission('can_manage_users');
  const canManageVisits = () => hasPermission('can_manage_visits');
  const canViewReports = () => hasPermission('can_view_reports');
  const canManageWorkflows = () => hasPermission('can_manage_workflows');
  const canManageDocuments = () => hasPermission('can_manage_documents');
  const canAccessAdmin = () => hasPermission('can_access_admin');
  const canExportData = () => hasPermission('can_export_data');
  const canViewAuditLogs = () => hasPermission('can_view_audit_logs');
  const canManageSystemSettings = () => hasPermission('can_manage_system_settings');
  const canViewSupplierReports = () => hasPermission('can_view_supplier_reports');

  return {
    user,
    permissions,
    accessiblePages,
    isLoading: false,
    error: null,
    refetch: () => Promise.resolve(),
    hasPermission,
    canAccessPage,
    canManageUsers,
    canManageVisits,
    canViewReports,
    canManageWorkflows,
    canManageDocuments,
    canAccessAdmin,
    canExportData,
    canViewAuditLogs,
    canManageSystemSettings,
    canViewSupplierReports,
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
