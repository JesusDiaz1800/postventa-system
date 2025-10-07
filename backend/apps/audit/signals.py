from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import AuditLog
from .services import AuditService


@receiver(post_save, sender=User)
def audit_user_created(sender, instance, created, **kwargs):
    """Auditar creación de usuarios"""
    if created:
        AuditService.log_action(
            action='create',
            description=f'Usuario creado: {instance.username}',
            user=instance,
            category='user_management',
            severity='medium'
        )


@receiver(post_save, sender=User)
def audit_user_updated(sender, instance, created, **kwargs):
    """Auditar actualización de usuarios"""
    if not created:
        AuditService.log_action(
            action='update',
            description=f'Usuario actualizado: {instance.username}',
            user=instance,
            category='user_management',
            severity='medium'
        )


@receiver(post_delete, sender=User)
def audit_user_deleted(sender, instance, **kwargs):
    """Auditar eliminación de usuarios"""
    AuditService.log_action(
        action='delete',
        description=f'Usuario eliminado: {instance.username}',
        user=instance,
        category='user_management',
        severity='high'
    )


# Señales para otros modelos (se implementarán cuando se necesiten)
@receiver(post_save)
def audit_model_changes(sender, instance, created, **kwargs):
    """Auditar cambios en modelos"""
    # Excluir modelos de auditoría para evitar recursión
    if sender._meta.app_label == 'audit':
        return
    
    # Excluir modelos específicos que no necesitan auditoría
    excluded_models = ['sessions', 'contenttypes', 'admin']
    if sender._meta.app_label in excluded_models:
        return
    
    # Determinar acción
    action = 'create' if created else 'update'
    
    # Obtener información del modelo
    model_name = f"{sender._meta.app_label}.{sender._meta.model_name}"
    
    # Crear descripción
    if hasattr(instance, 'get_audit_description'):
        description = instance.get_audit_description(action)
    else:
        description = f"{action.title()} {model_name}: {instance}"
    
    # Obtener usuario del contexto (si está disponible)
    user = None
    if hasattr(instance, 'created_by'):
        user = instance.created_by
    elif hasattr(instance, 'updated_by'):
        user = instance.updated_by
    
    # Registrar en auditoría
    AuditService.log_action(
        action=action,
        description=description,
        user=user,
        category='data_modification',
        severity='medium',
        module=sender._meta.app_label,
        function=f"{sender._meta.model_name}.{action}"
    )


@receiver(post_delete)
def audit_model_deletion(sender, instance, **kwargs):
    """Auditar eliminación de modelos"""
    # Excluir modelos de auditoría para evitar recursión
    if sender._meta.app_label == 'audit':
        return
    
    # Excluir modelos específicos que no necesitan auditoría
    excluded_models = ['sessions', 'contenttypes', 'admin']
    if sender._meta.app_label in excluded_models:
        return
    
    # Obtener información del modelo
    model_name = f"{sender._meta.app_label}.{sender._meta.model_name}"
    
    # Crear descripción
    if hasattr(instance, 'get_audit_description'):
        description = instance.get_audit_description('delete')
    else:
        description = f"Delete {model_name}: {instance}"
    
    # Obtener usuario del contexto (si está disponible)
    user = None
    if hasattr(instance, 'created_by'):
        user = instance.created_by
    elif hasattr(instance, 'updated_by'):
        user = instance.updated_by
    
    # Registrar en auditoría
    AuditService.log_action(
        action='delete',
        description=description,
        user=user,
        category='data_modification',
        severity='high',
        module=sender._meta.app_label,
        function=f"{sender._meta.model_name}.delete"
    )


# Señales para eventos específicos del sistema
def audit_login(user, request):
    """Auditar inicio de sesión"""
    AuditService.log_action(
        action='login',
        description=f'Usuario {user.username} inició sesión',
        user=user,
        category='authentication',
        severity='medium',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_id=request.META.get('HTTP_X_REQUEST_ID', '')
    )


def audit_logout(user, request):
    """Auditar cierre de sesión"""
    AuditService.log_action(
        action='logout',
        description=f'Usuario {user.username} cerró sesión',
        user=user,
        category='authentication',
        severity='medium',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_id=request.META.get('HTTP_X_REQUEST_ID', '')
    )


def audit_unauthorized_access(user, request, resource):
    """Auditar acceso no autorizado"""
    AuditService.log_action(
        action='unauthorized',
        description=f'Acceso no autorizado a {resource}',
        user=user,
        category='authorization',
        severity='high',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_id=request.META.get('HTTP_X_REQUEST_ID', '')
    )


def audit_file_upload(user, filename, file_size, request):
    """Auditar subida de archivos"""
    AuditService.log_action(
        action='upload',
        description=f'Archivo subido: {filename} ({file_size} bytes)',
        user=user,
        category='data_access',
        severity='medium',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_id=request.META.get('HTTP_X_REQUEST_ID', ''),
        metadata={'filename': filename, 'file_size': file_size}
    )


def audit_file_download(user, filename, request):
    """Auditar descarga de archivos"""
    AuditService.log_action(
        action='download',
        description=f'Archivo descargado: {filename}',
        user=user,
        category='data_access',
        severity='medium',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_id=request.META.get('HTTP_X_REQUEST_ID', ''),
        metadata={'filename': filename}
    )


def audit_data_export(user, export_type, record_count, request):
    """Auditar exportación de datos"""
    AuditService.log_action(
        action='export',
        description=f'Datos exportados: {export_type} ({record_count} registros)',
        user=user,
        category='data_access',
        severity='medium',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_id=request.META.get('HTTP_X_REQUEST_ID', ''),
        metadata={'export_type': export_type, 'record_count': record_count}
    )


def audit_system_error(error_message, module, function, request=None):
    """Auditar errores del sistema"""
    AuditService.log_action(
        action='error',
        description=f'Error del sistema: {error_message}',
        user=None,
        category='error',
        severity='high',
        module=module,
        function=function,
        ip_address=request.META.get('REMOTE_ADDR') if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
        request_id=request.META.get('HTTP_X_REQUEST_ID', '') if request else '',
        metadata={'error_message': error_message}
    )


def audit_security_event(event_type, description, user=None, request=None, severity='high'):
    """Auditar eventos de seguridad"""
    AuditService.log_action(
        action='security_event',
        description=f'Evento de seguridad: {description}',
        user=user,
        category='security',
        severity=severity,
        ip_address=request.META.get('REMOTE_ADDR') if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
        request_id=request.META.get('HTTP_X_REQUEST_ID', '') if request else '',
        metadata={'event_type': event_type}
    )
