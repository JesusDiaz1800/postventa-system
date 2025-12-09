"""
Middleware para registrar la navegación del usuario (páginas visitadas)
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from .models import AuditLogManager

User = get_user_model()
logger = logging.getLogger(__name__)


class NavigationAuditMiddleware(MiddlewareMixin):
    """
    Middleware para registrar las páginas que visita el usuario
    """
    
    def process_response(self, request, response):
        """Procesar la response para registrar navegación"""
        try:
            # Solo registrar para usuarios autenticados y requests exitosas
            if (hasattr(request, 'user') and 
                request.user.is_authenticated and 
                response.status_code == 200 and
                request.method == 'GET'):
                
                self._log_navigation(request, response)
                
        except Exception as e:
            logger.error(f"Error en NavigationAuditMiddleware: {e}")
        
        return response
    
    def _log_navigation(self, request, response):
        """Registrar la navegación del usuario"""
        try:
            path = request.path
            
            # Solo registrar páginas importantes (no APIs ni archivos estáticos)
            if self._should_log_navigation(path):
                page_description = self._get_page_description(path)
                
                # Registrar en el log de auditoría
                AuditLogManager.log_action(
                    user=request.user,
                    action='ver',
                    description=f"Visitó página: {page_description}",
                    ip_address=self._get_client_ip(request),
                    details={
                        'page': path,
                        'page_title': page_description,
                        'method': request.method,
                        'status_code': response.status_code
                    }
                )
                
        except Exception as e:
            logger.error(f"Error al registrar navegación: {e}")
    
    def _should_log_navigation(self, path):
        """Determinar si la navegación debe ser registrada"""
        # No registrar APIs, archivos estáticos, admin, etc.
        exclude_patterns = [
            '/api/',
            '/static/',
            '/media/',
            '/admin/',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
            '/sw.js',
            '/manifest.json',
            '/offline.html',
            '/health/',
            '/ping/',
        ]
        
        # No registrar si coincide con algún patrón de exclusión
        return not any(path.startswith(pattern) for pattern in exclude_patterns)
    
    def _get_page_description(self, path):
        """Obtener descripción amigable de la página"""
        page_descriptions = {
            '/': 'Página principal',
            '/dashboard': 'Dashboard principal',
            '/incidents': 'Lista de incidencias',
            '/incidents/new': 'Crear nueva incidencia',
            '/incidents/': 'Detalles de incidencia',
            '/documents': 'Gestión de documentos',
            '/documents/visit-reports': 'Reportes de visita',
            '/documents/lab-reports': 'Reportes de laboratorio',
            '/documents/supplier-reports': 'Reportes de proveedor',
            '/documents/quality-reports': 'Reportes de calidad',
            '/reports': 'Reportes del sistema',
            '/reports/client-quality': 'Reportes de calidad para cliente',
            '/reports/supplier': 'Reportes de proveedor',
            '/users': 'Gestión de usuarios',
            '/audit': 'Auditoría del sistema',
            '/profile': 'Perfil de usuario',
            '/settings': 'Configuración',
            '/help': 'Ayuda del sistema',
            '/about': 'Acerca del sistema',
        }
        
        # Buscar descripción específica
        for pattern, description in page_descriptions.items():
            if path.startswith(pattern):
                return description
        
        # Si no se encuentra, usar el path
        return path
    
    def _get_client_ip(self, request):
        """Obtener la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Export the middleware class
__all__ = ['NavigationAuditMiddleware']
