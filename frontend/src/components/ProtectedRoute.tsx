import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { usePermissions } from '../hooks/usePermissions';
import { useNotifications } from '../hooks/useNotifications';

/**
 * Componente para proteger rutas basado en permisos
 */
const ProtectedRoute = ({ 
  children, 
  requiredPermission, 
  requiredPage, 
  fallbackPath = '/dashboard',
  showMessage = true 
}) => {
  const { hasPermission, canAccessPage, isLoading, user } = usePermissions();
  const { showError } = useNotifications();
  const location = useLocation();

  // Mostrar loading mientras se cargan los permisos
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Si no hay usuario autenticado, redirigir al login
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Verificar permiso específico
  if (requiredPermission && !hasPermission(requiredPermission)) {
    if (showMessage) {
      showError('No tienes permisos para acceder a esta página');
    }
    return <Navigate to={fallbackPath} replace />;
  }

  // Verificar acceso a página específica
  if (requiredPage && !canAccessPage(requiredPage)) {
    if (showMessage) {
      showError('No tienes permisos para acceder a esta página');
    }
    return <Navigate to={fallbackPath} replace />;
  }

  return children;
};

/**
 * Componente para mostrar contenido condicionalmente basado en permisos
 */
export const PermissionGate = ({ 
  permission, 
  page, 
  children, 
  fallback = null,
  requireAll = false 
}) => {
  const { hasPermission, canAccessPage, isLoading } = usePermissions();

  if (isLoading) {
    return fallback;
  }

  let hasAccess = true;

  if (permission) {
    hasAccess = hasPermission(permission);
  }

  if (page) {
    const pageAccess = canAccessPage(page);
    hasAccess = requireAll ? (hasAccess && pageAccess) : (hasAccess || pageAccess);
  }

  return hasAccess ? children : fallback;
};

/**
 * Hook para verificar permisos en componentes
 */
export const useRouteProtection = () => {
  const { hasPermission, canAccessPage, user, isLoading } = usePermissions();

  const canAccess = (permission, page) => {
    if (isLoading) return false;
    
    let access = true;
    
    if (permission) {
      access = hasPermission(permission);
    }
    
    if (page) {
      access = access && canAccessPage(page);
    }
    
    return access;
  };

  const redirectIfNoAccess = (permission, page, fallbackPath = '/dashboard') => {
    if (!canAccess(permission, page)) {
      return <Navigate to={fallbackPath} replace />;
    }
    return null;
  };

  return {
    canAccess,
    redirectIfNoAccess,
    user,
    isLoading,
  };
};

export default ProtectedRoute;
