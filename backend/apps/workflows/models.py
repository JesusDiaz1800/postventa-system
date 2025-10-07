from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class WorkflowTemplate(models.Model):
    """Plantilla de workflow para diferentes tipos de procesos"""
    
    WORKFLOW_TYPES = [
        ('incident_approval', 'Aprobación de Incidencia'),
        ('document_approval', 'Aprobación de Documento'),
        ('quality_review', 'Revisión de Calidad'),
        ('supplier_response', 'Respuesta de Proveedor'),
        ('escalation', 'Escalación'),
        ('custom', 'Personalizado'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción', blank=True)
    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPES, verbose_name='Tipo de Workflow')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_default = models.BooleanField(default=False, verbose_name='Por Defecto')
    
    # Configuración del workflow
    auto_start = models.BooleanField(default=False, verbose_name='Inicio Automático')
    allow_parallel = models.BooleanField(default=False, verbose_name='Permitir Pasos Paralelos')
    max_duration = models.DurationField(null=True, blank=True, verbose_name='Duración Máxima')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workflows')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Plantilla de Workflow'
        verbose_name_plural = 'Plantillas de Workflow'
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validar que solo haya una plantilla por defecto por tipo"""
        if self.is_default:
            existing_default = WorkflowTemplate.objects.filter(
                workflow_type=self.workflow_type,
                is_default=True,
                is_active=True
            ).exclude(id=self.id)
            
            if existing_default.exists():
                raise ValidationError(
                    f'Ya existe una plantilla por defecto para el tipo {self.workflow_type}'
                )


class WorkflowStep(models.Model):
    """Pasos individuales de un workflow"""
    
    STEP_TYPES = [
        ('approval', 'Aprobación'),
        ('review', 'Revisión'),
        ('notification', 'Notificación'),
        ('assignment', 'Asignación'),
        ('escalation', 'Escalación'),
        ('condition', 'Condición'),
        ('action', 'Acción'),
    ]
    
    template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción', blank=True)
    step_type = models.CharField(max_length=50, choices=STEP_TYPES, verbose_name='Tipo de Paso')
    order = models.PositiveIntegerField(verbose_name='Orden')
    
    # Configuración del paso
    is_required = models.BooleanField(default=True, verbose_name='Requerido')
    is_parallel = models.BooleanField(default=False, verbose_name='Paralelo')
    time_limit = models.DurationField(null=True, blank=True, verbose_name='Tiempo Límite')
    auto_advance = models.BooleanField(default=False, verbose_name='Avance Automático')
    
    # Asignación de usuarios
    assigned_to_role = models.CharField(max_length=50, blank=True, verbose_name='Rol Asignado')
    assigned_to_user = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name='Usuario Asignado'
    )
    assigned_to_group = models.CharField(max_length=50, blank=True, verbose_name='Grupo Asignado')
    
    # Condiciones y acciones
    condition_expression = models.TextField(blank=True, verbose_name='Expresión de Condición')
    action_script = models.TextField(blank=True, verbose_name='Script de Acción')
    
    # Configuración de notificaciones
    notify_on_start = models.BooleanField(default=True, verbose_name='Notificar al Iniciar')
    notify_on_complete = models.BooleanField(default=True, verbose_name='Notificar al Completar')
    notify_on_timeout = models.BooleanField(default=True, verbose_name='Notificar al Vencimiento')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template', 'order']
        unique_together = ['template', 'order']
        verbose_name = 'Paso de Workflow'
        verbose_name_plural = 'Pasos de Workflow'
    
    def __str__(self):
        return f"{self.template.name} - {self.name}"


class WorkflowInstance(models.Model):
    """Instancia de workflow ejecutándose"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
        ('timeout', 'Tiempo Agotado'),
    ]
    
    template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name='instances')
    
    # Objeto relacionado
    related_incident_id = models.PositiveIntegerField(null=True, blank=True)
    related_document_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Estado del workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    current_step = models.ForeignKey(
        WorkflowStep, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name='Paso Actual'
    )
    
    # Fechas
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Usuarios
    started_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='started_workflows'
    )
    completed_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='completed_workflows'
    )
    
    # Datos del contexto
    context_data = models.JSONField(default=dict, blank=True)
    result_data = models.JSONField(default=dict, blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Instancia de Workflow'
        verbose_name_plural = 'Instancias de Workflow'
    
    def __str__(self):
        return f"{self.template.name} - {self.get_status_display()}"
    
    @property
    def is_active(self):
        """Verificar si el workflow está activo"""
        return self.status in ['pending', 'in_progress']
    
    @property
    def is_completed(self):
        """Verificar si el workflow está completado"""
        return self.status == 'completed'
    
    @property
    def progress_percentage(self):
        """Calcular porcentaje de progreso"""
        if not self.current_step:
            return 0
        
        total_steps = self.template.steps.count()
        current_step_order = self.current_step.order
        
        return (current_step_order / total_steps) * 100
    
    def can_be_approved_by(self, user):
        """Verificar si un usuario puede aprobar el workflow"""
        if not self.current_step:
            return False
        
        # Verificar si el usuario está asignado al paso actual
        if self.current_step.assigned_to_user == user:
            return True
        
        # Verificar por rol
        if self.current_step.assigned_to_role:
            # Aquí se implementaría la lógica de verificación de roles
            pass
        
        # Verificar por grupo
        if self.current_step.assigned_to_group:
            # Aquí se implementaría la lógica de verificación de grupos
            pass
        
        return False


class WorkflowApproval(models.Model):
    """Aprobaciones de pasos de workflow"""
    
    APPROVAL_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('delegated', 'Delegado'),
    ]
    
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name='approvals')
    step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, related_name='approvals')
    
    # Usuario que debe aprobar
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflow_approvals')
    
    # Estado de la aprobación
    status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='pending')
    
    # Comentarios y justificación
    comments = models.TextField(blank=True, verbose_name='Comentarios')
    justification = models.TextField(blank=True, verbose_name='Justificación')
    
    # Delegación
    delegated_to = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='delegated_approvals'
    )
    
    # Fechas
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Metadatos
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
        unique_together = ['instance', 'step', 'approver']
        verbose_name = 'Aprobación de Workflow'
        verbose_name_plural = 'Aprobaciones de Workflow'
    
    def __str__(self):
        return f"{self.instance} - {self.step.name} - {self.approver.username}"
    
    @property
    def is_pending(self):
        """Verificar si la aprobación está pendiente"""
        return self.status == 'pending'
    
    @property
    def is_approved(self):
        """Verificar si la aprobación está aprobada"""
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        """Verificar si la aprobación está rechazada"""
        return self.status == 'rejected'
    
    @property
    def is_overdue(self):
        """Verificar si la aprobación está vencida"""
        if not self.due_date:
            return False
        return timezone.now() > self.due_date and self.status == 'pending'


class WorkflowHistory(models.Model):
    """Historial de cambios en workflows"""
    
    ACTION_CHOICES = [
        ('started', 'Iniciado'),
        ('step_started', 'Paso Iniciado'),
        ('step_completed', 'Paso Completado'),
        ('step_rejected', 'Paso Rechazado'),
        ('step_delegated', 'Paso Delegado'),
        ('step_timeout', 'Paso Vencido'),
        ('workflow_completed', 'Workflow Completado'),
        ('workflow_rejected', 'Workflow Rechazado'),
        ('workflow_cancelled', 'Workflow Cancelado'),
        ('workflow_timeout', 'Workflow Vencido'),
    ]
    
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name='history')
    step = models.ForeignKey(WorkflowStep, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Acción realizada
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(verbose_name='Descripción')
    
    # Usuario que realizó la acción
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflow_history')
    
    # Datos adicionales
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Historial de Workflow'
        verbose_name_plural = 'Historial de Workflows'
    
    def __str__(self):
        return f"{self.instance} - {self.get_action_display()} - {self.user.username}"


class WorkflowRule(models.Model):
    """Reglas automáticas para workflows"""
    
    RULE_TYPES = [
        ('auto_start', 'Inicio Automático'),
        ('auto_approve', 'Aprobación Automática'),
        ('auto_reject', 'Rechazo Automático'),
        ('auto_escalate', 'Escalación Automática'),
        ('auto_notify', 'Notificación Automática'),
        ('auto_assign', 'Asignación Automática'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción', blank=True)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES, verbose_name='Tipo de Regla')
    
    # Condiciones
    condition_expression = models.TextField(verbose_name='Expresión de Condición')
    
    # Acciones
    action_script = models.TextField(verbose_name='Script de Acción')
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    priority = models.PositiveIntegerField(default=0, verbose_name='Prioridad')
    
    # Aplicación
    workflow_template = models.ForeignKey(
        WorkflowTemplate, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        verbose_name='Plantilla de Workflow'
    )
    step = models.ForeignKey(
        WorkflowStep, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        verbose_name='Paso de Workflow'
    )
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workflow_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = 'Regla de Workflow'
        verbose_name_plural = 'Reglas de Workflow'
    
    def __str__(self):
        return f"{self.name} - {self.get_rule_type_display()}"