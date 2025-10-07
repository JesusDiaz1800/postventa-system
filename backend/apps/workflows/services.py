from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import timedelta
from .models import (
    WorkflowTemplate, 
    WorkflowStep, 
    WorkflowInstance, 
    WorkflowApproval, 
    WorkflowHistory,
    WorkflowRule
)
from apps.notifications.services import NotificationService


class WorkflowService:
    """Servicio para gestión de workflows"""
    
    @staticmethod
    def create_workflow_instance(template, user, related_incident=None, related_document=None, context_data=None):
        """Crear nueva instancia de workflow"""
        instance = WorkflowInstance.objects.create(
            template=template,
            started_by=user,
            related_incident=related_incident,
            related_document=related_document,
            context_data=context_data or {}
        )
        
        # Crear historial
        WorkflowHistory.objects.create(
            instance=instance,
            action='started',
            description=f'Workflow iniciado por {user.username}',
            user=user
        )
        
        return instance
    
    @staticmethod
    def start_workflow(instance, user):
        """Iniciar workflow"""
        if instance.status != 'pending':
            raise ValueError("Workflow ya iniciado")
        
        # Obtener primer paso
        first_step = instance.template.steps.filter(order=1).first()
        if not first_step:
            raise ValueError("No hay pasos configurados en el workflow")
        
        # Actualizar estado
        instance.status = 'in_progress'
        instance.current_step = first_step
        instance.started_at = timezone.now()
        instance.save()
        
        # Crear aprobaciones para el primer paso
        WorkflowService.create_step_approvals(instance, first_step)
        
        # Crear historial
        WorkflowHistory.objects.create(
            instance=instance,
            step=first_step,
            action='step_started',
            description=f'Paso "{first_step.name}" iniciado',
            user=user
        )
        
        # Enviar notificaciones
        WorkflowService.send_step_notifications(instance, first_step, 'started')
        
        return instance
    
    @staticmethod
    def create_step_approvals(instance, step):
        """Crear aprobaciones para un paso"""
        approvals = []
        
        # Asignación por usuario específico
        if step.assigned_to_user:
            approval = WorkflowApproval.objects.create(
                instance=instance,
                step=step,
                approver=step.assigned_to_user,
                due_date=timezone.now() + step.time_limit if step.time_limit else None
            )
            approvals.append(approval)
        
        # Asignación por rol
        elif step.assigned_to_role:
            users = WorkflowService.get_users_by_role(step.assigned_to_role)
            for user in users:
                approval = WorkflowApproval.objects.create(
                    instance=instance,
                    step=step,
                    approver=user,
                    due_date=timezone.now() + step.time_limit if step.time_limit else None
                )
                approvals.append(approval)
        
        # Asignación por grupo
        elif step.assigned_to_group:
            users = WorkflowService.get_users_by_group(step.assigned_to_group)
            for user in users:
                approval = WorkflowApproval.objects.create(
                    instance=instance,
                    step=step,
                    approver=user,
                    due_date=timezone.now() + step.time_limit if step.time_limit else None
                )
                approvals.append(approval)
        
        return approvals
    
    @staticmethod
    def get_users_by_role(role):
        """Obtener usuarios por rol"""
        # Implementar lógica de roles
        # Por ahora retornar usuarios con el rol en el campo role
        return User.objects.filter(profile__role=role)
    
    @staticmethod
    def get_users_by_group(group_name):
        """Obtener usuarios por grupo"""
        # Implementar lógica de grupos
        # Por ahora retornar usuarios del grupo
        return User.objects.filter(groups__name=group_name)
    
    @staticmethod
    def advance_workflow(instance, user, action_data=None):
        """Avanzar workflow al siguiente paso"""
        if instance.status != 'in_progress':
            raise ValueError("Workflow no está en progreso")
        
        current_step = instance.current_step
        if not current_step:
            raise ValueError("No hay paso actual")
        
        # Verificar si el usuario puede aprobar
        if not instance.can_be_approved_by(user):
            raise ValueError("Usuario no autorizado para aprobar")
        
        # Verificar si todas las aprobaciones están completadas
        pending_approvals = instance.approvals.filter(
            step=current_step,
            status='pending'
        )
        
        if pending_approvals.exists():
            raise ValueError("Hay aprobaciones pendientes")
        
        # Marcar paso como completado
        WorkflowHistory.objects.create(
            instance=instance,
            step=current_step,
            action='step_completed',
            description=f'Paso "{current_step.name}" completado por {user.username}',
            user=user
        )
        
        # Enviar notificaciones
        WorkflowService.send_step_notifications(instance, current_step, 'completed')
        
        # Obtener siguiente paso
        next_step = instance.template.steps.filter(
            order=current_step.order + 1
        ).first()
        
        if next_step:
            # Avanzar al siguiente paso
            instance.current_step = next_step
            instance.save()
            
            # Crear aprobaciones para el siguiente paso
            WorkflowService.create_step_approvals(instance, next_step)
            
            # Crear historial
            WorkflowHistory.objects.create(
                instance=instance,
                step=next_step,
                action='step_started',
                description=f'Paso "{next_step.name}" iniciado',
                user=user
            )
            
            # Enviar notificaciones
            WorkflowService.send_step_notifications(instance, next_step, 'started')
        else:
            # Workflow completado
            WorkflowService.complete_workflow(instance, user)
        
        return instance
    
    @staticmethod
    def complete_workflow(instance, user):
        """Completar workflow"""
        instance.status = 'completed'
        instance.completed_at = timezone.now()
        instance.completed_by = user
        instance.current_step = None
        instance.save()
        
        # Crear historial
        WorkflowHistory.objects.create(
            instance=instance,
            action='workflow_completed',
            description=f'Workflow completado por {user.username}',
            user=user
        )
        
        # Enviar notificaciones
        NotificationService.create_notification(
            user=instance.started_by,
            title=f"Workflow Completado: {instance.template.name}",
            message=f"El workflow {instance.template.name} ha sido completado",
            notification_type='workflow_step_completed',
            related_incident=instance.related_incident,
            related_document=instance.related_document
        )
        
        return instance
    
    @staticmethod
    def cancel_workflow(instance, user, reason=''):
        """Cancelar workflow"""
        instance.status = 'cancelled'
        instance.completed_at = timezone.now()
        instance.completed_by = user
        instance.save()
        
        # Crear historial
        WorkflowHistory.objects.create(
            instance=instance,
            action='workflow_cancelled',
            description=f'Workflow cancelado por {user.username}. Razón: {reason}',
            user=user
        )
        
        # Enviar notificaciones
        NotificationService.create_notification(
            user=instance.started_by,
            title=f"Workflow Cancelado: {instance.template.name}",
            message=f"El workflow {instance.template.name} ha sido cancelado. Razón: {reason}",
            notification_type='workflow_step_completed',
            related_incident=instance.related_incident,
            related_document=instance.related_document
        )
        
        return instance
    
    @staticmethod
    def approve_workflow(approval, user, comments='', metadata=None):
        """Aprobar workflow"""
        if approval.status != 'pending':
            raise ValueError("Aprobación ya procesada")
        
        approval.status = 'approved'
        approval.completed_at = timezone.now()
        approval.comments = comments
        approval.metadata = metadata or {}
        approval.save()
        
        # Crear historial
        WorkflowHistory.objects.create(
            instance=approval.instance,
            step=approval.step,
            action='step_completed',
            description=f'Aprobación completada por {user.username}',
            user=user,
            metadata={'comments': comments}
        )
        
        # Verificar si se puede avanzar el workflow
        WorkflowService.check_workflow_advancement(approval.instance)
        
        return approval
    
    @staticmethod
    def reject_workflow(approval, user, comments='', justification='', metadata=None):
        """Rechazar workflow"""
        if approval.status != 'pending':
            raise ValueError("Aprobación ya procesada")
        
        approval.status = 'rejected'
        approval.completed_at = timezone.now()
        approval.comments = comments
        approval.justification = justification
        approval.metadata = metadata or {}
        approval.save()
        
        # Rechazar workflow completo
        instance = approval.instance
        instance.status = 'rejected'
        instance.completed_at = timezone.now()
        instance.completed_by = user
        instance.save()
        
        # Crear historial
        WorkflowHistory.objects.create(
            instance=instance,
            step=approval.step,
            action='step_rejected',
            description=f'Workflow rechazado por {user.username}. Razón: {justification}',
            user=user,
            metadata={
                'comments': comments,
                'justification': justification
            }
        )
        
        # Enviar notificaciones
        NotificationService.create_notification(
            user=instance.started_by,
            title=f"Workflow Rechazado: {instance.template.name}",
            message=f"El workflow {instance.template.name} ha sido rechazado. Razón: {justification}",
            notification_type='workflow_step_completed',
            is_important=True,
            related_incident=instance.related_incident,
            related_document=instance.related_document
        )
        
        return approval
    
    @staticmethod
    def delegate_approval(approval, user, delegated_to_id, comments=''):
        """Delegar aprobación"""
        if approval.status != 'pending':
            raise ValueError("Aprobación ya procesada")
        
        try:
            delegated_to = User.objects.get(id=delegated_to_id)
        except User.DoesNotExist:
            raise ValueError("Usuario delegado no encontrado")
        
        approval.status = 'delegated'
        approval.completed_at = timezone.now()
        approval.comments = comments
        approval.delegated_to = delegated_to
        approval.save()
        
        # Crear nueva aprobación para el usuario delegado
        new_approval = WorkflowApproval.objects.create(
            instance=approval.instance,
            step=approval.step,
            approver=delegated_to,
            due_date=approval.due_date
        )
        
        # Crear historial
        WorkflowHistory.objects.create(
            instance=approval.instance,
            step=approval.step,
            action='step_delegated',
            description=f'Aprobación delegada de {user.username} a {delegated_to.username}',
            user=user,
            metadata={'comments': comments}
        )
        
        # Enviar notificaciones
        NotificationService.create_notification(
            user=delegated_to,
            title=f"Aprobación Delegada: {approval.instance.template.name}",
            message=f"Se te ha delegado una aprobación para el workflow {approval.instance.template.name}",
            notification_type='workflow_approval_required',
            related_incident=approval.instance.related_incident,
            related_document=approval.instance.related_document,
            related_user=user
        )
        
        return approval
    
    @staticmethod
    def check_workflow_advancement(instance):
        """Verificar si el workflow puede avanzar"""
        if instance.status != 'in_progress':
            return
        
        current_step = instance.current_step
        if not current_step:
            return
        
        # Verificar si todas las aprobaciones están completadas
        pending_approvals = instance.approvals.filter(
            step=current_step,
            status='pending'
        )
        
        if not pending_approvals.exists():
            # Todas las aprobaciones están completadas, avanzar automáticamente
            WorkflowService.advance_workflow(instance, instance.started_by)
    
    @staticmethod
    def send_step_notifications(instance, step, action):
        """Enviar notificaciones de paso"""
        if action == 'started' and step.notify_on_start:
            # Notificar a los usuarios asignados
            for approval in instance.approvals.filter(step=step, status='pending'):
                NotificationService.create_notification(
                    user=approval.approver,
                    title=f"Aprobación Requerida: {instance.template.name}",
                    message=f"Se requiere tu aprobación para el paso '{step.name}' del workflow {instance.template.name}",
                    notification_type='workflow_approval_required',
                    is_important=True,
                    related_incident=instance.related_incident,
                    related_document=instance.related_document
                )
        
        elif action == 'completed' and step.notify_on_complete:
            # Notificar al iniciador del workflow
            NotificationService.create_notification(
                user=instance.started_by,
                title=f"Paso Completado: {instance.template.name}",
                message=f"El paso '{step.name}' del workflow {instance.template.name} ha sido completado",
                notification_type='workflow_step_completed',
                related_incident=instance.related_incident,
                related_document=instance.related_document
            )
    
    @staticmethod
    def get_workflow_progress(instance):
        """Obtener progreso del workflow"""
        if not instance.current_step:
            return {'progress': 100, 'current_step': None, 'total_steps': 0}
        
        total_steps = instance.template.steps.count()
        current_step_order = instance.current_step.order
        
        progress = (current_step_order / total_steps) * 100
        
        return {
            'progress': progress,
            'current_step': {
                'id': instance.current_step.id,
                'name': instance.current_step.name,
                'order': instance.current_step.order
            },
            'total_steps': total_steps,
            'completed_steps': current_step_order - 1,
            'remaining_steps': total_steps - current_step_order + 1
        }
    
    @staticmethod
    def get_workflow_stats(user):
        """Obtener estadísticas de workflow"""
        # Workflows del usuario
        user_workflows = WorkflowInstance.objects.filter(
            Q(started_by=user) | Q(approvals__approver=user)
        ).distinct()
        
        # Estadísticas generales
        total_workflows = user_workflows.count()
        active_workflows = user_workflows.filter(status='in_progress').count()
        completed_workflows = user_workflows.filter(status='completed').count()
        rejected_workflows = user_workflows.filter(status='rejected').count()
        
        # Aprobaciones pendientes
        pending_approvals = WorkflowApproval.objects.filter(
            approver=user,
            status='pending'
        ).count()
        
        # Aprobaciones vencidas
        overdue_approvals = WorkflowApproval.objects.filter(
            approver=user,
            status='pending',
            due_date__lt=timezone.now()
        ).count()
        
        # Workflows por tipo
        workflows_by_type = {}
        for workflow_type, _ in WorkflowTemplate.WORKFLOW_TYPES:
            count = user_workflows.filter(template__workflow_type=workflow_type).count()
            workflows_by_type[workflow_type] = count
        
        # Workflows por estado
        workflows_by_status = {}
        for status, _ in WorkflowInstance.STATUS_CHOICES:
            count = user_workflows.filter(status=status).count()
            workflows_by_status[status] = count
        
        # Tiempo promedio de completación
        completed_workflows_with_time = user_workflows.filter(
            status='completed',
            completed_at__isnull=False
        )
        
        if completed_workflows_with_time.exists():
            avg_completion_time = completed_workflows_with_time.aggregate(
                avg_time=Avg('completed_at') - Avg('started_at')
            )['avg_time']
        else:
            avg_completion_time = None
        
        # Workflows este mes
        this_month = timezone.now().replace(day=1)
        workflows_this_month = user_workflows.filter(
            started_at__gte=this_month
        ).count()
        
        # Workflows mes pasado
        last_month = this_month - timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        workflows_last_month = user_workflows.filter(
            started_at__gte=last_month_start,
            started_at__lt=this_month
        ).count()
        
        return {
            'total_workflows': total_workflows,
            'active_workflows': active_workflows,
            'completed_workflows': completed_workflows,
            'rejected_workflows': rejected_workflows,
            'pending_approvals': pending_approvals,
            'overdue_approvals': overdue_approvals,
            'workflows_by_type': workflows_by_type,
            'workflows_by_status': workflows_by_status,
            'average_completion_time': avg_completion_time,
            'workflows_this_month': workflows_this_month,
            'workflows_last_month': workflows_last_month
        }
    
    @staticmethod
    def search_workflows(user, search_params):
        """Buscar workflows"""
        queryset = WorkflowInstance.objects.filter(
            Q(started_by=user) | Q(approvals__approver=user)
        ).distinct()
        
        # Filtros
        if search_params.get('query'):
            query = search_params['query']
            queryset = queryset.filter(
                Q(template__name__icontains=query) |
                Q(related_incident__title__icontains=query) |
                Q(related_document__title__icontains=query)
            )
        
        if search_params.get('status'):
            queryset = queryset.filter(status=search_params['status'])
        
        if search_params.get('workflow_type'):
            queryset = queryset.filter(template__workflow_type=search_params['workflow_type'])
        
        if search_params.get('assigned_to'):
            queryset = queryset.filter(approvals__approver_id=search_params['assigned_to'])
        
        if search_params.get('date_from'):
            queryset = queryset.filter(started_at__gte=search_params['date_from'])
        
        if search_params.get('date_to'):
            queryset = queryset.filter(started_at__lte=search_params['date_to'])
        
        # Ordenamiento
        ordering = search_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    @staticmethod
    def duplicate_template(template, user):
        """Duplicar plantilla de workflow"""
        # Crear nueva plantilla
        new_template = WorkflowTemplate.objects.create(
            name=f"{template.name} (Copia)",
            description=template.description,
            workflow_type=template.workflow_type,
            is_active=True,
            is_default=False,
            auto_start=template.auto_start,
            allow_parallel=template.allow_parallel,
            max_duration=template.max_duration,
            created_by=user
        )
        
        # Duplicar pasos
        for step in template.steps.all():
            WorkflowStep.objects.create(
                template=new_template,
                name=step.name,
                description=step.description,
                step_type=step.step_type,
                order=step.order,
                is_required=step.is_required,
                is_parallel=step.is_parallel,
                time_limit=step.time_limit,
                auto_advance=step.auto_advance,
                assigned_to_role=step.assigned_to_role,
                assigned_to_user=step.assigned_to_user,
                assigned_to_group=step.assigned_to_group,
                condition_expression=step.condition_expression,
                action_script=step.action_script,
                notify_on_start=step.notify_on_start,
                notify_on_complete=step.notify_on_complete,
                notify_on_timeout=step.notify_on_timeout
            )
        
        return new_template
