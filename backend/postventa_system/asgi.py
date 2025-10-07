"""
ASGI config for postventa_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from typing import Any, Dict

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.db import close_old_connections

import apps.notifications.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.core.settings')

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
        """Obtener usuario a partir del token"""
        from rest_framework.authtoken.models import Token
        try:
            return Token.objects.get(key=token).user
        except:
            return None


class ConcurrentConnectionsMiddleware(BaseMiddleware):
    """Middleware para limitar conexiones concurrentes por usuario"""
    def __init__(self, inner):
        super().__init__(inner)
        from collections import defaultdict
        self.connections = defaultdict(set)
        self.max_connections = 5  # Máximo de conexiones por usuario
    
    async def __call__(self, scope: Dict[str, Any], receive: Any, send: Any) -> None:
        try:
            user = scope.get('user')
            if not user or not user.is_authenticated:
                return await super().__call__(scope, receive, send)
            
            # Verificar límite de conexiones
            user_connections = self.connections[user.id]
            if len(user_connections) >= self.max_connections:
                # Cerrar conexión más antigua
                oldest_socket = list(user_connections)[0]
                await oldest_socket.close()
                user_connections.remove(oldest_socket)
            
            # Agregar nueva conexión
            user_connections.add(scope['socket'])
            
            try:
                return await super().__call__(scope, receive, send)
            finally:
                # Limpiar al cerrar
                if scope['socket'] in user_connections:
                    user_connections.remove(scope['socket'])
                if not user_connections:
                    del self.connections[user.id]
                    
        except Exception as e:
            print(f'Error en ConcurrentConnectionsMiddleware: {str(e)}')
            return await super().__call__(scope, receive, send)


# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Define la cadena de middleware
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

# Configuración final
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_middleware,
})