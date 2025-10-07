from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    MonitoringRule, Alert, MetricValue, HealthCheck, HealthCheckResult,
    SystemMetrics, NotificationChannel, AlertTemplate, MonitoringDashboard,
    MonitoringWidget
)


class MonitoringRuleSerializer(serializers.ModelSerializer):
    """Serializer para MonitoringRule"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = MonitoringRule
        fields = [
            'id', 'name', 'description', 'metric_type', 'metric_name',
            'comparison_operator', 'threshold_value', 'severity', 'is_active',
            'check_interval', 'notification_channels', 'tags', 'created_at',
            'updated_at', 'created_by', 'created_by_username'
        ]
        read_only_fields = ['created_at', 'updated_at']


class MonitoringRuleCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de MonitoringRule"""
    
    class Meta:
        model = MonitoringRule
        fields = [
            'name', 'description', 'metric_type', 'metric_name',
            'comparison_operator', 'threshold_value', 'severity', 'is_active',
            'check_interval', 'notification_channels', 'tags'
        ]


class AlertSerializer(serializers.ModelSerializer):
    """Serializer para Alert"""
    
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    acknowledged_by_username = serializers.CharField(source='acknowledged_by.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'rule', 'rule_name', 'status', 'severity', 'title', 'message',
            'metric_value', 'threshold_value', 'triggered_at', 'acknowledged_at',
            'resolved_at', 'acknowledged_by', 'acknowledged_by_username',
            'resolved_by', 'resolved_by_username', 'metadata', 'tags', 'duration'
        ]
        read_only_fields = ['triggered_at', 'acknowledged_at', 'resolved_at']
    
    def get_duration(self, obj):
        """Obtener duración de la alerta"""
        if obj.resolved_at:
            return (obj.resolved_at - obj.triggered_at).total_seconds()
        return (obj.triggered_at - obj.triggered_at).total_seconds()


class AlertCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de Alert"""
    
    class Meta:
        model = Alert
        fields = [
            'rule', 'severity', 'title', 'message', 'metric_value',
            'threshold_value', 'metadata', 'tags'
        ]


class AlertUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualización de Alert"""
    
    class Meta:
        model = Alert
        fields = ['status', 'message', 'metadata']
    
    def update(self, instance, validated_data):
        """Actualizar alerta con lógica de estado"""
        status = validated_data.get('status')
        
        if status == 'acknowledged' and instance.status == 'active':
            instance.acknowledged_at = timezone.now()
            instance.acknowledged_by = self.context['request'].user
        
        elif status == 'resolved' and instance.status in ['active', 'acknowledged']:
            instance.resolved_at = timezone.now()
            instance.resolved_by = self.context['request'].user
        
        return super().update(instance, validated_data)


class MetricValueSerializer(serializers.ModelSerializer):
    """Serializer para MetricValue"""
    
    rule_name = serializers.CharField(source='rule.name', read_only=True)
    
    class Meta:
        model = MetricValue
        fields = [
            'id', 'rule', 'rule_name', 'value', 'timestamp', 'metadata'
        ]
        read_only_fields = ['timestamp']


class MetricValueCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de MetricValue"""
    
    class Meta:
        model = MetricValue
        fields = ['rule', 'value', 'metadata']


class HealthCheckSerializer(serializers.ModelSerializer):
    """Serializer para HealthCheck"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = HealthCheck
        fields = [
            'id', 'name', 'description', 'check_type', 'endpoint',
            'check_script', 'status', 'last_check', 'check_interval',
            'timeout', 'retry_count', 'is_active', 'tags', 'created_at',
            'updated_at', 'created_by', 'created_by_username'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_check']


class HealthCheckCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de HealthCheck"""
    
    class Meta:
        model = HealthCheck
        fields = [
            'name', 'description', 'check_type', 'endpoint', 'check_script',
            'check_interval', 'timeout', 'retry_count', 'is_active', 'tags'
        ]


class HealthCheckResultSerializer(serializers.ModelSerializer):
    """Serializer para HealthCheckResult"""
    
    health_check_name = serializers.CharField(source='health_check.name', read_only=True)
    
    class Meta:
        model = HealthCheckResult
        fields = [
            'id', 'health_check', 'health_check_name', 'status',
            'response_time', 'message', 'metadata', 'checked_at'
        ]
        read_only_fields = ['checked_at']


class HealthCheckResultCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de HealthCheckResult"""
    
    class Meta:
        model = HealthCheckResult
        fields = [
            'health_check', 'status', 'response_time', 'message', 'metadata'
        ]


class SystemMetricsSerializer(serializers.ModelSerializer):
    """Serializer para SystemMetrics"""
    
    class Meta:
        model = SystemMetrics
        fields = [
            'id', 'metric_type', 'metric_name', 'value', 'unit',
            'timestamp', 'metadata'
        ]
        read_only_fields = ['timestamp']


class SystemMetricsCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de SystemMetrics"""
    
    class Meta:
        model = SystemMetrics
        fields = [
            'metric_type', 'metric_name', 'value', 'unit', 'metadata'
        ]


class NotificationChannelSerializer(serializers.ModelSerializer):
    """Serializer para NotificationChannel"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = NotificationChannel
        fields = [
            'id', 'name', 'description', 'channel_type', 'config',
            'is_active', 'created_at', 'updated_at', 'created_by',
            'created_by_username'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationChannelCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de NotificationChannel"""
    
    class Meta:
        model = NotificationChannel
        fields = [
            'name', 'description', 'channel_type', 'config', 'is_active'
        ]


class NotificationChannelTestSerializer(serializers.Serializer):
    """Serializer para probar canal de notificación"""
    
    test_message = serializers.CharField(max_length=500, default="Test message from monitoring system")
    test_data = serializers.JSONField(default=dict)


class AlertTemplateSerializer(serializers.ModelSerializer):
    """Serializer para AlertTemplate"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = AlertTemplate
        fields = [
            'id', 'name', 'description', 'subject_template', 'message_template',
            'severity', 'is_default', 'created_at', 'updated_at', 'created_by',
            'created_by_username'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AlertTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de AlertTemplate"""
    
    class Meta:
        model = AlertTemplate
        fields = [
            'name', 'description', 'subject_template', 'message_template',
            'severity', 'is_default'
        ]


class MonitoringDashboardSerializer(serializers.ModelSerializer):
    """Serializer para MonitoringDashboard"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = MonitoringDashboard
        fields = [
            'id', 'name', 'description', 'layout', 'widgets', 'is_public',
            'created_at', 'updated_at', 'created_by', 'created_by_username'
        ]
        read_only_fields = ['created_at', 'updated_at']


class MonitoringDashboardCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de MonitoringDashboard"""
    
    class Meta:
        model = MonitoringDashboard
        fields = [
            'name', 'description', 'layout', 'widgets', 'is_public'
        ]


class MonitoringWidgetSerializer(serializers.ModelSerializer):
    """Serializer para MonitoringWidget"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = MonitoringWidget
        fields = [
            'id', 'name', 'description', 'widget_type', 'config', 'position',
            'size', 'is_active', 'created_at', 'updated_at', 'created_by',
            'created_by_username'
        ]
        read_only_fields = ['created_at', 'updated_at']


class MonitoringWidgetCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación de MonitoringWidget"""
    
    class Meta:
        model = MonitoringWidget
        fields = [
            'name', 'description', 'widget_type', 'config', 'position',
            'size', 'is_active'
        ]


class MonitoringStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de monitoreo"""
    
    total_rules = serializers.IntegerField()
    active_rules = serializers.IntegerField()
    total_alerts = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    alerts_by_severity = serializers.DictField()
    health_checks_total = serializers.IntegerField()
    health_checks_healthy = serializers.IntegerField()
    health_checks_unhealthy = serializers.IntegerField()
    system_metrics_count = serializers.IntegerField()
    notification_channels_count = serializers.IntegerField()


class MonitoringExecutionSerializer(serializers.Serializer):
    """Serializer para ejecución de monitoreo"""
    
    rule_id = serializers.IntegerField(required=False)
    health_check_id = serializers.IntegerField(required=False)
    force_execution = serializers.BooleanField(default=False)


class MonitoringTestSerializer(serializers.Serializer):
    """Serializer para pruebas de monitoreo"""
    
    test_type = serializers.ChoiceField(choices=[
        ('rule', 'Regla'),
        ('health_check', 'Verificación de Salud'),
        ('notification_channel', 'Canal de Notificación')
    ])
    test_data = serializers.JSONField(default=dict)
