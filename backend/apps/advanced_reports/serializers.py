from rest_framework import serializers
from .models import (
    ReportTemplate, ReportInstance, ReportSchedule, 
    ReportDashboard, ReportWidget, ReportExport
)
from django.contrib.auth.models import User


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer para ReportTemplate"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    instances_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'report_type', 'format', 'status',
            'template_config', 'data_sources', 'filters', 'grouping', 'sorting',
            'charts_config', 'tables_config', 'layout_config',
            'is_scheduled', 'schedule_cron', 'schedule_timezone',
            'email_recipients', 'auto_generate', 'retention_days',
            'is_public', 'tags', 'created_by', 'created_by_username', 'created_by_full_name',
            'created_at', 'updated_at', 'instances_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'instances_count']
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None
    
    def get_instances_count(self, obj):
        return obj.instances.count()


class ReportInstanceSerializer(serializers.ModelSerializer):
    """Serializer para ReportInstance"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportInstance
        fields = [
            'id', 'template', 'template_name', 'status',
            'custom_filters', 'custom_config', 'report_data', 'metadata',
            'file_path', 'file_url', 'file_size', 'file_hash',
            'requested_at', 'started_at', 'completed_at', 'expires_at',
            'requested_by', 'requested_by_username',
            'generated_by', 'generated_by_username',
            'error_message', 'error_details'
        ]
        read_only_fields = ['requested_at', 'started_at', 'completed_at']
    
    def get_file_url(self, obj):
        if obj.file_path and obj.status == 'completed':
            return f"/api/advanced-reports/instances/{obj.id}/download/"
        return None


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer para ReportSchedule"""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'template', 'template_name', 'name', 'description', 'status',
            'cron_expression', 'timezone', 'auto_execute',
            'max_retries', 'retry_delay', 'email_recipients', 'webhook_url',
            'last_executed', 'next_execution', 'created_at', 'updated_at',
            'created_by', 'created_by_username', 'created_by_full_name'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_executed', 'next_execution']
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None


class ReportDashboardSerializer(serializers.ModelSerializer):
    """Serializer para ReportDashboard"""
    
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportDashboard
        fields = [
            'id', 'name', 'description', 'layout_config', 'widgets_config', 'filters_config',
            'auto_refresh', 'refresh_interval', 'is_public', 'allowed_users', 'allowed_groups',
            'tags', 'created_by', 'created_by_username', 'created_by_full_name',
            'created_at', 'updated_at', 'widgets_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'widgets_count']
    
    def get_created_by_full_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None
    
    def get_widgets_count(self, obj):
        return obj.widgets.count()


class ReportWidgetSerializer(serializers.ModelSerializer):
    """Serializer para ReportWidget"""
    
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    
    class Meta:
        model = ReportWidget
        fields = [
            'id', 'dashboard', 'dashboard_name', 'name', 'description', 'widget_type',
            'position', 'size', 'config', 'data_source', 'filters', 'aggregation',
            'chart_type', 'colors', 'labels', 'auto_refresh', 'refresh_interval',
            'is_active', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReportExportSerializer(serializers.ModelSerializer):
    """Serializer para ReportExport"""
    
    instance_template_name = serializers.CharField(source='instance.template.name', read_only=True)
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportExport
        fields = [
            'id', 'instance', 'instance_template_name', 'export_format', 'status',
            'export_config', 'file_path', 'file_url', 'file_size', 'file_hash',
            'requested_at', 'completed_at', 'requested_by', 'requested_by_username',
            'error_message', 'error_details'
        ]
        read_only_fields = ['requested_at', 'completed_at']
    
    def get_file_url(self, obj):
        if obj.file_path and obj.status == 'completed':
            return f"/api/advanced-reports/exports/{obj.id}/download/"
        return None


class ReportGenerationSerializer(serializers.Serializer):
    """Serializer para generación de reportes"""
    
    template_id = serializers.IntegerField()
    custom_filters = serializers.JSONField(default=dict, required=False)
    custom_config = serializers.JSONField(default=dict, required=False)
    format = serializers.ChoiceField(choices=ReportTemplate.FORMAT_CHOICES, required=False)
    email_recipients = serializers.ListField(child=serializers.EmailField(), required=False)


class ReportScheduleCreateSerializer(serializers.Serializer):
    """Serializer para creación de programaciones de reportes"""
    
    template_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    cron_expression = serializers.CharField(max_length=100)
    timezone = serializers.CharField(max_length=50, default='UTC')
    auto_execute = serializers.BooleanField(default=True)
    email_recipients = serializers.ListField(child=serializers.EmailField(), required=False)
    webhook_url = serializers.URLField(required=False, allow_blank=True)


class ReportDashboardCreateSerializer(serializers.Serializer):
    """Serializer para creación de dashboards"""
    
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    layout_config = serializers.JSONField(default=dict, required=False)
    widgets_config = serializers.JSONField(default=list, required=False)
    is_public = serializers.BooleanField(default=False)
    allowed_users = serializers.ListField(child=serializers.IntegerField(), required=False)
    allowed_groups = serializers.ListField(child=serializers.CharField(), required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class ReportWidgetCreateSerializer(serializers.Serializer):
    """Serializer para creación de widgets"""
    
    dashboard_id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    widget_type = serializers.ChoiceField(choices=ReportWidget.WIDGET_TYPES)
    position = serializers.JSONField(default=dict, required=False)
    size = serializers.JSONField(default=dict, required=False)
    config = serializers.JSONField(default=dict, required=False)
    data_source = serializers.JSONField(default=dict, required=False)
    chart_type = serializers.ChoiceField(choices=ReportWidget.CHART_TYPES, required=False)
    order = serializers.IntegerField(default=0, required=False)


class ReportExportCreateSerializer(serializers.Serializer):
    """Serializer para creación de exportaciones"""
    
    instance_id = serializers.IntegerField()
    export_format = serializers.ChoiceField(choices=ReportExport.EXPORT_FORMATS)
    export_config = serializers.JSONField(default=dict, required=False)


class ReportStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de reportes"""
    
    total_templates = serializers.IntegerField()
    active_templates = serializers.IntegerField()
    total_instances = serializers.IntegerField()
    completed_instances = serializers.IntegerField()
    failed_instances = serializers.IntegerField()
    total_dashboards = serializers.IntegerField()
    public_dashboards = serializers.IntegerField()
    total_schedules = serializers.IntegerField()
    active_schedules = serializers.IntegerField()
    by_type = serializers.DictField()
    by_format = serializers.DictField()
    by_status = serializers.DictField()
    recent_activity = serializers.DictField()
