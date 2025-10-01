from rest_framework import serializers
from .models import Workflow, WorkflowState, WorkflowTransition, IncidentWorkflow, WorkflowHistory
from apps.users.serializers import UserSerializer


class WorkflowStateSerializer(serializers.ModelSerializer):
    """Serializer for workflow states"""
    
    class Meta:
        model = WorkflowState
        fields = [
            'id', 'name', 'display_name', 'description', 'is_initial',
            'is_final', 'order', 'required_actions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    """Serializer for workflow transitions"""
    from_state = WorkflowStateSerializer(read_only=True)
    to_state = WorkflowStateSerializer(read_only=True)
    
    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'from_state', 'to_state', 'name', 'display_name',
            'description', 'required_conditions', 'required_actions',
            'allowed_roles', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowSerializer(serializers.ModelSerializer):
    """Serializer for workflows"""
    created_by = UserSerializer(read_only=True)
    states = WorkflowStateSerializer(many=True, read_only=True)
    transitions = WorkflowTransitionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'incident_type', 'is_active',
            'created_by', 'states', 'transitions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class WorkflowCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating workflows"""
    
    class Meta:
        model = Workflow
        fields = [
            'name', 'description', 'incident_type', 'is_active'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkflowStateCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating workflow states"""
    
    class Meta:
        model = WorkflowState
        fields = [
            'name', 'display_name', 'description', 'is_initial',
            'is_final', 'order', 'required_actions'
        ]


class WorkflowTransitionCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating workflow transitions"""
    
    class Meta:
        model = WorkflowTransition
        fields = [
            'from_state', 'to_state', 'name', 'display_name',
            'description', 'required_conditions', 'required_actions',
            'allowed_roles', 'is_active'
        ]


class IncidentWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for incident workflows"""
    workflow = WorkflowSerializer(read_only=True)
    current_state = WorkflowStateSerializer(read_only=True)
    
    class Meta:
        model = IncidentWorkflow
        fields = [
            'id', 'workflow', 'current_state', 'started_at', 'updated_at'
        ]
        read_only_fields = ['id', 'started_at', 'updated_at']


class WorkflowHistorySerializer(serializers.ModelSerializer):
    """Serializer for workflow history"""
    user = UserSerializer(read_only=True)
    from_state = WorkflowStateSerializer(read_only=True)
    to_state = WorkflowStateSerializer(read_only=True)
    transition = WorkflowTransitionSerializer(read_only=True)
    
    class Meta:
        model = WorkflowHistory
        fields = [
            'id', 'from_state', 'to_state', 'transition', 'user',
            'description', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowTransitionRequestSerializer(serializers.Serializer):
    """Serializer for workflow transition requests"""
    to_state_id = serializers.IntegerField(help_text='ID del estado destino')
    description = serializers.CharField(help_text='Descripción de la transición')
    metadata = serializers.JSONField(
        default=dict,
        help_text='Metadatos adicionales'
    )
