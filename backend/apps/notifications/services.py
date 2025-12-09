<<<<<<< HEAD
from django.contrib.auth.models import User
from django.utils import timezone
import json
from .models import Notification, NotificationPreference

try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False
    get_channel_layer = None
    async_to_sync = None

try:
    from .views import send_email_notification, send_sms_notification
except ImportError:
    def send_email_notification(notification):
        print(f"Email notification: {notification.title} - {notification.message}")
    
    def send_sms_notification(notification):
        print(f"SMS notification: {notification.title} - {notification.message}")


class NotificationService:
    """Servicio para gestión de notificaciones"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type, 
                          is_important=False, related_incident=None, 
                          related_document=None, related_user=None, metadata=None):
        """Crear notificación y enviarla por WebSocket"""
        notification = Notification.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            is_important=is_important,
            related_incident=related_incident,
            related_document=related_document,
            related_user=related_user,
            metadata=metadata or {}
        )
        
        # Enviar por WebSocket
        NotificationService.send_websocket_notification(notification)
        
        # Enviar por email si está habilitado
        send_email_notification(notification)
        
        # Enviar por SMS si está habilitado
        send_sms_notification(notification)
        
        return notification
    
    @staticmethod
    def send_websocket_notification(notification):
        """Enviar notificación por WebSocket"""
        try:
            if not CHANNELS_AVAILABLE:
                print(f"WebSocket notification (channels not available): {notification.title} - {notification.message}")
                return
                
            channel_layer = get_channel_layer()
            if channel_layer:
                # Preparar datos de la notificación
=======
"""
Servicio de Notificaciones en Tiempo Real
Maneja la creación y envío de notificaciones automáticas
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, NotificationCategory
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """Servicio centralizado para gestión de notificaciones"""
    
    @staticmethod
    def create_notification(
        user: User,
        title: str,
        message: str,
        notification_type: str,
        category: Optional[str] = None,
        is_important: bool = False,
        is_system: bool = False,
        related_incident_id: Optional[int] = None,
        related_document_id: Optional[int] = None,
        related_user: Optional[User] = None,
        metadata: Optional[Dict[str, Any]] = None,
        related_url: Optional[str] = None
    ) -> Notification:
        """
        Crear una nueva notificación
        
        Args:
            user: Usuario destinatario
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo de notificación
            category: Categoría de la notificación
            is_important: Si es importante
            is_system: Si es del sistema
            related_incident_id: ID de incidencia relacionada
            related_document_id: ID de documento relacionado
            related_user: Usuario relacionado
            metadata: Metadatos adicionales
            related_url: URL relacionada
            
        Returns:
            Notification: Notificación creada
        """
        try:
            # Obtener categoría si se especifica
            category_obj = None
            if category:
                category_obj, _ = NotificationCategory.objects.get_or_create(
                    name=category,
                    defaults={
                        'description': f'Categoría {category}',
                        'is_active': True
                    }
                )
            
            # Crear notificación
            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                category=category_obj,
                is_important=is_important,
                is_system=is_system,
                related_incident_id=related_incident_id,
                related_document_id=related_document_id,
                related_user=related_user,
                metadata=metadata or {},
                related_url=related_url
            )
            
            # Enviar por WebSocket
            NotificationService.send_websocket_notification(notification)
            
            logger.info(f'Notificación creada: {notification.id} para usuario {user.username}')
            return notification
            
        except Exception as e:
            logger.error(f'Error creando notificación: {str(e)}')
            raise
    
    @staticmethod
    def send_websocket_notification(notification: Notification):
        """Enviar notificación por WebSocket"""
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                group_name = f'user_{notification.user.id}'
                
>>>>>>> 674c244 (tus cambios)
                notification_data = {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'notification_type': notification.notification_type,
                    'is_read': notification.is_read,
                    'is_important': notification.is_important,
                    'created_at': notification.created_at.isoformat(),
                    'time_ago': NotificationService.calculate_time_ago(notification.created_at),
<<<<<<< HEAD
                           'related_incident_id': notification.related_incident_id,
                           'related_document_id': notification.related_document_id,
                    'related_user': {
                        'id': notification.related_user.id,
                        'username': notification.related_user.username,
                        'first_name': notification.related_user.first_name,
                        'last_name': notification.related_user.last_name
                    } if notification.related_user else None,
                    'metadata': notification.metadata
                }
                
                # Enviar al grupo del usuario
                async_to_sync(channel_layer.group_send)(
                    f'user_{notification.user.id}',
=======
                    'related_url': notification.related_url or '',
                    'metadata': notification.metadata or {}
                }
                
                async_to_sync(channel_layer.group_send)(
                    group_name,
>>>>>>> 674c244 (tus cambios)
                    {
                        'type': 'send_notification',
                        'notification': notification_data
                    }
                )
<<<<<<< HEAD
        except Exception as e:
            print(f"Error enviando notificación WebSocket: {e}")
    
    @staticmethod
    def send_broadcast_notification(title, message, is_important=False):
        """Enviar notificación de broadcast a todos los usuarios"""
        try:
            if not CHANNELS_AVAILABLE:
                print(f"Broadcast notification (channels not available): {title} - {message}")
                return
                
            channel_layer = get_channel_layer()
            if channel_layer:
                notification_data = {
                    'title': title,
                    'message': message,
                    'is_important': is_important,
                    'timestamp': timezone.now().isoformat()
                }
                
                # Enviar al grupo de broadcast
                async_to_sync(channel_layer.group_send)(
                    'system_notifications',
                    {
                        'type': 'system_notification',
                        'notification': notification_data
                    }
                )
        except Exception as e:
            print(f"Error enviando notificación de broadcast: {e}")
    
    @staticmethod
    def calculate_time_ago(created_at):
        """Calcular tiempo transcurrido desde la creación"""
=======
                
                logger.info(f'Notificación enviada por WebSocket a {group_name}')
                
        except Exception as e:
            logger.error(f'Error enviando notificación por WebSocket: {str(e)}')
    
    @staticmethod
    def create_incident_notification(
        incident,
        action: str,
        user: Optional[User] = None
    ) -> List[Notification]:
        """
        Crear notificaciones relacionadas con incidentes
        
        Args:
            incident: Instancia del incidente
            action: Acción realizada ('created', 'updated', 'escalated', 'closed')
            user: Usuario que realizó la acción
            
        Returns:
            List[Notification]: Lista de notificaciones creadas
        """
        notifications = []
        
        # Definir mensajes según la acción
        messages = {
            'created': f'Nueva incidencia #{incident.id} creada: {incident.titulo}',
            'updated': f'Incidencia #{incident.id} actualizada: {incident.titulo}',
            'escalated': f'Incidencia #{incident.id} escalada: {incident.titulo}',
            'closed': f'Incidencia #{incident.id} cerrada: {incident.titulo}'
        }
        
        titles = {
            'created': 'Nueva Incidencia',
            'updated': 'Incidencia Actualizada',
            'escalated': 'Incidencia Escalada',
            'closed': 'Incidencia Cerrada'
        }
        
        message = messages.get(action, f'Incidencia #{incident.id} {action}')
        title = titles.get(action, f'Incidencia {action.title()}')
        
        # Notificar al usuario asignado
        if incident.usuario_asignado:
            notification = NotificationService.create_notification(
                user=incident.usuario_asignado,
                title=title,
                message=message,
                notification_type=f'incident_{action}',
                category='incidents',
                is_important=incident.prioridad in ['alta', 'urgente'],
                related_incident_id=incident.id,
                related_user=user,
                related_url=f'/incidents/{incident.id}',
                metadata={
                    'incident_id': incident.id,
                    'incident_titulo': incident.titulo,
                    'prioridad': incident.prioridad,
                    'estado': incident.estado
                }
            )
            notifications.append(notification)
        
        # Notificar a supervisores si es importante
        if incident.prioridad in ['alta', 'urgente']:
            supervisors = User.objects.filter(
                role__in=['supervisor', 'administrador', 'admin']
            ).exclude(id=incident.usuario_asignado.id if incident.usuario_asignado else 0)
            
            for supervisor in supervisors:
                notification = NotificationService.create_notification(
                    user=supervisor,
                    title=f'⚠️ {title} - Prioridad {incident.prioridad.title()}',
                    message=f'{message} - Requiere atención inmediata',
                    notification_type=f'incident_{action}',
                    category='incidents',
                    is_important=True,
                    related_incident_id=incident.id,
                    related_user=user,
                    related_url=f'/incidents/{incident.id}',
                    metadata={
                        'incident_id': incident.id,
                        'incident_titulo': incident.titulo,
                        'prioridad': incident.prioridad,
                        'estado': incident.estado,
                        'es_escalado': True
                    }
                )
                notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def create_document_notification(
        document,
        action: str,
        user: Optional[User] = None
    ) -> Notification:
        """
        Crear notificación relacionada con documentos
        
        Args:
            document: Instancia del documento
            action: Acción realizada ('uploaded', 'approved', 'rejected')
            user: Usuario que realizó la acción
            
        Returns:
            Notification: Notificación creada
        """
        messages = {
            'uploaded': f'Documento subido: {document.nombre}',
            'approved': f'Documento aprobado: {document.nombre}',
            'rejected': f'Documento rechazado: {document.nombre}'
        }
        
        titles = {
            'uploaded': 'Documento Subido',
            'approved': 'Documento Aprobado',
            'rejected': 'Documento Rechazado'
        }
        
        message = messages.get(action, f'Documento {action}')
        title = titles.get(action, f'Documento {action.title()}')
        
        return NotificationService.create_notification(
            user=document.usuario,
            title=title,
            message=message,
            notification_type=f'document_{action}',
            category='documents',
            is_important=action == 'rejected',
            related_document_id=document.id,
            related_user=user,
            related_url=f'/documents/{document.id}',
            metadata={
                'document_id': document.id,
                'document_nombre': document.nombre,
                'document_tipo': getattr(document, 'tipo', 'unknown')
            }
        )
    
    @staticmethod
    def create_system_notification(
        message: str,
        title: str = 'Notificación del Sistema',
        is_important: bool = False,
        target_users: Optional[List[User]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """
        Crear notificación del sistema
        
        Args:
            message: Mensaje de la notificación
            title: Título de la notificación
            is_important: Si es importante
            target_users: Usuarios objetivo (si no se especifica, se envía a todos)
            metadata: Metadatos adicionales
            
        Returns:
            List[Notification]: Lista de notificaciones creadas
        """
        notifications = []
        
        if target_users is None:
            target_users = User.objects.filter(is_active=True)
        
        for user in target_users:
            notification = NotificationService.create_notification(
                user=user,
                title=title,
                message=message,
                notification_type='system_alert',
                category='system',
                is_important=is_important,
                is_system=True,
                metadata=metadata or {}
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def create_deadline_notification(
        incident,
        days_remaining: int
    ) -> Notification:
        """
        Crear notificación de fecha límite
        
        Args:
            incident: Instancia del incidente
            days_remaining: Días restantes
            
        Returns:
            Notification: Notificación creada
        """
        if days_remaining <= 0:
            message = f'⚠️ Fecha límite excedida para incidencia #{incident.id}: {incident.titulo}'
            title = 'Fecha Límite Excedida'
            is_important = True
            notification_type = 'deadline_exceeded'
        else:
            message = f'📅 Fecha límite próxima para incidencia #{incident.id}: {incident.titulo} ({days_remaining} días restantes)'
            title = 'Fecha Límite Próxima'
            is_important = days_remaining <= 2
            notification_type = 'deadline_approaching'
        
        return NotificationService.create_notification(
            user=incident.usuario_asignado,
            title=title,
            message=message,
            notification_type=notification_type,
            category='deadlines',
            is_important=is_important,
            related_incident_id=incident.id,
            related_url=f'/incidents/{incident.id}',
            metadata={
                'incident_id': incident.id,
                'incident_titulo': incident.titulo,
                'days_remaining': days_remaining,
                'fecha_limite': incident.fecha_limite.isoformat() if incident.fecha_limite else None
            }
        )
    
    @staticmethod
    def calculate_time_ago(created_at) -> str:
        """Calcular tiempo transcurrido"""
        from django.utils import timezone
>>>>>>> 674c244 (tus cambios)
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
    
    @staticmethod
<<<<<<< HEAD
    def notify_incident_created(incident, created_by):
        """Notificar creación de incidencia"""
        # Notificar al usuario asignado si es diferente del creador
        if incident.assigned_to and incident.assigned_to != created_by:
            NotificationService.create_notification(
                user=incident.assigned_to,
                title=f"Nueva Incidencia Asignada: {incident.title}",
                message=f"Se te ha asignado la incidencia {incident.code}: {incident.title}",
                notification_type='incident_created',
                is_important=(incident.priority == 'Alta'),
                related_incident=incident,
                related_user=created_by
            )
        
        # Notificar a supervisores si es de alta prioridad
        if incident.priority == 'Alta':
            supervisors = User.objects.filter(
                groups__name='Supervisores'
            ).exclude(id=created_by.id)
            
            for supervisor in supervisors:
                NotificationService.create_notification(
                    user=supervisor,
                    title=f"Incidencia de Alta Prioridad: {incident.title}",
                    message=f"Se ha creado una incidencia de alta prioridad {incident.code}",
                    notification_type='incident_created',
                    is_important=True,
                    related_incident=incident,
                    related_user=created_by
                )
    
    @staticmethod
    def notify_incident_updated(incident, updated_by, changes):
        """Notificar actualización de incidencia"""
        # Notificar al usuario asignado
        if incident.assigned_to:
            NotificationService.create_notification(
                user=incident.assigned_to,
                title=f"Incidencia Actualizada: {incident.title}",
                message=f"La incidencia {incident.code} ha sido actualizada",
                notification_type='incident_updated',
                related_incident=incident,
                related_user=updated_by,
                metadata={'changes': changes}
            )
    
    @staticmethod
    def notify_incident_escalated(incident, escalated_by, escalation_type):
        """Notificar escalación de incidencia"""
        # Notificar al usuario asignado
        if incident.assigned_to:
            NotificationService.create_notification(
                user=incident.assigned_to,
                title=f"Incidencia Escalada: {incident.title}",
                message=f"La incidencia {incident.code} ha sido escalada a {escalation_type}",
                notification_type='incident_escalated',
                is_important=True,
                related_incident=incident,
                related_user=escalated_by
            )
        
        # Notificar al equipo correspondiente según el tipo de escalación
        if escalation_type == 'Calidad':
            quality_team = User.objects.filter(groups__name='Equipo de Calidad')
            for user in quality_team:
                NotificationService.create_notification(
                    user=user,
                    title=f"Incidencia Escalada a Calidad: {incident.title}",
                    message=f"La incidencia {incident.code} ha sido escalada a tu equipo",
                    notification_type='incident_escalated',
                    is_important=True,
                    related_incident=incident,
                    related_user=escalated_by
                )
    
    @staticmethod
    def notify_incident_closed(incident, closed_by):
        """Notificar cierre de incidencia"""
        # Notificar al creador de la incidencia
        if incident.created_by:
            NotificationService.create_notification(
                user=incident.created_by,
                title=f"Incidencia Cerrada: {incident.title}",
                message=f"La incidencia {incident.code} ha sido cerrada",
                notification_type='incident_closed',
                related_incident=incident,
                related_user=closed_by
            )
        
        # Notificar al usuario asignado si es diferente del que cerró
        if incident.assigned_to and incident.assigned_to != closed_by:
            NotificationService.create_notification(
                user=incident.assigned_to,
                title=f"Incidencia Cerrada: {incident.title}",
                message=f"La incidencia {incident.code} ha sido cerrada",
                notification_type='incident_closed',
                related_incident=incident,
                related_user=closed_by
            )
    
    @staticmethod
    def notify_document_uploaded(document, uploaded_by):
        """Notificar subida de documento"""
        # Notificar al creador de la incidencia relacionada
        if document.related_incident and document.related_incident.created_by:
            NotificationService.create_notification(
                user=document.related_incident.created_by,
                title=f"Documento Subido: {document.title}",
                message=f"Se ha subido un documento para la incidencia {document.related_incident.code}",
                notification_type='document_uploaded',
                related_document=document,
                related_incident=document.related_incident,
                related_user=uploaded_by
            )
        
        # Notificar al usuario asignado de la incidencia
        if document.related_incident and document.related_incident.assigned_to:
            NotificationService.create_notification(
                user=document.related_incident.assigned_to,
                title=f"Documento Subido: {document.title}",
                message=f"Se ha subido un documento para la incidencia {document.related_incident.code}",
                notification_type='document_uploaded',
                related_document=document,
                related_incident=document.related_incident,
                related_user=uploaded_by
            )
    
    @staticmethod
    def notify_document_approved(document, approved_by):
        """Notificar aprobación de documento"""
        NotificationService.create_notification(
            user=document.created_by,
            title=f"Documento Aprobado: {document.title}",
            message=f"Tu documento {document.title} ha sido aprobado",
            notification_type='document_approved',
            related_document=document,
            related_user=approved_by
        )
    
    @staticmethod
    def notify_document_rejected(document, rejected_by, reason=None):
        """Notificar rechazo de documento"""
        NotificationService.create_notification(
            user=document.created_by,
            title=f"Documento Rechazado: {document.title}",
            message=f"Tu documento {document.title} ha sido rechazado{f': {reason}' if reason else ''}",
            notification_type='document_rejected',
            related_document=document,
            related_user=rejected_by,
            metadata={'reason': reason} if reason else {}
        )
    
    @staticmethod
    def notify_user_assigned(user, assigned_by, assignment_type, related_object):
        """Notificar asignación de usuario"""
        title = f"Has sido asignado a {assignment_type}"
        message = f"Se te ha asignado a {assignment_type}"
        
        if assignment_type == 'Incidencia':
            message = f"Se te ha asignado la incidencia {related_object.code}: {related_object.title}"
        elif assignment_type == 'Documento':
            message = f"Se te ha asignado el documento {related_object.title}"
        
        NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type='user_assigned',
            related_user=assigned_by,
            metadata={'assignment_type': assignment_type}
        )
    
    @staticmethod
    def notify_deadline_approaching(incident, days_remaining):
        """Notificar fecha límite próxima"""
        NotificationService.create_notification(
            user=incident.assigned_to,
            title=f"Fecha Límite Próxima: {incident.title}",
            message=f"La incidencia {incident.code} tiene {days_remaining} días restantes",
            notification_type='deadline_approaching',
            is_important=(days_remaining <= 1),
            related_incident=incident
        )
    
    @staticmethod
    def notify_deadline_exceeded(incident):
        """Notificar fecha límite excedida"""
        NotificationService.create_notification(
            user=incident.assigned_to,
            title=f"Fecha Límite Excedida: {incident.title}",
            message=f"La incidencia {incident.code} ha excedido su fecha límite",
            notification_type='deadline_exceeded',
            is_important=True,
            related_incident=incident
        )
        
        # Notificar a supervisores
        supervisors = User.objects.filter(groups__name='Supervisores')
        for supervisor in supervisors:
            NotificationService.create_notification(
                user=supervisor,
                title=f"Fecha Límite Excedida: {incident.title}",
                message=f"La incidencia {incident.code} ha excedido su fecha límite",
                notification_type='deadline_exceeded',
                is_important=True,
                related_incident=incident
            )
    
    @staticmethod
    def send_system_alert(title, message, is_important=False):
        """Enviar alerta del sistema"""
        NotificationService.create_notification(
            user=User.objects.filter(is_superuser=True).first(),
            title=title,
            message=message,
            notification_type='system_alert',
            is_important=is_important
        )
        
        # También enviar por broadcast
        NotificationService.send_broadcast_notification(title, message, is_important)
    
    @staticmethod
    def cleanup_old_notifications(days=30):
        """Limpiar notificaciones antiguas"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()[0]
        
        return deleted_count
=======
    def cleanup_old_notifications(days: int = 30):
        """
        Limpiar notificaciones antiguas
        
        Args:
            days: Días de antigüedad para eliminar
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True,
            is_important=False
        ).delete()[0]
        
        logger.info(f'Limpiadas {deleted_count} notificaciones antiguas')
        return deleted_count


# Funciones de conveniencia para uso en signals
def notify_incident_created(sender, instance, created, **kwargs):
    """Signal handler para cuando se crea una incidencia"""
    if created:
        NotificationService.create_incident_notification(instance, 'created')


def notify_incident_updated(sender, instance, **kwargs):
    """Signal handler para cuando se actualiza una incidencia"""
    if instance.pk:  # Solo si ya existe
        NotificationService.create_incident_notification(instance, 'updated')


def notify_document_uploaded(sender, instance, created, **kwargs):
    """Signal handler para cuando se sube un documento"""
    if created:
        NotificationService.create_document_notification(instance, 'uploaded')
>>>>>>> 674c244 (tus cambios)
