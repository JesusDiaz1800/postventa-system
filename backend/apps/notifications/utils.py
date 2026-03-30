from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification(user, title, message, notification_type, category=None, 
                   is_important=False, is_system=False, related_incident=None, 
                   related_document=None, related_user=None, metadata=None, 
                   related_url=None):
    """
    Helper para enviar notificaciones a través de WebSocket y guardar en BD
    """
    from .models import Notification, NotificationPreferences
    
    try:
        # Crear notificación en BD
        notification = Notification.create_notification(
            user=user,
            title=title, 
            message=message,
            notification_type=notification_type,
            category=category,
            is_important=is_important,
            is_system=is_system,
            related_incident=related_incident,
            related_document=related_document,
            related_user=related_user,
            metadata=metadata,
            related_url=related_url
        )
        
        # Verificar preferencias del usuario
        try:
            preferences = NotificationPreferences.objects.get(user=user)
            if not preferences.should_notify(notification_type, is_important):
                # No enviar si el usuario lo tiene deshabilitado
                return notification
        except NotificationPreferences.DoesNotExist:
            # Si no hay preferencias, enviar por defecto
            pass
        
        # Preparar datos para WebSocket
        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'category': category.name if category else None,
            'is_important': notification.is_important,
            'is_system': notification.is_system,
            'created_at': notification.created_at.isoformat(),
            'metadata': notification.metadata,
            'related_url': notification.related_url
        }
        
        # Enviar a través de WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{user.id}',
            {
                'type': 'send_notification',
                'notification': notification_data
            }
        )
        
        # Enviar notificación del sistema si corresponde
        if is_system:
            async_to_sync(channel_layer.group_send)(
                'system_notifications',
                {
                    'type': 'system_notification',
                    'notification': notification_data
                }
            )
        
        return notification
        
    except Exception as e:
        print(f'Error al enviar notificación: {str(e)}')
        return None


def send_system_alert(title, message, severity='info', metadata=None):
    """
    Helper para enviar alertas del sistema a todos los usuarios
    """
    try:
        channel_layer = get_channel_layer()
        alert_data = {
            'title': title,
            'message': message,
            'severity': severity,
            'timestamp': timezone.now().isoformat(),
            'metadata': metadata or {}
        }
        
        async_to_sync(channel_layer.group_send)(
            'system_notifications',
            {
                'type': 'system_alert',
                'alert': alert_data
            }
        )
        
        return True
        
    except Exception as e:
        print(f'Error al enviar alerta del sistema: {str(e)}')
        return False


def send_bulk_notifications(users, title, message, notification_type, **kwargs):
    """
    Helper para enviar notificaciones en masa
    """
    notifications = []
    for user in users:
        notification = send_notification(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            **kwargs
        )
        if notification:
            notifications.append(notification)
    
    return notifications