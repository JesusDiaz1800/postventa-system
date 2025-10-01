"""
Serializers para el sistema de auditoría
"""
from rest_framework import serializers
from .models import AuditLog
from apps.users.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de auditoría"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.ReadOnlyField()
    resource_type_display = serializers.ReadOnlyField()
    user_display = serializers.ReadOnlyField()
    created_at_display = serializers.ReadOnlyField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_username', 'user_display', 'action', 'action_display',
            'resource_type', 'resource_type_display', 'resource_id',
            'details', 'ip_address', 'user_agent', 'metadata',
            'created_at', 'created_at_display'
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar logs de auditoría"""
    user_display = serializers.ReadOnlyField()
    action_display = serializers.ReadOnlyField()
    resource_type_display = serializers.ReadOnlyField()
    created_at_display = serializers.ReadOnlyField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_display', 'action', 'action_display',
            'resource_type', 'resource_type_display', 'resource_id',
            'details', 'ip_address', 'created_at', 'created_at_display'
        ]


class AuditLogFilterSerializer(serializers.Serializer):
    """Serializer para filtros de logs de auditoría"""
    user = serializers.CharField(required=False, allow_blank=True)
    action = serializers.ChoiceField(
        choices=AuditLog.ACTION_CHOICES,
        required=False,
        allow_blank=True
    )
    resource_type = serializers.ChoiceField(
        choices=AuditLog.RESOURCE_TYPE_CHOICES,
        required=False,
        allow_blank=True
    )
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    search = serializers.CharField(required=False, allow_blank=True)
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=50)