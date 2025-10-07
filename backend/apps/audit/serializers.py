from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AuditLog, AuditRule, AuditReport, AuditDashboard, AuditAlert


class UserSerializer(serializers.ModelSerializer):
    """Serializer para información básica de usuario"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para registros de auditoría"""
    user = UserSerializer(read_only=True)
    action_display = serializers.SerializerMethodField()
    result_display = serializers.SerializerMethodField()
    severity_display = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    formatted_timestamp = serializers.ReadOnlyField()
    formatted_duration = serializers.ReadOnlyField()
    is_successful = serializers.ReadOnlyField()
    is_failure = serializers.ReadOnlyField()
    is_high_severity = serializers.ReadOnlyField()
    changes_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'action_display', 'result', 'result_display',
            'description', 'user', 'session_key', 'ip_address', 'user_agent',
            'content_type', 'object_id', 'content_object', 'old_values',
            'new_values', 'metadata', 'timestamp', 'formatted_timestamp',
            'duration', 'formatted_duration', 'module', 'function',
            'line_number', 'severity', 'severity_display', 'category',
            'category_display', 'request_id', 'correlation_id',
            'is_successful', 'is_failure', 'is_high_severity',
            'changes_summary'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_action_display(self, obj):
        """Obtener display de la acción"""
        return dict(AuditLog.ACTION_TYPES).get(obj.action, obj.action)
    
    def get_result_display(self, obj):
        """Obtener display del resultado"""
        return dict(AuditLog.RESULT_TYPES).get(obj.result, obj.result)
    
    def get_severity_display(self, obj):
        """Obtener display de la severidad"""
        return dict(AuditLog._meta.get_field('severity').choices).get(obj.severity, obj.severity)
    
    def get_category_display(self, obj):
        """Obtener display de la categoría"""
        return dict(AuditLog._meta.get_field('category').choices).get(obj.category, obj.category)
    
    def get_changes_summary(self, obj):
        """Obtener resumen de cambios"""
        return obj.get_changes_summary()


class AuditLogCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear registros de auditoría"""
    class Meta:
        model = AuditLog
        fields = [
            'action', 'result', 'description', 'session_key', 'ip_address',
            'user_agent', 'content_type', 'object_id', 'old_values',
            'new_values', 'metadata', 'duration', 'module', 'function',
            'line_number', 'severity', 'category', 'request_id', 'correlation_id'
        ]
    
    def create(self, validated_data):
        """Crear registro de auditoría"""
        # Obtener usuario del contexto
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        
        return super().create(validated_data)


class AuditRuleSerializer(serializers.ModelSerializer):
    """Serializer para reglas de auditoría"""
    created_by = UserSerializer(read_only=True)
    rule_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'rule_type_display',
            'action_filter', 'user_filter', 'ip_filter', 'module_filter',
            'severity_filter', 'category_filter', 'is_active', 'priority',
            'alert_email', 'alert_webhook', 'block_action', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_rule_type_display(self, obj):
        """Obtener display del tipo de regla"""
        return dict(AuditRule.RULE_TYPES).get(obj.rule_type, obj.rule_type)


class AuditReportSerializer(serializers.ModelSerializer):
    """Serializer para reportes de auditoría"""
    created_by = UserSerializer(read_only=True)
    report_type_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    is_completed = serializers.ReadOnlyField()
    is_generating = serializers.ReadOnlyField()
    formatted_file_size = serializers.ReadOnlyField()
    
    class Meta:
        model = AuditReport
        fields = [
            'id', 'name', 'description', 'report_type', 'report_type_display',
            'status', 'status_display', 'date_from', 'date_to', 'user_filter',
            'action_filter', 'severity_filter', 'category_filter',
            'include_details', 'include_changes', 'include_metadata',
            'group_by', 'total_records', 'file_path', 'file_size',
            'formatted_file_size', 'created_by', 'created_at',
            'completed_at', 'is_completed', 'is_generating'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']
    
    def get_report_type_display(self, obj):
        """Obtener display del tipo de reporte"""
        return dict(AuditReport.REPORT_TYPES).get(obj.report_type, obj.report_type)
    
    def get_status_display(self, obj):
        """Obtener display del estado"""
        return dict(AuditReport.STATUS_CHOICES).get(obj.status, obj.status)


class AuditReportCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reportes de auditoría"""
    class Meta:
        model = AuditReport
        fields = [
            'name', 'description', 'report_type', 'date_from', 'date_to',
            'user_filter', 'action_filter', 'severity_filter', 'category_filter',
            'include_details', 'include_changes', 'include_metadata', 'group_by'
        ]
    
    def create(self, validated_data):
        """Crear reporte de auditoría"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AuditDashboardSerializer(serializers.ModelSerializer):
    """Serializer para dashboards de auditoría"""
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditDashboard
        fields = [
            'id', 'name', 'description', 'widgets_config', 'default_filters',
            'auto_refresh', 'refresh_interval', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditAlertSerializer(serializers.ModelSerializer):
    """Serializer para alertas de auditoría"""
    audit_log = AuditLogSerializer(read_only=True)
    resolved_by = UserSerializer(read_only=True)
    severity_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    is_active = serializers.ReadOnlyField()
    is_resolved = serializers.ReadOnlyField()
    
    class Meta:
        model = AuditAlert
        fields = [
            'id', 'title', 'description', 'severity', 'severity_display',
            'status', 'status_display', 'audit_log', 'resolved_by',
            'resolved_at', 'resolution_notes', 'created_at', 'updated_at',
            'is_active', 'is_resolved'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_severity_display(self, obj):
        """Obtener display de la severidad"""
        return dict(AuditAlert.SEVERITY_LEVELS).get(obj.severity, obj.severity)
    
    def get_status_display(self, obj):
        """Obtener display del estado"""
        return dict(AuditAlert.STATUS_CHOICES).get(obj.status, obj.status)


class AuditAlertActionSerializer(serializers.Serializer):
    """Serializer para acciones de alertas"""
    ACTION_CHOICES = [
        ('resolve', 'Resolver'),
        ('acknowledge', 'Reconocer'),
        ('dismiss', 'Descartar'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class AuditStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de auditoría"""
    total_logs = serializers.IntegerField()
    logs_today = serializers.IntegerField()
    logs_this_week = serializers.IntegerField()
    logs_this_month = serializers.IntegerField()
    successful_actions = serializers.IntegerField()
    failed_actions = serializers.IntegerField()
    high_severity_logs = serializers.IntegerField()
    critical_logs = serializers.IntegerField()
    logs_by_action = serializers.DictField()
    logs_by_category = serializers.DictField()
    logs_by_severity = serializers.DictField()
    logs_by_user = serializers.DictField()
    top_ips = serializers.DictField()
    average_response_time = serializers.DurationField()
    error_rate = serializers.FloatField()


class AuditSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de auditoría"""
    query = serializers.CharField(required=False, allow_blank=True)
    action = serializers.CharField(required=False, allow_blank=True)
    result = serializers.CharField(required=False, allow_blank=True)
    user = serializers.IntegerField(required=False, allow_null=True)
    severity = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.CharField(required=False, allow_blank=True)
    module = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    ordering = serializers.ChoiceField(
        choices=['timestamp', '-timestamp', 'action', '-action', 'severity', '-severity'],
        required=False,
        default='-timestamp'
    )


class AuditExportSerializer(serializers.Serializer):
    """Serializer para exportación de auditoría"""
    format = serializers.ChoiceField(choices=['csv', 'xlsx', 'json', 'pdf'])
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    filters = serializers.JSONField(required=False, default=dict)
    include_details = serializers.BooleanField(default=True)
    include_changes = serializers.BooleanField(default=True)
    include_metadata = serializers.BooleanField(default=False)
    group_by = serializers.CharField(required=False, allow_blank=True)


class AuditDashboardWidgetSerializer(serializers.Serializer):
    """Serializer para widgets del dashboard"""
    widget_type = serializers.CharField()
    title = serializers.CharField()
    config = serializers.JSONField(default=dict)
    position = serializers.JSONField(default=dict)
    size = serializers.JSONField(default=dict)
    filters = serializers.JSONField(default=dict)
    refresh_interval = serializers.IntegerField(default=300)
    is_visible = serializers.BooleanField(default=True)


class AuditRealTimeSerializer(serializers.Serializer):
    """Serializer para datos en tiempo real de auditoría"""
    timestamp = serializers.DateTimeField()
    action = serializers.CharField()
    user = serializers.CharField()
    result = serializers.CharField()
    severity = serializers.CharField()
    description = serializers.CharField()
    ip_address = serializers.IPAddressField()
    module = serializers.CharField()
    duration = serializers.DurationField()