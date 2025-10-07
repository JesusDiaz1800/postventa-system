import time
import logging
import threading
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger('postventa.middleware')
local = threading.local()

class RequestTimingMiddleware(MiddlewareMixin):
    """Middleware para medir y registrar el tiempo de respuesta de las solicitudes."""
    
    def process_request(self, request):
        local.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(local, 'start_time'):
            duration = time.time() - local.start_time
            logger.info(
                'Request timing',
                extra={
                    'path': request.path,
                    'method': request.method,
                    'duration': duration,
                    'status_code': response.status_code
                }
            )
        return response

class RateLimitMiddleware(MiddlewareMixin):
    """Middleware para limitar la tasa de solicitudes por usuario/IP."""
    
    def process_request(self, request):
        if settings.DEBUG:
            return None
            
        ip = self._get_client_ip(request)
        key = f'ratelimit:{ip}'
        
        if not cache.get(key):
            cache.set(key, 1, 60)  # 1 minuto
        else:
            count = cache.incr(key)
            if count > 100:  # 100 solicitudes por minuto
                return JsonResponse(
                    {'error': 'Rate limit exceeded'},
                    status=429
                )
        return None
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware para agregar encabezados de seguridad."""
    
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = self._get_csp_policy()
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    def _get_csp_policy(self):
        if settings.DEBUG:
            return "default-src 'self' 'unsafe-inline' 'unsafe-eval'"
        return (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' ws: wss:;"
        )

class WebSocketAuthMiddleware:
    """Middleware para autenticación de WebSocket."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            # Verificar autenticación
            try:
                token = self._get_token_from_scope(scope)
                user = await self._get_user_from_token(token)
                if not user:
                    await send({
                        'type': 'websocket.close',
                        'code': 4001
                    })
                    return
                scope['user'] = user
            except Exception as e:
                logger.error('WebSocket auth error', exc_info=e)
                await send({
                    'type': 'websocket.close',
                    'code': 4002
                })
                return
                
        return await self.app(scope, receive, send)
    
    def _get_token_from_scope(self, scope):
        # Implementar extracción de token desde headers o query params
        pass
    
    async def _get_user_from_token(self, token):
        # Implementar validación de token y obtención de usuario
        pass