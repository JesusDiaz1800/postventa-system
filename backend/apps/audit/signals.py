from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core import serializers
from django.apps import apps
import json
import logging

from .models import AuditLog, DeletedItem
from .services import AuditService

logger = logging.getLogger(__name__)

# --- Authentication Signals ---

@receiver(user_logged_in)
def audit_login(sender, user, request, **kwargs):
    """Auditar inicio de sesión"""
    AuditService.log_action(
        user=user,
        action='user_login',
        description=f'Usuario {user.username} inició sesión',
        ip_address=request.META.get('REMOTE_ADDR') if request else None,
        details={'user_agent': request.META.get('HTTP_USER_AGENT', '') if request else ''}
    )

@receiver(user_logged_out)
def audit_logout(sender, user, request, **kwargs):
    """Auditar cierre de sesión"""
    if user:
        AuditService.log_action(
            user=user,
            action='user_logout',
            description=f'Usuario {user.username} cerró sesión',
            ip_address=request.META.get('REMOTE_ADDR') if request else None
        )

# --- Model Signals (Strict Filtering) ---

def get_current_user(instance):
    """Intentar obtener el usuario responsable del cambio"""
    if hasattr(instance, 'updated_by'):
        return instance.updated_by
    if hasattr(instance, 'created_by'):
        return instance.created_by
    if hasattr(instance, 'user'):
        return instance.user
    return None

@receiver(post_save)
def audit_strict_changes(sender, instance, created, **kwargs):
    """
    Auditoría estricta para: Crear, Escalar, Cerrar.
    Filtra solo modelos relevantes (Incident, Report, User).
    """
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    
    # Solo nos interesan ciertos modelos
    # Whitelist de modelos permitidos para LOG (reducir ruido)
    ALLOWED_MODELS = ['incident', 'report', 'user', 'clientqualityreport']
    
    if model_name not in ALLOWED_MODELS:
        return
        
    # Doble chequeo para permissions y otros internos
    if model_name == 'permission' or model_name == 'contenttype' or model_name == 'session':
        return

    user = get_current_user(instance)
    
    # 1. CREAR (Create)
    if created:
        action_type = 'create'
        if model_name == 'incident':
            action_code = 'incident_created'
            desc = f"Creó nueva incidencia: {instance}"
        elif model_name == 'report':
            action_code = 'report_attached' # "Adjuntar/Crear reporte"
            desc = f"Adjuntó/Creó reporte: {instance}"
        elif model_name == 'user':
            action_code = 'user_created' # No standard but useful
            desc = f"Creó usuario: {instance.username}"
        else:
            # Generic create for other monitored models
            action_code = 'create' 
            desc = f"Creó {model_name}: {instance}"

        AuditService.log_action(
            user=user,
            action=action_code,
            description=desc,
            details={'model': model_name, 'pk': instance.pk}
        )

    # 2. ACTUALIZACIONES ESPECÍFICAS (Escalar, Cerrar)
    else:
        # Solo para Incidencias chequeamos cambios de estado/prioridad
        if model_name == 'incident':
            # Necesitamos comparar con la versión anterior. 
            # Desafortunadamente post_save no nos da la "previa".
            # Usualmente se maneja en pre_save o chequeando campos dirty si usamos un lib, 
            # pero asumiremos lógica basada en el estado actual.
            
            # Detectar CIERRE
            if hasattr(instance, 'estado') and instance.estado == 'cerrado':
                # Idealmente verificaríamos si ANTES no estaba cerrado, pero por ahora 
                # si se guarda como cerrado, lo logueamos (posible duplicado si se edita cerrado, 
                # pero aceptable para "Cerrar incidencias nada más")
                AuditService.log_action(
                    user=user,
                    action='incident_closed', # "close"
                    description=f"Cerró incidencia: {instance}",
                    details={'model': model_name, 'pk': instance.pk}
                )
            
            # Detectar ESCALAMIENTO (Ej: prioridad alta/critica)
            # Esto es una aproximación.
            if hasattr(instance, 'prioridad') and instance.prioridad in ['high', 'critical']:
                # Podría ser spam si se edita mucho en critical.
                # Lo ideal es loguear "escalar" solo cuando cambia.
                # Como simplificación, asumimos que la UI envía una acción explícita para escalar
                # O si estamos aquí, es difícil saber si CAMBIÓ sin pre_save.
                pass 
                # Dejamos que la vista maneje "escalar" explícitamente si es un botón,
                # o confiamos en que 'update' genérico NO se loguea, según requisitos.


@receiver(pre_save)
def capture_pre_change_state(sender, instance, **kwargs):
    """
    Capturar estado previo para detectar cambios específicos como Escalación.
    """
    if sender._meta.model_name != 'incident':
        return

    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_priority = old_instance.prioridad
            instance._old_status = old_instance.estado
        except sender.DoesNotExist:
            pass

@receiver(post_save)
def audit_escalation_check(sender, instance, created, **kwargs):
    """Detectar escalamiento basado en cambio de prioridad"""
    if created or sender._meta.model_name != 'incident':
        return
        
    # Verificar cambio de prioridad a mayor
    if hasattr(instance, '_old_priority') and instance.prioridad != instance._old_priority:
        # Si la nueva es alta/critica y la vieja no
        high_priorities = ['high', 'critical']
        if instance.prioridad in high_priorities and instance._old_priority not in high_priorities:
             AuditService.log_action(
                user=get_current_user(instance),
                action='escalation_triggered', # "Escalar"
                description=f"Escaló incidencia a {instance.prioridad}",
                details={'from': instance._old_priority, 'to': instance.prioridad}
            )

# --- Deletion & Recycle Bin ---

@receiver(post_delete)
def audit_delete_and_recycle(sender, instance, **kwargs):
    """
    Auditar eliminación y guardar en Papelera (Recycle Bin).
    """
    app_label = sender._meta.app_label
    model_name = sender._meta.model_name
    
    # Evitar recursión y modelos internos
    # Whitelist de modelos permitidos para PAPELERA (evitar duplicados hijos)
    # Solo guardamos cosas que se pueden restaurar independientemente
    ALLOWED_RECYCLE_MODELS = ['incident', 'report', 'user', 'clientqualityreport']
    
    if model_name not in ALLOWED_RECYCLE_MODELS:
        return

    user = get_current_user(instance)
    
    # 1. Log de Auditoría (Eliminar)
    AuditService.log_action(
        user=user,
        action='delete', # "Eliminar"
        description=f"Eliminó {model_name}: {str(instance)}",
        details={'model': model_name, 'pk': instance.pk}
    )
    
    # 2. Guardar en Papelera (DeletedItem)
    try:
        # Serialización robusta
        serialized_data = serializers.serialize('json', [instance])
        # serialize devuelve una lista de strings JSON por objeto, pero aquí es una string única con una lista dentro.
        # json.loads(serialized_data) será una lista de dicts.
        
        json_data = json.loads(serialized_data)
        
        # Guardar
        DeletedItem.objects.create(
            original_id=str(instance.pk),
            model_name=model_name,
            app_label=app_label,
            object_repr=str(instance), # Guardar representación legible
            serialized_data=json_data, # Guardamos la estructura completa
            deleted_by=user
        )
    except Exception as e:
        logger.error(f"Error guardando en papelera: {e}")
