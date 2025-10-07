"""
Middleware para auditoría automática de acc            # Registrar en el log de auditoría
            AuditLogManager.log_action(
                user=request.user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=self._create_action_description(request, response),
                metadata={"""
import json
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from .models import AuditLogManager, AuditLog

User = get_user_model()
logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para registrar automáticamente las acciones de los usuarios
    """
    
    def process_request(self, request):
        """Procesar la request antes de que llegue a la vista"""
        # Marcar el inicio de la request para tracking
        request._audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Procesar la response después de que la vista haya respondido"""
        try:
            # Solo registrar para usuarios autenticados
            if hasattr(request, 'user') and request.user.is_authenticated:
                self._log_request(request, response)
        except Exception as e:
            logger.error(f"Error en AuditMiddleware: {e}")
        
        return response
    
    def _log_request(self, request, response):
        """Registrar la acción del usuario"""
        try:
            # Determinar el tipo de acción basado en el método HTTP
            action = self._get_action_from_method(request.method)
            
            # Obtener información del recurso
            resource_type, resource_id = self._get_resource_info(request)
            
            # Crear descripción de la acción
            details = self._create_action_description(request, response)
            
            # Registrar en el log de auditoría
            AuditLogManager.log_action(
                user=request.user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=self._get_client_ip(request),
                metadata={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', ''),
                }
            )
            
        except Exception as e:
            logger.error(f"Error al registrar acción en AuditMiddleware: {e}")
    
    def _get_action_from_method(self, method):
        """Determinar la acción basada en el método HTTP"""
        method_actions = {
            'GET': 'view',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        return method_actions.get(method.upper(), 'view')
    
    def _get_resource_info(self, request):
        """Extraer información del recurso de la URL"""
        path_parts = request.path.strip('/').split('/')
        
        # Mapear rutas a tipos de recurso
        resource_mapping = {
            'api/incidents': 'incident',
            'api/users': 'user',
            'api/documents': 'document',
            'api/reports': 'report',
            'api/workflows': 'workflow',
            'api/ai': 'ai_analysis',
        }
        
        # Buscar el tipo de recurso
        resource_type = 'system'
        resource_id = '0'
        
        for path_part in path_parts:
            if path_part in resource_mapping:
                resource_type = resource_mapping[path_part]
                break
        
        # Intentar extraer ID del recurso
        for i, part in enumerate(path_parts):
            if part.isdigit():
                resource_id = part
                break
        
        return resource_type, resource_id
    
    def _create_action_description(self, request, response):
        """Crear una descripción legible de la acción"""
        method = request.method
        path = request.path
        status_code = response.status_code
        
        if method == 'GET':
            return f"Visualizó {path}"
        elif method == 'POST':
            return f"Creó recurso en {path}"
        elif method in ['PUT', 'PATCH']:
            return f"Actualizó recurso en {path}"
        elif method == 'DELETE':
            return f"Eliminó recurso en {path}"
        else:
            return f"Acción {method} en {path}"
    
    def _get_client_ip(self, request):
        """Obtener la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Export the middleware class
__all__ = ['AuditMiddleware']
