"""
Middleware para control de acceso basado en roles
"""

from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from .permissions import get_accessible_pages, has_permission


class RoleBasedAccessMiddleware:
    """
    Middleware que controla el acceso a las páginas basado en roles
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Páginas que requieren autenticación pero no permisos específicos
        self.public_authenticated_pages = [
            'dashboard',
            'profile',
            'logout',
        ]
        
        # Páginas que no requieren autenticación
        self.public_pages = [
            'login',
            'register',
            'password-reset',
        ]
    
    def __call__(self, request):
        # Solo aplicar el middleware a las rutas de la API
        if request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Obtener la página actual
        current_page = self.get_current_page(request.path)
        
        # Si es una página pública, permitir acceso
        if current_page in self.public_pages:
            return self.get_response(request)
        
        # Si el usuario no está autenticado, redirigir al login
        if not request.user.is_authenticated:
            if request.path.startswith('/api/'):
                return JsonResponse({'error': 'No autenticado'}, status=401)
            return redirect('login')
        
        # Si es una página que requiere autenticación pero no permisos específicos
        if current_page in self.public_authenticated_pages:
            return self.get_response(request)
        
        # Verificar si el usuario tiene acceso a la página
        accessible_pages = get_accessible_pages(request.user)
        
        if current_page not in accessible_pages:
            if request.path.startswith('/api/'):
                return JsonResponse({'error': 'Permisos insuficientes'}, status=403)
            
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('dashboard')
        
        return self.get_response(request)
    
    def get_current_page(self, path):
        """
        Extrae el nombre de la página de la URL
        """
        # Remover la barra inicial y dividir por '/'
        path_parts = path.strip('/').split('/')
        
        if not path_parts or path_parts[0] == '':
            return 'dashboard'
        
        # Retornar la primera parte como página principal
        return path_parts[0]


class APIPermissionMiddleware:
    """
    Middleware específico para controlar permisos en la API
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Solo aplicar a rutas de API
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Rutas de API que no requieren permisos específicos
        public_api_routes = [
            '/api/auth/login/',
            '/api/auth/refresh/',
            '/api/auth/logout/',
            '/api/users/permissions/',  # Permitir acceso a permisos para verificar autenticación
        ]
        
        if request.path in public_api_routes:
            return self.get_response(request)
        
        # Para otras rutas, solo verificar permisos si el usuario está autenticado
        # No bloquear aquí la autenticación, dejar que DRF lo maneje
        if request.user.is_authenticated:
            # Verificar permisos específicos por endpoint solo si está autenticado
            if not self.check_endpoint_permissions(request):
                return JsonResponse({'error': 'Permisos insuficientes'}, status=403)
        
        return self.get_response(request)
    
    def check_endpoint_permissions(self, request):
        """
        Verifica permisos específicos para cada endpoint
        """
        path = request.path
        method = request.method
        
        # Permisos para gestión de usuarios
        if path.startswith('/api/users/') and method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return has_permission(request.user, 'can_manage_users')
        
        # Permisos para gestión de incidencias
        if path.startswith('/api/incidents/') and method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return has_permission(request.user, 'can_manage_incidents')
        
        # Permisos para reportes - permitir a todos los usuarios autenticados
        # if path.startswith('/api/reports/'):
        #     return has_permission(request.user, 'can_view_reports')
        
        # Permisos para workflows
        if path.startswith('/api/workflows/') and method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return has_permission(request.user, 'can_manage_workflows')
        
        # Permisos para documentos
        if path.startswith('/api/documents/') and method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return has_permission(request.user, 'can_manage_documents')
        
        # Permisos para logs de auditoría
        if path.startswith('/api/audit/'):
            return has_permission(request.user, 'can_view_audit_logs')
        
        # Por defecto, permitir acceso de lectura
        return True
