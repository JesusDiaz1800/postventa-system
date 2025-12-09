"""
Middleware para auditoría automática de acciones importantes de usuarios
"""
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
    Middleware para registrar automáticamente solo las acciones importantes de los usuarios
    """
    
    def process_request(self, request):
        """Procesar la request antes de que llegue a la vista"""
        request._audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Procesar la response después de que la vista haya respondido"""
        try:
            # Solo registrar para usuarios autenticados
            if hasattr(request, 'user') and request.user.is_authenticated:
                # Solo registrar acciones importantes
                if self._should_audit(request):
                    self._log_request(request, response)
        except Exception as e:
            logger.error(f"Error en AuditMiddleware: {e}")
        
        return response
    
    def _should_audit(self, request):
        """Determinar si la acción debe ser auditada"""
        method = request.method
        path = request.path
        
        # Siempre auditar Login/Logout
        if '/api/auth/' in path:
            return True
            
        # Siempre auditar escrituras (POST, PUT, PATCH, DELETE)
        if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return True
            
        # Auditar descargas de documentos
        if '/download/' in path:
            return True
            
        return False

    def _log_request(self, request, response):
        """Registrar la request en la base de datos"""
        try:
            method = request.method
            path = request.path
            
            # Determinar acción y recurso
            action = self._get_action_from_method(method)
            resource_type, resource_id = self._get_resource_info(request)
            
            # Crear descripción
            description = self._create_action_description(request, response)
            
            # Registrar en el log de auditoría
            AuditLogManager.log_action(
                user=request.user,
                action=action,
                description=description,
                ip_address=self._get_client_ip(request),
                details={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'resource_type': resource_type,
                    'resource_id': resource_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error al registrar acción en AuditMiddleware: {e}")
    
    def _get_action_from_method(self, method):
        """Determinar la acción basada en el método HTTP"""
        method_actions = {
            'POST': 'crear',
            'PUT': 'actualizar',
            'PATCH': 'actualizar',
            'DELETE': 'eliminar',
        }
        return method_actions.get(method.upper(), 'crear')
    
    def _get_resource_info(self, request):
        """Extraer información del recurso de la URL"""
        path = request.path
        
        # Mapear rutas a tipos de recurso
        if '/api/incidents/' in path:
            return 'incident', self._extract_id_from_path(path)
        elif '/api/documents/' in path:
            return 'document', self._extract_id_from_path(path)
        elif '/api/auth/login/' in path:
            return 'authentication', 'login'
        elif '/api/auth/logout/' in path:
            return 'authentication', 'logout'
        elif '/api/workflows/' in path:
            return 'workflow', self._extract_id_from_path(path)
        else:
            return 'system', '0'
    
    def _extract_id_from_path(self, path):
        """Extraer ID de la URL"""
        parts = path.strip('/').split('/')
        for part in parts:
            if part.isdigit():
                return part
        return '0'
    
    def _create_action_description(self, request, response):
        """Crear una descripción legible de la acción en español"""
        method = request.method
        path = request.path
        
        # Descriptions específicas para cada tipo de acción
        descriptions = {
            '/api/auth/login/': 'Inició sesión en el sistema',
            '/api/auth/logout/': 'Cerró sesión del sistema',
            '/api/incidents/': self._get_incident_description(method, path),
            '/api/documents/upload/': 'Subió archivo al sistema',
            '/api/documents/download/': 'Descargó archivo del sistema',
            '/api/documents/attach/': 'Adjuntó documento',
            '/api/documents/visit-reports/': self._get_report_description(method, 'reporte de visita'),
            '/api/documents/lab-reports/': self._get_report_description(method, 'reporte de laboratorio'),
            '/api/documents/supplier-reports/': self._get_report_description(method, 'reporte de proveedor'),
            '/api/documents/quality-reports/': self._get_report_description(method, 'reporte de calidad'),
            '/api/workflows/escalate/': 'Escaló incidencia',
            '/api/workflows/close/': 'Cerró incidencia',
        }
        
        # Buscar descripción específica
        for pattern, desc in descriptions.items():
            if path.startswith(pattern):
                return desc
        
        # Descripción genérica
        if method == 'POST':
            return 'Creó nuevo elemento'
        elif method in ['PUT', 'PATCH']:
            return 'Actualizó elemento'
        elif method == 'DELETE':
            return 'Eliminó elemento'
        else:
            return 'Realizó acción en el sistema'
    
    def _get_incident_description(self, method, path):
        """Obtener descripción específica para incidencias"""
        if method == 'POST':
            return 'Creó nueva incidencia'
        elif method in ['PUT', 'PATCH']:
            return 'Actualizó incidencia'
        elif method == 'DELETE':
            return 'Eliminó incidencia'
        else:
            return 'Realizó acción en incidencia'
    
    def _get_report_description(self, method, report_type):
        """Obtener descripción específica para reportes"""
        if method == 'POST':
            return f'Creó {report_type}'
        elif method in ['PUT', 'PATCH']:
            return f'Actualizó {report_type}'
        elif method == 'DELETE':
            return f'Eliminó {report_type}'
        else:
            return f'Realizó acción en {report_type}'
    
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
