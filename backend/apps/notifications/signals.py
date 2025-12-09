from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.incidents.models import Incident
from apps.documents.models import Document
from .models import Notification, NotificationPreferences, NotificationCategory
from .utils import send_notification, send_system_alert

User = get_user_model()


@receiver(post_save, sender=Incident)
def handle_incident_notification(sender, instance, created, **kwargs):
    """Generar notificaciones para incidencias"""
    try:
        # Obtener o crear categoría para incidencias
        category, _ = NotificationCategory.objects.get_or_create(
            name='incidents',
            defaults={
                'description': 'Notificaciones relacionadas con incidencias',
                'icon': 'warning',
                'color': '#ff9800'
            }
        )
        
        if created:
            # Notificar al creador
            send_notification(
                user=instance.created_by,
                title='Incidencia creada',
                message=f'Se ha creado la incidencia {instance.code}',
                notification_type='incident_created',
                category=category,
                is_important=True,
                related_incident=instance,
                metadata={
                    'incident_id': instance.id,
                    'code': instance.code,
                    'obra': instance.obra,
                    'cliente': instance.cliente,
                    'priority': instance.prioridad                }
            )
            
            # Notificar a los asignados
            if instance.assigned_to:
                send_notification(
                    user=instance.assigned_to,
                    title='Nueva incidencia asignada',
                    message=f'Se te ha asignado la incidencia {instance.code}',
                    notification_type='user_assigned',
                    category=category,
                    is_important=True,
                    related_incident=instance,
                    related_user=instance.created_by,
                    metadata={
                        'incident_id': instance.id,
                        'code': instance.code,
                        'obra': instance.obra,
                        'cliente': instance.cliente,
                        'priority': instance.prioridad                    }
                )
        else:
            # Verificar cambios en campos importantes
            important_changes = []
            if hasattr(instance, '_old_values'):
                old_values = instance._old_values
                fields_to_check = {
                    'estado': 'estado',
                    'prioridad': 'prioridad',
                    'assigned_to': 'asignado',
                }
                
                for field, label in fields_to_check.items():
                    old_val = old_values.get(field)
                    new_val = getattr(instance, field, None)
                    if old_val != new_val:
                        important_changes.append({
                            'field': label,
                            'old_value': str(old_val) if old_val else '',
                            'new_value': str(new_val) if new_val else ''
                        })
            
            if important_changes:
                changes_text = '\n'.join([f"{c['field']}: {c['old_value']} → {c['new_value']}" 
                                         for c in important_changes])
                
                # Notificar cambios importantes a involucrados
                users_to_notify = {
                    instance.created_by,
                    instance.assigned_to,
                }
                # Agregar last_modified_by si existe
                if hasattr(instance, 'last_modified_by') and instance.last_modified_by:
                    users_to_notify.add(instance.last_modified_by)
                users_to_notify.discard(None)
                
                for user in users_to_notify:
                    send_notification(
                        user=user,
                        title=f'Incidencia {instance.code} actualizada',                        message=f'Se han realizado los siguientes cambios:\n{changes_text}',
                        notification_type='incident_updated',
                        category=category,
                        related_incident=instance,
                        related_user=getattr(instance, 'last_modified_by', None),
                        metadata={
                            'incident_id': instance.id,
                            'code': instance.code,
                            'obra': instance.obra,
                            'cliente': instance.cliente,                            'changes': important_changes
                        }
                    )
            
            # Notificar escalamientos
            if instance.prioridad in ['alta', 'critica']:
                users_to_notify = set(User.objects.filter(
                    groups__name__in=['managers', 'supervisors']
                ).distinct())
                
                for user in users_to_notify:
                    send_notification(
                        user=user,
                        title=f'Incidencia {instance.code} escalada',
                        message=f'La incidencia ha sido escalada a prioridad {instance.get_prioridad_display()}',
                        notification_type='incident_escalated',
                        category=category,
                        is_important=True,
                        related_incident=instance,
                        related_user=getattr(instance, 'last_modified_by', None),
                        metadata={
                            'incident_id': instance.id,
                            'code': instance.code,
                            'obra': instance.obra,
                            'cliente': instance.cliente,
                            'priority': instance.prioridad
                        }
                    )
                    
    except Exception as e:
        print(f'Error al generar notificación de incidencia: {str(e)}')


@receiver(pre_save, sender=Incident)
def track_incident_changes(sender, instance, **kwargs):
    """Rastrear cambios en campos importantes de incidencias"""
    if instance.pk:
        try:
            old_instance = Incident.objects.get(pk=instance.pk)
            instance._old_values = {
                'estado': old_instance.estado,
                'prioridad': old_instance.prioridad,
                'assigned_to': old_instance.assigned_to,            }
        except Incident.DoesNotExist:
            instance._old_values = {}



@receiver(post_save, sender=Document)
def handle_document_notification(sender, instance, created, **kwargs):
    """Generar notificaciones para documentos"""
    try:
        # Obtener o crear categoría para documentos
        category, _ = NotificationCategory.objects.get_or_create(
            name='documents',
            defaults={
                'description': 'Notificaciones relacionadas con documentos',
                'icon': 'description',
                'color': '#2196f3'
            }
        )
        
        if created:
            # Notificar al creador
            send_notification(
                user=instance.created_by,
                title='Documento subido',
                message=f'Se ha subido el documento: {instance.title}',
                notification_type='document_uploaded',
                category=category,
                related_document=instance,
                metadata={
                    'document_id': instance.id,
                    'title': instance.title,
                    'type': instance.document_type
                }
            )
            
            # Notificar a los revisores si requiere aprobación
            if instance.requires_approval:
                reviewers = User.objects.filter(groups__name='document_reviewers')
                
                for reviewer in reviewers:
                    send_notification(
                        user=reviewer,
                        title='Documento requiere revisión',
                        message=f'El documento {instance.title} requiere su revisión',
                        notification_type='document_uploaded',
                        category=category,
                        is_important=True,
                        related_document=instance,
                        related_user=instance.created_by,
                        metadata={
                            'document_id': instance.id,
                            'title': instance.title,
                            'type': instance.document_type
                        }
                    )
        
        else:
            # Verificar cambios de estado
            if hasattr(instance, '_old_values') and instance._old_values.get('status') != instance.status:
                if instance.status == 'approved':
                    msg = 'aprobado'
                    notification_type = 'document_approved'
                elif instance.status == 'rejected':
                    msg = 'rechazado'
                    notification_type = 'document_rejected'
                else:
                    msg = f'actualizado a {instance.get_status_display()}'
                    notification_type = 'document_updated'
                
                send_notification(
                    user=instance.created_by,
                    title=f'Documento {instance.title} {msg}',
                    message=f'El documento ha sido {msg}',
                    notification_type=notification_type,
                    category=category,
                    related_document=instance,
                    related_user=instance.last_modified_by,
                    metadata={
                        'document_id': instance.id,
                        'title': instance.title,
                        'old_status': instance._old_values.get('status'),
                        'new_status': instance.status
                    }
                )
                    
    except Exception as e:
        print(f'Error al generar notificación de documento: {str(e)}')


@receiver(pre_save, sender=Document)
def track_document_changes(sender, instance, **kwargs):
    """Rastrear cambios en documentos"""
    if instance.pk:
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            instance._old_values = {
                'status': old_instance.status,
                'title': old_instance.title,
                'document_type': old_instance.document_type
            }
        except Document.DoesNotExist:
            instance._old_values = {}


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Crear preferencias por defecto para nuevos usuarios"""
    try:
        if created:
            NotificationPreferences.objects.create(user=instance)
            
            # Notificar a administradores
            admins = User.objects.filter(is_superuser=True)
            
            for admin in admins:
                send_notification(
                    user=admin,
                    title='Nuevo usuario registrado',
                    message=f'El usuario {instance.get_full_name()} se ha registrado en el sistema',
                    notification_type='user_registered',
                    is_system=True,
                    metadata={
                        'user_id': instance.id,
                        'username': instance.username,
                        'email': instance.email
                    }
                )
                
    except Exception as e:
        print(f'Error al crear preferencias de notificación: {str(e)}')
@receiver(post_save, sender=Incident)
def check_deadline_notifications(sender, instance, created, **kwargs):
    """Verificar notificaciones de fecha límite"""
    # Nota: El modelo Incident no tiene campo due_date actualmente
    # Esta función se mantiene para futuras implementaciones
    try:
        # Si en el futuro se agrega un campo due_date, se puede implementar aquí
        pass
    except Exception as e:
        print(f'Error al verificar notificaciones de fecha límite: {str(e)}')
