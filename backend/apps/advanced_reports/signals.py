from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import logging

from .models import (
    ReportTemplate, ReportInstance, ReportSchedule, 
    ReportDashboard, ReportWidget, ReportExport
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ReportTemplate)
def report_template_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda una plantilla de reporte"""
    action = 'created' if created else 'updated'
    logger.info(f"Report template {action}: {instance.name} ({instance.report_type})")


@receiver(post_save, sender=ReportInstance)
def report_instance_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda una instancia de reporte"""
    if created:
        logger.info(f"Report instance created: {instance.template.name} - {instance.status}")
    else:
        # Verificar si cambió el estado
        if instance.status in ['completed', 'failed', 'cancelled']:
            logger.info(f"Report instance {instance.status}: {instance.template.name}")


@receiver(post_save, sender=ReportSchedule)
def report_schedule_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda una programación de reporte"""
    action = 'created' if created else 'updated'
    logger.info(f"Report schedule {action}: {instance.name} ({instance.template.name})")


@receiver(post_save, sender=ReportDashboard)
def report_dashboard_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda un dashboard de reportes"""
    action = 'created' if created else 'updated'
    logger.info(f"Report dashboard {action}: {instance.name}")


@receiver(post_save, sender=ReportWidget)
def report_widget_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda un widget de reporte"""
    action = 'created' if created else 'updated'
    logger.info(f"Report widget {action}: {instance.name} ({instance.dashboard.name})")


@receiver(post_save, sender=ReportExport)
def report_export_saved(sender, instance, created, **kwargs):
    """Señal cuando se guarda una exportación de reporte"""
    if created:
        logger.info(f"Report export created: {instance.instance.template.name} - {instance.export_format}")
    else:
        # Verificar si cambió el estado
        if instance.status in ['completed', 'failed']:
            logger.info(f"Report export {instance.status}: {instance.instance.template.name}")


@receiver(post_delete, sender=ReportTemplate)
def report_template_deleted(sender, instance, **kwargs):
    """Señal cuando se elimina una plantilla de reporte"""
    logger.info(f"Report template deleted: {instance.name} ({instance.report_type})")


@receiver(post_delete, sender=ReportSchedule)
def report_schedule_deleted(sender, instance, **kwargs):
    """Señal cuando se elimina una programación de reporte"""
    logger.info(f"Report schedule deleted: {instance.name} ({instance.template.name})")


@receiver(post_delete, sender=ReportDashboard)
def report_dashboard_deleted(sender, instance, **kwargs):
    """Señal cuando se elimina un dashboard de reportes"""
    logger.info(f"Report dashboard deleted: {instance.name}")


@receiver(post_delete, sender=ReportWidget)
def report_widget_deleted(sender, instance, **kwargs):
    """Señal cuando se elimina un widget de reporte"""
    logger.info(f"Report widget deleted: {instance.name} ({instance.dashboard.name})")


@receiver(pre_save, sender=ReportInstance)
def report_instance_pre_save(sender, instance, **kwargs):
    """Señal antes de guardar una instancia de reporte"""
    # Actualizar timestamp de actualización
    instance.updated_at = timezone.now()
    
    # Log de cambio de estado
    if instance.pk:
        try:
            old_instance = ReportInstance.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                logger.info(f"Report instance status changed: {old_instance.status} -> {instance.status} ({instance.template.name})")
        except ReportInstance.DoesNotExist:
            pass


@receiver(pre_save, sender=ReportExport)
def report_export_pre_save(sender, instance, **kwargs):
    """Señal antes de guardar una exportación de reporte"""
    # Log de cambio de estado
    if instance.pk:
        try:
            old_export = ReportExport.objects.get(pk=instance.pk)
            if old_export.status != instance.status:
                logger.info(f"Report export status changed: {old_export.status} -> {instance.status} ({instance.instance.template.name})")
        except ReportExport.DoesNotExist:
            pass
