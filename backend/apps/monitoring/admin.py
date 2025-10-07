from django.contrib import admin
from .models import (
    MonitoringRule, Alert, MetricValue, HealthCheck, HealthCheckResult,
    SystemMetrics, NotificationChannel, AlertTemplate, MonitoringDashboard,
    MonitoringWidget
)


@admin.register(MonitoringRule)
class MonitoringRuleAdmin(admin.ModelAdmin):
    """Admin interface for MonitoringRule model"""
    
    list_display = [
        'name', 'metric_type', 'metric_name', 'comparison_operator',
        'threshold_value', 'severity', 'is_active', 'created_by'
    ]
    list_filter = [
        'metric_type', 'severity', 'is_active', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'metric_name', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'metric_type', 'metric_name')
        }),
        ('Configuración de Regla', {
            'fields': ('comparison_operator', 'threshold_value', 'severity')
        }),
        ('Configuración de Ejecución', {
            'fields': ('is_active', 'check_interval', 'notification_channels')
        }),
        ('Metadatos', {
            'fields': ('tags', 'created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin interface for Alert model"""
    
    list_display = [
        'title', 'rule', 'severity', 'status', 'triggered_at',
        'acknowledged_by', 'resolved_by'
    ]
    list_filter = [
        'severity', 'status', 'triggered_at', 'acknowledged_at', 'resolved_at'
    ]
    search_fields = [
        'title', 'message', 'rule__name', 'acknowledged_by__username',
        'resolved_by__username'
    ]
    readonly_fields = ['triggered_at', 'acknowledged_at', 'resolved_at']
    fieldsets = (
        ('Alerta', {
            'fields': ('rule', 'severity', 'status', 'title', 'message')
        }),
        ('Valores', {
            'fields': ('metric_value', 'threshold_value')
        }),
        ('Usuarios', {
            'fields': ('acknowledged_by', 'resolved_by')
        }),
        ('Fechas', {
            'fields': ('triggered_at', 'acknowledged_at', 'resolved_at')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'tags')
        }),
    )


@admin.register(MetricValue)
class MetricValueAdmin(admin.ModelAdmin):
    """Admin interface for MetricValue model"""
    
    list_display = [
        'rule', 'value', 'timestamp'
    ]
    list_filter = [
        'rule__metric_type', 'timestamp'
    ]
    search_fields = [
        'rule__name', 'rule__metric_name'
    ]
    readonly_fields = ['timestamp']
    fieldsets = (
        ('Valor de Métrica', {
            'fields': ('rule', 'value', 'timestamp')
        }),
        ('Metadatos', {
            'fields': ('metadata',)
        }),
    )


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    """Admin interface for HealthCheck model"""
    
    list_display = [
        'name', 'check_type', 'status', 'last_check', 'is_active', 'created_by'
    ]
    list_filter = [
        'check_type', 'status', 'is_active', 'last_check'
    ]
    search_fields = [
        'name', 'description', 'created_by__username'
    ]
    readonly_fields = ['last_check', 'created_at', 'updated_at']
    fieldsets = (
        ('Verificación de Salud', {
            'fields': ('name', 'description', 'check_type')
        }),
        ('Configuración', {
            'fields': ('endpoint', 'check_script', 'status', 'is_active')
        }),
        ('Configuración de Ejecución', {
            'fields': ('check_interval', 'timeout', 'retry_count')
        }),
        ('Metadatos', {
            'fields': ('tags', 'created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(HealthCheckResult)
class HealthCheckResultAdmin(admin.ModelAdmin):
    """Admin interface for HealthCheckResult model"""
    
    list_display = [
        'health_check', 'status', 'response_time', 'checked_at'
    ]
    list_filter = [
        'status', 'checked_at'
    ]
    search_fields = [
        'health_check__name', 'message'
    ]
    readonly_fields = ['checked_at']
    fieldsets = (
        ('Resultado', {
            'fields': ('health_check', 'status', 'response_time', 'message')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'checked_at')
        }),
    )


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    """Admin interface for SystemMetrics model"""
    
    list_display = [
        'metric_type', 'metric_name', 'value', 'unit', 'timestamp'
    ]
    list_filter = [
        'metric_type', 'timestamp'
    ]
    search_fields = [
        'metric_name'
    ]
    readonly_fields = ['timestamp']
    fieldsets = (
        ('Métrica del Sistema', {
            'fields': ('metric_type', 'metric_name', 'value', 'unit', 'timestamp')
        }),
        ('Metadatos', {
            'fields': ('metadata',)
        }),
    )


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    """Admin interface for NotificationChannel model"""
    
    list_display = [
        'name', 'channel_type', 'is_active', 'created_by'
    ]
    list_filter = [
        'channel_type', 'is_active', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Canal de Notificación', {
            'fields': ('name', 'description', 'channel_type')
        }),
        ('Configuración', {
            'fields': ('config', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(AlertTemplate)
class AlertTemplateAdmin(admin.ModelAdmin):
    """Admin interface for AlertTemplate model"""
    
    list_display = [
        'name', 'severity', 'is_default', 'created_by'
    ]
    list_filter = [
        'severity', 'is_default', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Plantilla', {
            'fields': ('name', 'description', 'severity', 'is_default')
        }),
        ('Contenido', {
            'fields': ('subject_template', 'message_template')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(MonitoringDashboard)
class MonitoringDashboardAdmin(admin.ModelAdmin):
    """Admin interface for MonitoringDashboard model"""
    
    list_display = [
        'name', 'is_public', 'created_by'
    ]
    list_filter = [
        'is_public', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Dashboard', {
            'fields': ('name', 'description', 'is_public')
        }),
        ('Configuración', {
            'fields': ('layout', 'widgets')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(MonitoringWidget)
class MonitoringWidgetAdmin(admin.ModelAdmin):
    """Admin interface for MonitoringWidget model"""
    
    list_display = [
        'name', 'widget_type', 'is_active', 'created_by'
    ]
    list_filter = [
        'widget_type', 'is_active', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Widget', {
            'fields': ('name', 'description', 'widget_type', 'is_active')
        }),
        ('Configuración', {
            'fields': ('config', 'position', 'size')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
