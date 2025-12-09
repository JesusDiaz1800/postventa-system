"""
<<<<<<< HEAD
Middleware para auditoría automática de acc            # Registrar en el log de auditoría
            AuditLogManager.log_action(
                user=request.user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=self._create_action_description(request, response),
                metadata={"""
=======
Middleware para auditoría automática de acciones importantes de usuarios
"""
>>>>>>> 674c244 (tus cambios)
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
<<<<<<< HEAD
    Middleware para registrar automáticamente las acciones de los usuarios
=======
    Middleware para registrar automáticamente solo las acciones importantes de los usuarios
>>>>>>> 674c244 (tus cambios)
    """
    
    def process_request(self, request):
        """Procesar la request antes de que llegue a la vista"""
<<<<<<< HEAD
        # Marcar el inicio de la request para tracking
=======
>>>>>>> 674c244 (tus cambios)
        request._audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Procesar la response después de que la vista haya respondido"""
        try:
            # Solo registrar para usuarios autenticados
            if hasattr(request, 'user') and request.user.is_authenticated:
<<<<<<< HEAD
                self._log_request(request, response)
=======
                # Solo registrar acciones importantes
                if self._should_audit(request):
                    self._log_request(request, response)
>>>>>>> 674c244 (tus cambios)
        except Exception as e:
            logger.error(f"Error en AuditMiddleware: {e}")
        
        return response
    
<<<<<<< HEAD
=======
    def _should_audit(self, request):
        """Determinar si la acción debe ser auditada"""
        path = request.path
        method = request.method
        
        # Rutas que SÍ deben ser auditadas
        important_paths = [
            '/api/auth/login/',           # Login
            '/api/auth/logout/',          # Logout
            '/api/incidents/',            # Crear/eliminar incidencias
            '/api/documents/',            # Crear/eliminar documentos
            '/api/documents/visit-reports/', # Crear reportes de visita
            '/api/documents/lab-reports/',   # Crear reportes de laboratorio
            '/api/documents/supplier-reports/', # Crear reportes de proveedor
            '/api/documents/quality-reports/',  # Crear reportes de calidad
            '/api/documents/upload/',     # Subir archivos
            '/api/documents/download/',   # Descargar archivos
            '/api/documents/attach/',     # Adjuntar documentos
            '/api/workflows/escalate/',   # Escalar incidencias
            '/api/workflows/close/',      # Cerrar incidencias
        ]
        
        # Métodos importantes
        important_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        
        # Verificar si es una ruta importante
        is_important_path = any(path.startswith(important_path) for important_path in important_paths)
        
        # Verificar si es un método importante
        is_important_method = method in important_methods
        
        # Solo auditar si es una ruta importante Y un método importante
        return is_important_path and is_important_method
    
>>>>>>> 674c244 (tus cambios)
    def _log_request(self, request, response):
        """Registrar la acción del usuario"""
        try:
            # Determinar el tipo de acción basado en el método HTTP
            action = self._get_action_from_method(request.method)
            
            # Obtener información del recurso
            resource_type, resource_id = self._get_resource_info(request)
            
            # Crear descripción de la acción
<<<<<<< HEAD
            details = self._create_action_description(request, response)
=======
            description = self._create_action_description(request, response)
>>>>>>> 674c244 (tus cambios)
            
            # Registrar en el log de auditoría
            AuditLogManager.log_action(
                user=request.user,
                action=action,
<<<<<<< HEAD
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=self._get_client_ip(request),
                metadata={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', ''),
=======
                description=description,
                ip_address=self._get_client_ip(request),
                details={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'resource_type': resource_type,
                    'resource_id': resource_id
>>>>>>> 674c244 (tus cambios)
                }
            )
            
        except Exception as e:
            logger.error(f"Error al registrar acción en AuditMiddleware: {e}")
    
    def _get_action_from_method(self, method):
        """Determinar la acción basada en el método HTTP"""
        method_actions = {
<<<<<<< HEAD
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
=======
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
>>>>>>> 674c244 (tus cambios)
    
    def _get_client_ip(self, request):
        """Obtener la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Export the middleware class
<<<<<<< HEAD
__all__ = ['AuditMiddleware']
=======
__all__ = ['AuditMiddleware']
>>>>>>> 674c244 (tus cambios)
