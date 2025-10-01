"""
Sistema de permisos basado en roles para el sistema de postventa
"""

from functools import wraps
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status


class RoleBasedPermission(BasePermission):
    """
    Permiso basado en roles para DRF
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Obtener el rol requerido desde la vista
        required_role = getattr(view, 'required_role', None)
        required_roles = getattr(view, 'required_roles', [])
        
        if required_role:
            return request.user.has_role(required_role)
        
        if required_roles:
            return request.user.role in required_roles
        
        # Si no hay roles específicos requeridos, permitir acceso
        return True


def role_required(role):
    """
    Decorador para vistas que requieren un rol específico
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'No autenticado'}, status=401)
            
            if not request.user.has_role(role):
                return JsonResponse({'error': 'Permisos insuficientes'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def roles_required(roles):
    """
    Decorador para vistas que requieren uno de varios roles
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'No autenticado'}, status=401)
            
            if request.user.role not in roles:
                return JsonResponse({'error': 'Permisos insuficientes'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Definición de permisos por rol
ROLE_PERMISSIONS = {
    'administrador': {
        'can_manage_users': True,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': True,
        'can_manage_documents': True,
        'can_access_admin': True,
        'can_export_data': True,
        'can_view_audit_logs': True,
        'can_manage_system_settings': True,
    },
    'admin': {
        'can_manage_users': True,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': True,
        'can_manage_documents': True,
        'can_access_admin': True,
        'can_export_data': True,
        'can_view_audit_logs': True,
        'can_manage_system_settings': True,
    },
    'supervisor': {
        'can_manage_users': True,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': True,
        'can_manage_documents': True,
        'can_access_admin': False,
        'can_export_data': True,
        'can_view_audit_logs': True,
        'can_manage_system_settings': False,
    },
    'analyst': {
        'can_manage_users': False,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': False,
        'can_manage_documents': True,
        'can_access_admin': False,
        'can_export_data': False,
        'can_view_audit_logs': False,
        'can_manage_system_settings': False,
    },
    'customer_service': {
        'can_manage_users': False,
        'can_manage_incidents': False,
        'can_view_reports': False,
        'can_manage_workflows': False,
        'can_manage_documents': False,
        'can_access_admin': False,
        'can_export_data': False,
        'can_view_audit_logs': False,
        'can_manage_system_settings': False,
    },
    'management': {
        'can_manage_users': False,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': True,
        'can_manage_documents': True,
        'can_access_admin': False,
        'can_export_data': True,
        'can_view_audit_logs': True,
        'can_manage_system_settings': False,
    },
    'technical_service': {
        'can_manage_users': False,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': True,
        'can_manage_documents': True,
        'can_access_admin': False,
        'can_export_data': True,
        'can_view_audit_logs': True,
        'can_manage_system_settings': False,
    },
    'quality': {
        'can_manage_users': False,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': True,
        'can_manage_documents': True,
        'can_access_admin': False,
        'can_export_data': True,
        'can_view_audit_logs': True,
        'can_manage_system_settings': False,
    },
    'provider': {
        'can_manage_users': False,
        'can_manage_incidents': False,
        'can_view_reports': False,
        'can_manage_workflows': False,
        'can_manage_documents': False,
        'can_access_admin': False,
        'can_export_data': False,
        'can_view_audit_logs': False,
        'can_manage_system_settings': False,
    },
}


def get_user_permissions(user):
    """
    Obtiene los permisos de un usuario basado en su rol
    """
    if not user or not user.is_authenticated:
        return {}
    
    return ROLE_PERMISSIONS.get(user.role, {})


def has_permission(user, permission):
    """
    Verifica si un usuario tiene un permiso específico
    """
    if not user or not user.is_authenticated:
        return False
    
    user_permissions = get_user_permissions(user)
    return user_permissions.get(permission, False)


def get_accessible_pages(user):
    """
    Obtiene las páginas a las que un usuario puede acceder
    """
    if not user or not user.is_authenticated:
        return []
    
    permissions = get_user_permissions(user)
    accessible_pages = []
    
    # Páginas básicas que todos pueden ver
    accessible_pages.extend(['dashboard', 'profile'])
    
    # Páginas basadas en permisos
    if permissions.get('can_manage_incidents'):
        accessible_pages.extend(['incidents', 'incidents/create', 'incidents/edit'])
    
    if permissions.get('can_manage_users'):
        accessible_pages.extend(['users', 'users/create', 'users/edit'])
    
    if permissions.get('can_view_reports'):
        accessible_pages.extend(['reports'])
    
    if permissions.get('can_manage_workflows'):
        accessible_pages.extend(['workflows', 'workflows/create', 'workflows/edit'])
    
    if permissions.get('can_manage_documents'):
        accessible_pages.extend(['documents'])
    
    if permissions.get('can_view_audit_logs'):
        accessible_pages.extend(['audit'])
    
    if permissions.get('can_access_admin'):
        accessible_pages.extend(['admin'])
    
    return accessible_pages
