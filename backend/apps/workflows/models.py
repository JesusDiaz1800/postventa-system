from django.db import models
from django.utils import timezone
from apps.users.models import User


class Workflow(models.Model):
    """
    Model for workflow definitions
    """
    name = models.CharField(
        max_length=200,
        help_text='Nombre del workflow'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Descripción del workflow'
    )
    
    incident_type = models.CharField(
        max_length=100,
        choices=[
            ('defecto_fabricacion', 'Defecto de Fabricación'),
            ('daño_transporte', 'Daño en Transporte'),
            ('calidad', 'Calidad'),
            ('embalaje', 'Embalaje'),
            ('etiquetado', 'Etiquetado'),
            ('tuberia_pp_rct', 'Tubería PP-RCT'),
            ('llave_bola', 'Llave de Bola'),
            ('accesorio', 'Accesorio'),
        ],
        help_text='Tipo de incidencia para el cual aplica este workflow'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el workflow está activo'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que creó el workflow'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflows'
        verbose_name = 'Workflow'
        verbose_name_plural = 'Workflows'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.incident_type})"


class WorkflowState(models.Model):
    """
    Model for workflow states
    """
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='states',
        help_text='Workflow al que pertenece este estado'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Nombre del estado'
    )
    
    display_name = models.CharField(
        max_length=200,
        help_text='Nombre para mostrar del estado'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Descripción del estado'
    )
    
    is_initial = models.BooleanField(
        default=False,
        help_text='Indica si es el estado inicial del workflow'
    )
    
    is_final = models.BooleanField(
        default=False,
        help_text='Indica si es un estado final del workflow'
    )
    
    order = models.IntegerField(
        default=0,
        help_text='Orden del estado en el workflow'
    )
    
    required_actions = models.JSONField(
        default=list,
        help_text='Acciones requeridas para completar este estado',
        choices=[
            ('upload_photos', 'Subir fotos'),
            ('complete_analysis', 'Completar análisis'),
            ('generate_document', 'Generar documento'),
            ('lab_report', 'Reporte de laboratorio'),
            ('approve_solution', 'Aprobar solución'),
            ('notify_client', 'Notificar cliente'),
            ('notify_provider', 'Notificar proveedor'),
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_states'
        verbose_name = 'Estado de Workflow'
        verbose_name_plural = 'Estados de Workflow'
        ordering = ['workflow', 'order']
        unique_together = ['workflow', 'name']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.display_name}"


class WorkflowTransition(models.Model):
    """
    Model for workflow transitions
    """
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='transitions',
        help_text='Workflow al que pertenece esta transición'
    )
    
    from_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.CASCADE,
        related_name='outgoing_transitions',
        help_text='Estado origen'
    )
    
    to_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.CASCADE,
        related_name='incoming_transitions',
        help_text='Estado destino'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Nombre de la transición'
    )
    
    display_name = models.CharField(
        max_length=200,
        help_text='Nombre para mostrar de la transición'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Descripción de la transición'
    )
    
    required_conditions = models.JSONField(
        default=list,
        help_text='Condiciones requeridas para realizar esta transición'
    )
    
    required_actions = models.JSONField(
        default=list,
        help_text='Acciones requeridas para realizar esta transición'
    )
    
    allowed_roles = models.JSONField(
        default=list,
        help_text='Roles que pueden realizar esta transición',
        choices=[
            ('admin', 'Admin'),
            ('supervisor', 'Supervisor'),
            ('analista', 'Analista'),
            ('atencion_cliente', 'Atención al Cliente'),
            ('proveedor', 'Proveedor'),
        ]
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si la transición está activa'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_transitions'
        verbose_name = 'Transición de Workflow'
        verbose_name_plural = 'Transiciones de Workflow'
        ordering = ['workflow', 'from_state__order']
        unique_together = ['workflow', 'from_state', 'to_state']
    
    def __str__(self):
        return f"{self.workflow.name}: {self.from_state.display_name} → {self.to_state.display_name}"


class IncidentWorkflow(models.Model):
    """
    Model for tracking incident workflow progress
    """
    incident = models.OneToOneField(
        'incidents.Incident',
        on_delete=models.CASCADE,
        related_name='workflow_progress',
        help_text='Incidencia relacionada'
    )
    
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.PROTECT,
        help_text='Workflow aplicado a la incidencia'
    )
    
    current_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.PROTECT,
        help_text='Estado actual de la incidencia'
    )
    
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de inicio del workflow'
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incident_workflows'
        verbose_name = 'Workflow de Incidencia'
        verbose_name_plural = 'Workflows de Incidencias'
    
    def __str__(self):
        return f"{self.incident.code} - {self.current_state.display_name}"


class WorkflowHistory(models.Model):
    """
    Model for tracking workflow history
    """
    incident_workflow = models.ForeignKey(
        IncidentWorkflow,
        on_delete=models.CASCADE,
        related_name='history',
        help_text='Workflow de la incidencia'
    )
    
    from_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.PROTECT,
        related_name='history_from',
        null=True,
        blank=True,
        help_text='Estado origen'
    )
    
    to_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.PROTECT,
        related_name='history_to',
        help_text='Estado destino'
    )
    
    transition = models.ForeignKey(
        WorkflowTransition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Transición utilizada'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Usuario que realizó la transición'
    )
    
    description = models.TextField(
        help_text='Descripción de la transición'
    )
    
    metadata = models.JSONField(
        default=dict,
        help_text='Metadatos adicionales de la transición'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workflow_history'
        verbose_name = 'Historial de Workflow'
        verbose_name_plural = 'Historiales de Workflow'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.incident_workflow.incident.code}: {self.from_state.display_name if self.from_state else 'Inicio'} → {self.to_state.display_name}"
