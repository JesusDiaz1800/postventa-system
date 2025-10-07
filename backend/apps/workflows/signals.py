from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import WorkflowInstance, WorkflowApproval, WorkflowStep
from .services import WorkflowService
from apps.notifications.services import NotificationService


@receiver(post_save, sender=WorkflowInstance)
def notify_workflow_created(sender, instance, created, **kwargs):
    """Notificar cuando se crea una instancia de workflow"""
    if created:
        NotificationService.create_notification(
            user=instance.started_by,
            title=f"Workflow Iniciado: {instance.template.name}",
            message=f"Se ha iniciado el workflow {instance.template.name}",
            notification_type='workflow_step_completed',
            related_incident=instance.related_incident,
            related_document=instance.related_document
        )


@receiver(post_save, sender=WorkflowApproval)
def notify_approval_assigned(sender, instance, created, **kwargs):
    """Notificar cuando se asigna una aprobación"""
    if created:
        NotificationService.create_notification(
            user=instance.approver,
            title=f"Aprobación Requerida: {instance.instance.template.name}",
            message=f"Se requiere tu aprobación para el paso '{instance.step.name}' del workflow {instance.instance.template.name}",
            notification_type='workflow_approval_required',
            is_important=True,
            related_incident=instance.instance.related_incident,
            related_document=instance.instance.related_document
        )


@receiver(pre_save, sender=WorkflowApproval)
def check_approval_timeout(sender, instance, **kwargs):
    """Verificar si la aprobación está vencida"""
    if instance.pk and instance.status == 'pending':
        if instance.due_date and timezone.now() > instance.due_date:
            # Marcar como vencida y notificar
            NotificationService.create_notification(
                user=instance.approver,
                title=f"Aprobación Vencida: {instance.instance.template.name}",
                message=f"La aprobación para el paso '{instance.step.name}' del workflow {instance.instance.template.name} ha vencido",
                notification_type='workflow_approval_required',
                is_important=True,
                related_incident=instance.instance.related_incident,
                related_document=instance.instance.related_document
            )
