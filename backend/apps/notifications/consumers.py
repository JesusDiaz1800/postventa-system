import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Notification, NotificationPreferences

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Conectar usuario al WebSocket"""
        try:
            self.user = self.scope['user']
            self.user_id = self.user.id if self.user.is_authenticated else None
            
            if not self.user_id:
                await self.close(code=4001)
                return
            
            # Unirse al grupo del usuario
            self.group_name = f'user_{self.user_id}'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Enviar notificaciones no leídas al conectar
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected successfully',
                'unread_count': unread_count
            }))
        except Exception as e:
            print(f'Error en conexión WebSocket: {str(e)}')
            await self.close(code=4002)
    
    async def disconnect(self, close_code):
        """Desconectar usuario del WebSocket"""
        try:
            if hasattr(self, 'group_name'):
                await self.channel_layer.group_discard(
                    self.group_name,
                    self.channel_name
                )
        except Exception as e:
            print(f'Error en desconexión WebSocket: {str(e)}')
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            handlers = {
                'mark_as_read': self._handle_mark_as_read,
                'mark_all_as_read': self._handle_mark_all_as_read,
                'get_notifications': self._handle_get_notifications,
                'get_unread_count': self._handle_get_unread_count,
                'get_important': self._handle_get_important,
                'mark_as_important': self._handle_mark_as_important
            }
            
            handler = handlers.get(message_type)
            if handler:
                await handler(text_data_json)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Tipo de mensaje desconocido: {message_type}'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato JSON inválido'
            }))
        except Exception as e:
            print(f'Error en receive: {str(e)}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error interno del servidor'
            }))
    
    async def _handle_mark_as_read(self, data):
        notification_id = data.get('notification_id')
        if not notification_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'ID de notificación requerido'
            }))
            return
            
        success = await self.mark_notification_as_read(notification_id)
        if success:
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'success',
                'message': 'Notificación marcada como leída',
                'unread_count': unread_count
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Notificación no encontrada'
            }))
    
    async def _handle_mark_all_as_read(self, data):
        await self.mark_all_as_read()
        await self.send(text_data=json.dumps({
            'type': 'success',
            'message': 'Todas las notificaciones marcadas como leídas',
            'unread_count': 0
        }))
    
    async def _handle_get_notifications(self, data):
        limit = data.get('limit', 10)
        page = data.get('page', 1)
        filter_type = data.get('filter_type')  # 'all', 'unread', 'important'
        
        try:
            notifications = await self.get_recent_notifications(limit, page, filter_type)
            total_count = await self.get_total_notifications_count(filter_type)
            
            await self.send(text_data=json.dumps({
                'type': 'notifications_list',
                'notifications': notifications,
                'total_count': total_count,
                'page': page,
                'total_pages': (total_count + limit - 1) // limit
            }))
        except Exception as e:
            print(f'Error al obtener notificaciones: {str(e)}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error al obtener notificaciones'
            }))
    
    async def _handle_get_unread_count(self, data):
        try:
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': unread_count
            }))
        except Exception as e:
            print(f'Error al obtener conteo: {str(e)}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error al obtener conteo'
            }))
    
    async def _handle_get_important(self, data):
        try:
            important_notifications = await self.get_important_notifications()
            await self.send(text_data=json.dumps({
                'type': 'important_notifications',
                'notifications': important_notifications
            }))
        except Exception as e:
            print(f'Error al obtener importantes: {str(e)}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error al obtener notificaciones importantes'
            }))
    
    async def _handle_mark_as_important(self, data):
        notification_id = data.get('notification_id')
        important = data.get('important', True)
        
        if not notification_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'ID de notificación requerido'
            }))
            return
            
        success = await self.mark_notification_as_important(notification_id, important)
        if success:
            await self.send(text_data=json.dumps({
                'type': 'success',
                'message': f'Notificación marcada como {"importante" if important else "no importante"}'
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Notificación no encontrada'
            }))
    
    async def send_notification(self, event):
        """Enviar notificación al usuario"""
        notification_data = event['notification']
        
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': notification_data
        }))
        
        # Actualizar conteo de no leídas
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'count': unread_count
        }))
    
    async def notification_updated(self, event):
        """Notificar cuando se actualiza una notificación"""
        notification_data = event['notification']
        
        await self.send(text_data=json.dumps({
            'type': 'notification_updated',
            'notification': notification_data
        }))
    
    async def notification_deleted(self, event):
        """Notificar cuando se elimina una notificación"""
        notification_id = event['notification_id']
        
        await self.send(text_data=json.dumps({
            'type': 'notification_deleted',
            'notification_id': notification_id
        }))
        
        # Actualizar conteo de no leídas
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count_update',
            'count': unread_count
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Obtener conteo de notificaciones no leídas"""
        try:
            return Notification.objects.filter(user=self.user, is_read=False).count()
        except Exception as e:
            print(f'Error al obtener conteo no leídas: {str(e)}')
            return 0
    
    @database_sync_to_async
    def get_recent_notifications(self, limit=10, page=1, filter_type=None):
        """Obtener notificaciones recientes con paginación y filtros"""
        try:
            offset = (page - 1) * limit
            queryset = Notification.objects.filter(user=self.user)
            
            if filter_type == 'unread':
                queryset = queryset.filter(is_read=False)
            elif filter_type == 'important':
                queryset = queryset.filter(is_important=True)
            
            notifications = queryset.order_by('-created_at')[offset:offset + limit]
            
            return [
                {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'is_read': notification.is_read,
                    'is_important': notification.is_important,
                    'created_at': notification.created_at.isoformat(),
                    'time_ago': self.calculate_time_ago(notification.created_at),
                    'related_url': notification.related_url or '',
                    'metadata': notification.metadata or {}
                }
                for notification in notifications
            ]
        except Exception as e:
            print(f'Error al obtener notificaciones: {str(e)}')
            return []
    
    @database_sync_to_async
    def get_total_notifications_count(self, filter_type=None):
        """Obtener conteo total de notificaciones según filtro"""
        try:
            queryset = Notification.objects.filter(user=self.user)
            
            if filter_type == 'unread':
                queryset = queryset.filter(is_read=False)
            elif filter_type == 'important':
                queryset = queryset.filter(is_important=True)
                
            return queryset.count()
        except Exception as e:
            print(f'Error al obtener conteo total: {str(e)}')
            return 0
    
    @database_sync_to_async
    def get_important_notifications(self):
        """Obtener notificaciones importantes"""
        try:
            notifications = Notification.objects.filter(
                user=self.user,
                is_important=True
            ).order_by('-created_at')[:5]
            
            return [
                {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'time_ago': self.calculate_time_ago(notification.created_at)
                }
                for notification in notifications
            ]
        except Exception as e:
            print(f'Error al obtener notificaciones importantes: {str(e)}')
            return []
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Marcar notificación como leída"""
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.mark_as_read()
            notification.save(update_fields=['is_read', 'updated_at'])
            return True
        except Notification.DoesNotExist:
            return False
        except Exception as e:
            print(f'Error al marcar como leída: {str(e)}')
            return False
    
    @database_sync_to_async
    def mark_all_as_read(self):
        """Marcar todas las notificaciones como leídas"""
        try:
            Notification.objects.filter(user=self.user, is_read=False).update(
                is_read=True,
                updated_at=timezone.now()
            )
            return True
        except Exception as e:
            print(f'Error al marcar todas como leídas: {str(e)}')
            return False
    
    @database_sync_to_async
    def mark_notification_as_important(self, notification_id, important=True):
        """Marcar notificación como importante o no importante"""
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.is_important = important
            notification.save(update_fields=['is_important', 'updated_at'])
            return True
        except Notification.DoesNotExist:
            return False
        except Exception as e:
            print(f'Error al marcar como importante: {str(e)}')
            return False
    
    def calculate_time_ago(self, created_at):
        """Calcular tiempo transcurrido"""
        from django.utils import timezone
        now = timezone.now()
        diff = now - created_at
        
        if diff.days > 0:
            return f"{diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "Ahora"


class NotificationBroadcastConsumer(AsyncWebsocketConsumer):
    """Consumer para notificaciones de broadcast (sistema)"""
    
    async def connect(self):
        """Conectar al grupo de broadcast"""
        try:
            self.user = self.scope['user']
            self.user_id = self.user.id if self.user.is_authenticated else None
            
            if not self.user_id:
                await self.close(code=4001)
                return
            
            self.group_name = 'system_notifications'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            
            # Enviar mensaje de conexión exitosa
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Conectado a notificaciones del sistema'
            }))
        except Exception as e:
            print(f'Error en conexión broadcast: {str(e)}')
            await self.close(code=4002)
    
    async def disconnect(self, close_code):
        """Desconectar del grupo de broadcast"""
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            print(f'Error en desconexión broadcast: {str(e)}')
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            handlers = {
                'subscribe': self._handle_subscribe,
                'get_status': self._handle_get_status,
                'ping': self._handle_ping
            }
            
            handler = handlers.get(message_type)
            if handler:
                await handler(text_data_json)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Tipo de mensaje desconocido: {message_type}'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato JSON inválido'
            }))
        except Exception as e:
            print(f'Error en receive broadcast: {str(e)}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error interno del servidor'
            }))
    
    async def _handle_subscribe(self, data):
        """Manejar suscripción"""
        categories = data.get('categories', [])
        try:
            # Registrar categorías de interés del usuario
            await self.subscribe_to_categories(categories)
            
            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'message': 'Suscrito exitosamente',
                'categories': categories
            }))
        except Exception as e:
            print(f'Error en suscripción: {str(e)}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error al procesar suscripción'
            }))
    
    async def _handle_get_status(self, data):
        """Manejar consulta de estado"""
        try:
            system_status = await self.get_system_status()
            await self.send(text_data=json.dumps({
                'type': 'system_status',
                'status': system_status
            }))
        except Exception as e:
            print(f'Error al obtener estado: {str(e)}')
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error al obtener estado del sistema'
            }))
    
    async def _handle_ping(self, data):
        """Manejar ping para verificar conexión"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))
    
    @database_sync_to_async
    def subscribe_to_categories(self, categories):
        """Suscribir usuario a categorías de notificaciones"""
        try:
            # Actualizar preferencias del usuario
            user_preferences, created = NotificationPreferences.objects.get_or_create(
                user=self.user
            )
            user_preferences.categories = categories
            user_preferences.save()
            return True
        except Exception as e:
            print(f'Error al suscribir a categorías: {str(e)}')
            return False
    
    @database_sync_to_async
    def get_system_status(self):
        """Obtener estado del sistema"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                db_ok = True
        except:
            db_ok = False
            
        return {
            'database': 'online' if db_ok else 'offline',
            'websocket': 'online',
            'timestamp': timezone.now().isoformat(),
            'version': '2.0.0'
        }
    
    async def system_notification(self, event):
        """Enviar notificación del sistema"""
        try:
            notification = event['notification']
            
            # Verificar si el usuario está suscrito a esta categoría
            if await self.should_send_notification(notification):
                await self.send(text_data=json.dumps({
                    'type': 'system_notification',
                    'notification': notification
                }))
        except Exception as e:
            print(f'Error al enviar notificación del sistema: {str(e)}')
    
    async def system_alert(self, event):
        """Enviar alerta del sistema"""
        try:
            alert = event['alert']
            severity = alert.get('severity', 'info')
            
            await self.send(text_data=json.dumps({
                'type': 'system_alert',
                'alert': {
                    **alert,
                    'timestamp': timezone.now().isoformat()
                }
            }))
        except Exception as e:
            print(f'Error al enviar alerta del sistema: {str(e)}')
    
    @database_sync_to_async
    def should_send_notification(self, notification):
        """Verificar si se debe enviar la notificación al usuario"""
        try:
            preferences = NotificationPreferences.objects.get(user=self.user)
            notification_category = notification.get('category', 'general')
            return notification_category in preferences.categories
        except NotificationPreferences.DoesNotExist:
            return True  # Si no hay preferencias, enviar todo
        except Exception as e:
            print(f'Error al verificar preferencias: {str(e)}')
            return True
