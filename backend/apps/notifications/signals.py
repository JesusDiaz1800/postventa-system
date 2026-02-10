from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.incidents.models import Incident
from apps.documents.models import Document
from .models import Notification, NotificationPreferences, NotificationCategory
from .utils import send_notification, send_system_alert
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=Incident)
def handle_incident_notification(sender, instance, created, **kwargs):
    """Generar notificaciones para incidencias optimizadas por rol"""
    if kwargs.get('raw', False):
        return
    try:
        # Categoría
        category, _ = NotificationCategory.objects.get_or_create(
            name='incidents',
            defaults={
                'description': 'Notificaciones relacionadas con incidencias',
                'icon': 'warning',
                'color': '#ff9800'
            }
        )
        
        # Determine actor (quien hizo el cambio)
        # Esto es un aproximado ya que signals no tienen request.user
        # Se asume que last_modified_by esta seteado en el modelo
        actor = getattr(instance, 'last_modified_by', None)
        if created and hasattr(instance, 'created_by'):
             actor = instance.created_by

        # Helper para evitar auto-notificaciones salvo admin
        def should_notify(target_user):
            if not target_user: 
                return False
            # Admin siempre recibe todo (opcional: si quieres que admin TAMPOCO reciba sus propias acciones, descomenta la linea de abajo)
            # if target_user.role == 'admin': return True 
            return target_user != actor

        if created:
            # 1. Notificar Admins (Siempre)
            admins = User.objects.filter(role='admin')
            for admin in admins:
                if should_notify(admin):
                    send_notification(
                        user=admin,
                        title='Nueva incidencia creada',
                        message=f'Se ha creado la incidencia {instance.code} por {instance.created_by.full_name if instance.created_by else "Sistema"}',
                        notification_type='incident_created',
                        category=category,
                        is_important=instance.prioridad in ['alta', 'critica'],
                        related_incident=instance,
                        metadata={'incident_id': instance.id, 'code': instance.code}
                    )

            # 2. Notificar Asignado (Técnico/Supervisor)
            if instance.assigned_to and should_notify(instance.assigned_to):
                send_notification(
                    user=instance.assigned_to,
                    title='Nueva incidencia asignada',
                    message=f'Se te ha asignado la incidencia {instance.code}',
                    notification_type='user_assigned',
                    category=category,
                    is_important=True,
                    related_incident=instance,
                    related_user=instance.created_by,
                    metadata={'incident_id': instance.id, 'code': instance.code}
                )

        else:
            # Modificaciones
            changes_text = ""
            important_changes = []
            
            if hasattr(instance, '_old_values'):
                old_values = instance._old_values
                
                # Check Escalation Flags first (Priority logic)
                is_escalated_internal = getattr(instance, 'escalated_to_internal_quality', False)
                was_escalated_internal = old_values.get('escalated_to_internal_quality', False)
                
                is_escalated_supplier = getattr(instance, 'escalated_to_supplier', False)
                was_escalated_supplier = old_values.get('escalated_to_supplier', False)

                # Escalamiento a Calidad Interna
                if is_escalated_internal and not was_escalated_internal:
                    # Notify Quality + Admin
                    targets = User.objects.filter(role__in=['quality', 'admin'])
                    for target in targets:
                        if should_notify(target):
                            send_notification(
                                user=target,
                                title=f'Escalamiento a Calidad Interna',
                                message=f'La incidencia {instance.code} ha sido escalada a Calidad Interna.',
                                notification_type='incident_escalated',
                                category=category,
                                is_important=True,
                                related_incident=instance,
                                metadata={'incident_id': instance.id, 'stage': 'internal_quality'}
                            )

                # Escalamiento a Proveedor
                if is_escalated_supplier and not was_escalated_supplier:
                    # Notify Management + Admin + Quality
                    targets = User.objects.filter(role__in=['management', 'admin', 'quality'])
                    for target in targets:
                        if should_notify(target):
                            send_notification(
                                user=target,
                                title=f'Escalamiento a Proveedor',
                                message=f'La incidencia {instance.code} ha sido escalada a Proveedor.',
                                notification_type='incident_escalated',
                                category=category,
                                is_important=True,
                                related_incident=instance,
                                metadata={'incident_id': instance.id, 'stage': 'supplier'}
                            )

                # Cambios generales de estado/prioridad
                fields_to_check = {
                    'estado': 'Estado',
                    'prioridad': 'Prioridad',
                    'assigned_to': 'Asignado'
                }
                
                for field, label in fields_to_check.items():
                    old_val = old_values.get(field)
                    new_val = getattr(instance, field, None)
                    if old_val != new_val:
                        important_changes.append(f"{label}: {old_val} -> {new_val}")

            if important_changes:
                changes_text = "\n".join(important_changes)
                # Notify Involucrados: CreatedBy, AssignedTo, Admins
                # Filtrar duplicados
                recipients = set()
                if instance.created_by: recipients.add(instance.created_by)
                if instance.assigned_to: recipients.add(instance.assigned_to)
                
                # Add Admins
                admins = User.objects.filter(role='admin')
                for admin in admins: recipients.add(admin)

                for recipient in recipients:
                    if should_notify(recipient):
                        send_notification(
                            user=recipient,
                            title=f'Actualización en {instance.code}',
                            message=f'Cambios recientes:\n{changes_text}',
                            notification_type='incident_updated',
                            category=category,
                            related_incident=instance,
                            metadata={'incident_id': instance.id, 'changes': important_changes}
                        )

    except Exception as e:
        logger.error(f'Error al generar notificación de incidencia: {str(e)}')


@receiver(pre_save, sender=Incident)
def track_incident_changes(sender, instance, **kwargs):
    """Rastrear cambios en campos importantes"""
    if instance.pk:
        try:
            old_instance = Incident.objects.get(pk=instance.pk)
            instance._old_values = {
                'estado': old_instance.estado,
                'prioridad': old_instance.prioridad,
                'assigned_to': old_instance.assigned_to,
                'escalated_to_internal_quality': getattr(old_instance, 'escalated_to_internal_quality', False),
                'escalated_to_supplier': getattr(old_instance, 'escalated_to_supplier', False),
            }
        except Incident.DoesNotExist:
            instance._old_values = {}


@receiver(post_save, sender=Document)
def handle_document_notification(sender, instance, created, **kwargs):
    """Notificaciones de documentos optimizadas por rol"""
    if kwargs.get('raw', False):
        return
    try:
        category, _ = NotificationCategory.objects.get_or_create(
            name='documents',
            defaults={'description': 'Documentos', 'icon': 'description', 'color': '#2196f3'}
        )
        
        actor = getattr(instance, 'last_modified_by', instance.created_by)
        
        def should_notify(target_user):
            if not target_user: return False
            # Admin gets all
            if target_user.role == 'admin': return True
            return target_user != actor

        if created:
            # Notificar Admin
            for admin in User.objects.filter(role='admin'):
                if should_notify(admin):
                    send_notification(
                         user=admin,
                         title='Nuevo documento',
                         message=f'Documento {instance.title} subido por {instance.created_by.full_name}',
                         notification_type='document_uploaded',
                         category=category,
                         related_document=instance
                    )

            # Notificar Revisores (Calidad/Admin) si requiere aprobación
            if instance.requires_approval:
                # Assuming 'quality' role are reviewers
                reviewers = User.objects.filter(role__in=['quality', 'admin'])
                for reviewer in reviewers:
                    if should_notify(reviewer):
                         send_notification(
                            user=reviewer,
                            title='Revisión requerida',
                            message=f'El documento {instance.title} requiere aprobación.',
                            notification_type='document_approval_required',
                            category=category,
                            is_important=True,
                            related_document=instance
                        )
        else:
             # Cambios de estado (Aprobado/Rechazado)
            if hasattr(instance, '_old_values') and instance._old_values.get('status') != instance.status:
                new_status = instance.status
                msg_map = {'approved': 'Aprobado', 'rejected': 'Rechazado'}
                status_msg = msg_map.get(new_status, 'Actualizado')
                
                # Notify Creator
                if should_notify(instance.created_by):
                    send_notification(
                        user=instance.created_by,
                        title=f'Documento {status_msg}',
                        message=f'Tu documento {instance.title} ha sido {status_msg.lower()}.',
                        notification_type=f'document_{new_status}',
                        category=category,
                        is_important=new_status=='rejected',
                        related_document=instance
                    )
                
                # Notify Admins of state change
                for admin in User.objects.filter(role='admin'):
                    if should_notify(admin):
                         send_notification(
                            user=admin,
                            title=f'Documento {status_msg}',
                            message=f'Documento {instance.title} fue {status_msg.lower()}.',
                            notification_type=f'document_{new_status}',
                            category=category,
                            related_document=instance
                        )

    except Exception as e:
        logger.error(f'Error en notificaciones de documentos: {e}')


@receiver(pre_save, sender=Document)
def track_document_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Document.objects.get(pk=instance.pk)
            instance._old_values = {
                'status': old.status,
                'title': old.title
            }
        except Document.DoesNotExist:
            instance._old_values = {}


@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Crear preferencias por defecto"""
    if created:
        NotificationPreferences.objects.get_or_create(user=instance)
        # Notify Admins only
        for admin in User.objects.filter(role='admin'):
             send_notification(
                user=admin,
                title='Nuevo Usuario',
                message=f'Usuario registrado: {instance.username}',
                notification_type='user_registered',
                is_system=True
            )

