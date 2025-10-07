from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    WorkflowTemplate, 
    WorkflowStep, 
    WorkflowInstance, 
    WorkflowApproval, 
    WorkflowHistory,
    WorkflowRule
)
from apps.incidents.models import Incident
from apps.documents.models import Document


class UserSerializer(serializers.ModelSerializer):
    """Serializer para información básica de usuario"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer para información básica de incidencia (ajustado a campos reales)."""
    class Meta:
        model = Incident
        fields = ['id', 'code', 'cliente', 'estado', 'prioridad']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer para información básica de documento (ajustado a campos reales)."""
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'is_final']


class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer para pasos de workflow"""
    assigned_to_user = UserSerializer(read_only=True)
    
    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'name', 'description', 'step_type', 'order', 'is_required',
            'is_parallel', 'time_limit', 'auto_advance', 'assigned_to_role',
            'assigned_to_user', 'assigned_to_group', 'condition_expression',
            'action_script', 'notify_on_start', 'notify_on_complete',
            'notify_on_timeout', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    """Serializer para plantillas de workflow"""
    steps = WorkflowStepSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    workflow_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowTemplate
        fields = [
            'id', 'name', 'description', 'workflow_type', 'workflow_type_display',
            'is_active', 'is_default', 'auto_start', 'allow_parallel',
            'max_duration', 'created_by', 'created_at', 'updated_at', 'steps'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_workflow_type_display(self, obj):
        """Obtener display del tipo de workflow"""
        return dict(WorkflowTemplate.WORKFLOW_TYPES).get(obj.workflow_type, obj.workflow_type)
    
    def create(self, validated_data):
        """Crear plantilla con pasos"""
        steps_data = self.context.get('steps_data', [])
        template = WorkflowTemplate.objects.create(**validated_data)
        
        for step_data in steps_data:
            WorkflowStep.objects.create(template=template, **step_data)
        
        return template


class WorkflowApprovalSerializer(serializers.ModelSerializer):
    """Serializer para aprobaciones de workflow"""
    approver = UserSerializer(read_only=True)
    delegated_to = UserSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowApproval
        fields = [
            'id', 'step', 'approver', 'status', 'status_display', 'comments',
            'justification', 'delegated_to', 'assigned_at', 'completed_at',
            'due_date', 'metadata'
        ]
        read_only_fields = ['id', 'assigned_at', 'completed_at']
    
    def get_status_display(self, obj):
        """Obtener display del estado"""
        return dict(WorkflowApproval.APPROVAL_CHOICES).get(obj.status, obj.status)


class WorkflowHistorySerializer(serializers.ModelSerializer):
    """Serializer para historial de workflow"""
    user = UserSerializer(read_only=True)
    step = WorkflowStepSerializer(read_only=True)
    action_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowHistory
        fields = [
            'id', 'step', 'action', 'action_display', 'description', 'user',
            'old_values', 'new_values', 'metadata', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_action_display(self, obj):
        """Obtener display de la acción"""
        return dict(WorkflowHistory.ACTION_CHOICES).get(obj.action, obj.action)


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Serializer para instancias de workflow"""
    template = WorkflowTemplateSerializer(read_only=True)
    current_step = WorkflowStepSerializer(read_only=True)
    # Model stores related_incident_id and related_document_id as integers.
    related_incident = serializers.SerializerMethodField()
    related_document = serializers.SerializerMethodField()
    started_by = UserSerializer(read_only=True)
    completed_by = UserSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    progress_percentage = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    approvals = WorkflowApprovalSerializer(many=True, read_only=True)
    history = WorkflowHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'template', 'related_incident', 'related_document',
            'status', 'status_display', 'current_step', 'started_at',
            'completed_at', 'due_date', 'started_by', 'completed_by',
            'context_data', 'result_data', 'progress_percentage',
            'is_active', 'is_completed', 'approvals', 'history',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_status_display(self, obj):
        """Obtener display del estado"""
        return dict(WorkflowInstance.STATUS_CHOICES).get(obj.status, obj.status)

    def get_related_incident(self, obj):
        try:
            if obj.related_incident_id:
                inc = Incident.objects.filter(id=obj.related_incident_id).first()
                if inc:
                    return IncidentSerializer(inc).data
        except Exception:
            pass
        return None

    def get_related_document(self, obj):
        try:
            if obj.related_document_id:
                doc = Document.objects.filter(id=obj.related_document_id).first()
                if doc:
                    return DocumentSerializer(doc).data
        except Exception:
            pass
        return None


class WorkflowInstanceCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear instancias de workflow"""
    class Meta:
        model = WorkflowInstance
        # Accept the integer id fields used by the model.
        fields = [
            'template', 'related_incident_id', 'related_document_id',
            'context_data', 'due_date'
        ]
    
    def create(self, validated_data):
        """Crear instancia de workflow"""
        validated_data['started_by'] = self.context['request'].user
        # Allow callers to provide related_incident / related_document as ids or as keys
        if 'related_incident' in validated_data and 'related_incident_id' not in validated_data:
            validated_data['related_incident_id'] = validated_data.pop('related_incident')
        if 'related_document' in validated_data and 'related_document_id' not in validated_data:
            validated_data['related_document_id'] = validated_data.pop('related_document')

        instance = WorkflowInstance.objects.create(**validated_data)
        
        # Iniciar el workflow
        instance.start_workflow()
        
        return instance


class WorkflowApprovalActionSerializer(serializers.Serializer):
    """Serializer para acciones de aprobación"""
    ACTION_CHOICES = [
        ('approve', 'Aprobar'),
        ('reject', 'Rechazar'),
        ('delegate', 'Delegar'),
        ('request_info', 'Solicitar Información'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    comments = serializers.CharField(required=False, allow_blank=True)
    justification = serializers.CharField(required=False, allow_blank=True)
    delegated_to = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_delegated_to(self, value):
        """Validar usuario delegado"""
        if value:
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Usuario no encontrado")
        return value


class WorkflowRuleSerializer(serializers.ModelSerializer):
    """Serializer para reglas de workflow"""
    created_by = UserSerializer(read_only=True)
    workflow_template = WorkflowTemplateSerializer(read_only=True)
    step = WorkflowStepSerializer(read_only=True)
    rule_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'rule_type_display',
            'condition_expression', 'action_script', 'is_active', 'priority',
            'workflow_template', 'step', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_rule_type_display(self, obj):
        """Obtener display del tipo de regla"""
        return dict(WorkflowRule.RULE_TYPES).get(obj.rule_type, obj.rule_type)


class WorkflowStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de workflow"""
    total_workflows = serializers.IntegerField()
    active_workflows = serializers.IntegerField()
    completed_workflows = serializers.IntegerField()
    rejected_workflows = serializers.IntegerField()
    pending_approvals = serializers.IntegerField()
    overdue_approvals = serializers.IntegerField()
    workflows_by_type = serializers.DictField()
    workflows_by_status = serializers.DictField()
    average_completion_time = serializers.DurationField()
    workflows_this_month = serializers.IntegerField()
    workflows_last_month = serializers.IntegerField()


class WorkflowDashboardSerializer(serializers.Serializer):
    """Serializer para dashboard de workflow"""
    my_pending_approvals = WorkflowApprovalSerializer(many=True)
    my_active_workflows = WorkflowInstanceSerializer(many=True)
    recent_workflows = WorkflowInstanceSerializer(many=True)
    stats = WorkflowStatsSerializer()
    overdue_workflows = WorkflowInstanceSerializer(many=True)
    upcoming_deadlines = WorkflowInstanceSerializer(many=True)


class WorkflowSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de workflows"""
    query = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    workflow_type = serializers.CharField(required=False, allow_blank=True)
    assigned_to = serializers.IntegerField(required=False, allow_null=True)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    ordering = serializers.ChoiceField(
        choices=['created_at', '-created_at', 'due_date', '-due_date', 'status'],
        required=False,
        default='-created_at'
    )