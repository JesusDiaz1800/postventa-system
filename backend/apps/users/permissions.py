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
        'can_view_supplier_reports': True,
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
        'can_view_supplier_reports': True,
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
         'can_view_supplier_reports': False,
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
        'can_view_supplier_reports': False,  # No puede ver reportes de proveedores
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
        'can_view_supplier_reports': False,  # No puede ver reportes de proveedores
    },
    'analyst': {
        'can_manage_users': False,
        'can_manage_incidents': True,
        'can_view_reports': True,
        'can_manage_workflows': True,
        'can_manage_documents': True,
        'can_access_admin': False,
        'can_export_data': True,
        'can_view_audit_logs': True,
        'can_manage_system_settings': False,
        'can_view_supplier_reports': False,
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
        'can_view_supplier_reports': True,
    },
    'provider': {
        'can_manage_users': False,
        'can_manage_incidents': False,
        'can_view_reports': True,
        'can_manage_workflows': False,
        'can_manage_documents': True,
        'can_access_admin': False,
        'can_export_data': True,
        'can_view_audit_logs': False,
        'can_manage_system_settings': False,
        'can_view_supplier_reports': True,
    }
}


def has_permission(user, permission):
    """
    Verifica si un usuario tiene un permiso específico basado en su rol
    """
    if not user or not user.is_authenticated:
        return False
        
    # Superusuario siempre tiene permisos
    if user.is_superuser:
        return True
        
    user_role = getattr(user, 'role', 'guest')
    role_perms = ROLE_PERMISSIONS.get(user_role, {})
    
    return role_perms.get(permission, False)


def get_user_permissions(user):
    """
    Obtiene todos los permisos del usuario
    """
    if not user or not user.is_authenticated:
        return {}
        
    user_role = getattr(user, 'role', 'guest')
    return ROLE_PERMISSIONS.get(user_role, {})


def get_accessible_pages(user):
    """
    Obtiene las páginas accesibles para el usuario
    """
    if not user or not user.is_authenticated:
        return []
        
    permissions = get_user_permissions(user)
    accessible_pages = ['dashboard', 'profile']
    
    if permissions.get('can_manage_users'):
        accessible_pages.append('users')
        
    if permissions.get('can_manage_incidents') or permissions.get('can_view_reports'):
        accessible_pages.extend(['incidents', 'incidents/list'])
        
    if permissions.get('can_manage_workflows'):
        accessible_pages.append('workflows')
        
    if permissions.get('can_manage_documents'):
        accessible_pages.append('documents')
        
    if permissions.get('can_view_audit_logs'):
        accessible_pages.append('audit')
        
    if permissions.get('can_view_reports'):
        accessible_pages.append('reports')
        
    if permissions.get('can_view_supplier_reports'):
        accessible_pages.extend(['reports/supplier', 'documents/supplier-reports'])
        
    return accessible_pages
