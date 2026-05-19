from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import logging

from .models import (
    ExternalSystem, IntegrationTemplate, IntegrationInstance, 
    IntegrationLog, WebhookEndpoint, WebhookLog
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ExternalSystem)
def external_system_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda un sistema externo"""
    action = 'created' if created else 'updated'
    logger.info(f"External system {action}: {instance.name} ({instance.system_type})")


@receiver(post_save, sender=IntegrationTemplate)
def integration_template_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda una plantilla de integración"""
    action = 'created' if created else 'updated'
    logger.info(f"Integration template {action}: {instance.name} ({instance.template_type})")


@receiver(post_save, sender=IntegrationInstance)
def integration_instance_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda una instancia de integración"""
    if created:
        logger.info(f"Integration instance created: {instance.template.name} - {instance.status}")
    else:
        # Verificar si cambió el estado
        if instance.status in ['completed', 'failed', 'cancelled']:
            logger.info(f"Integration instance {instance.status}: {instance.template.name}")


@receiver(post_save, sender=IntegrationLog)
def integration_log_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda un log de integración"""
    if created:
        logger.info(f"Integration log: {instance.level.upper()} - {instance.instance.template.name} - {instance.message}")


@receiver(post_save, sender=WebhookEndpoint)
def webhook_endpoint_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda un endpoint de webhook"""
    action = 'created' if created else 'updated'
    logger.info(f"Webhook endpoint {action}: {instance.name} ({instance.http_method} {instance.url_path})")


@receiver(post_save, sender=WebhookLog)
def webhook_log_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda un log de webhook"""
    if created:
        logger.info(f"Webhook log: {instance.status.upper()} - {instance.endpoint.name} - {instance.request_method}")


@receiver(post_delete, sender=ExternalSystem)
def external_system_deleted(sender, instance, **kwargs):
    """Señal cuando se elimina un sistema externo"""
    logger.info(f"External system deleted: {instance.name} ({instance.system_type})")


@receiver(post_delete, sender=IntegrationTemplate)
def integration_template_deleted(sender, instance, **kwargs):
    """Señal cuando se elimina una plantilla de integración"""
    logger.info(f"Integration template deleted: {instance.name} ({instance.template_type})")


@receiver(post_delete, sender=WebhookEndpoint)
def webhook_endpoint_deleted(sender, instance, **kwargs):
    """Señal cuando se elimina un endpoint de webhook"""
    logger.info(f"Webhook endpoint deleted: {instance.name} ({instance.http_method} {instance.url_path})")


@receiver(pre_save, sender=IntegrationInstance)
def integration_instance_pre_save(sender, instance, **kwargs):
    """Señal antes de guardar una instancia de integración"""
    # Actualizar timestamp de actualización
    instance.updated_at = timezone.now()
    
    # Log de cambio de estado
    if instance.pk:
        try:
            old_instance = IntegrationInstance.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                logger.info(f"Integration instance status changed: {old_instance.status} -> {instance.status} ({instance.template.name})")
        except IntegrationInstance.DoesNotExist:
            pass
