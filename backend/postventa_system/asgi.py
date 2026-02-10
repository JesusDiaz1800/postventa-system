"""
ASGI config for postventa_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from typing import Any, Dict

# Configurar Django antes de importar cualquier modelo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# Ahora podemos importar los modelos de Django de forma segura
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.db import close_old_connections

import apps.notifications.routing

class CloseConnectionsMiddleware(BaseMiddleware):
    """Middleware para cerrar conexiones a la base de datos"""
    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        try:
            await super().__call__(scope, receive, send)
        finally:
            await database_sync_to_async(close_old_connections)()


class QueryAuthMiddleware(BaseMiddleware):
    """Middleware para autenticación por token en query params"""
    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        try:
            # Obtener token de los query params
            query_string = scope.get('query_string', b'').decode()
            query_params = dict(param.split('=') for param in query_string.split('&') if param)
            token = query_params.get('token')

            if token:
                # Autenticar usuario por token
                user = await database_sync_to_async(self.get_user_from_token)(token)
                if user:
                    scope['user'] = user
                else:
                    scope['user'] = None
            
            return await super().__call__(scope, receive, send)
            
        except Exception as e:
            print(f'Error en QueryAuthMiddleware: {str(e)}')
            scope['user'] = None
            return await super().__call__(scope, receive, send)
    
    def get_user_from_token(self, token: str) -> User:
        """Obtener usuario a partir del token JWT"""
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # Decodificar y validar token JWT
            access_token = AccessToken(token)
            user_id = access_token.get('user_id')
            
            if user_id:
                return User.objects.get(id=user_id)
            return None
        except Exception as e:
            print(f'Error validando JWT token: {str(e)}')
            return None


class ConcurrentConnectionsMiddleware(BaseMiddleware):
    """Middleware para limitar conexiones concurrentes por usuario"""
    def __init__(self, inner):
        super().__init__(inner)
        from collections import defaultdict
        self.connections = defaultdict(int)
        self.max_connections = 5  # Máximo de conexiones por usuario
    
    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        try:
            user = scope.get('user')
            if not user or not user.is_authenticated:
                return await super().__call__(scope, receive, send)
            
            # Verificar límite de conexiones
            user_id = user.id
            if self.connections[user_id] >= self.max_connections:
                # Rechazar nueva conexión si se excede el límite
                await send({
                    'type': 'websocket.close',
                    'code': 1008,
                    'reason': 'Too many connections'
                })
                return
            
            # Incrementar contador de conexiones
            self.connections[user_id] += 1
            
            try:
                return await super().__call__(scope, receive, send)
            finally:
                # Decrementar contador al cerrar
                if self.connections[user_id] > 0:
                    self.connections[user_id] -= 1
                if self.connections[user_id] == 0:
                    del self.connections[user_id]
                    
        except Exception as e:
            print(f'Error en ConcurrentConnectionsMiddleware: {str(e)}')
            return await super().__call__(scope, receive, send)


# Configuración completa con middleware para WebSocket
websocket_middleware = CloseConnectionsMiddleware(
    QueryAuthMiddleware(
        ConcurrentConnectionsMiddleware(
            AuthMiddlewareStack(
                URLRouter(
                    apps.notifications.routing.websocket_urlpatterns
                )
            )
        )
    )
)

# Configuración final optimizada
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_middleware,
})