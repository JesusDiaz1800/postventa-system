from django.contrib import admin
from .models import (
    ReportTemplate, ReportInstance, ReportSchedule, 
    ReportDashboard, ReportWidget, ReportExport
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin interface for ReportTemplate model"""
    
    list_display = [
        'name', 'report_type', 'format', 'status', 'is_public', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'report_type', 'format', 'status', 'is_public', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'report_type', 'format', 'status')
        }),
        ('Configuración del Reporte', {
            'fields': ('template_config', 'data_sources', 'filters', 'grouping', 'sorting')
        }),
        ('Configuración de Visualización', {
            'fields': ('charts_config', 'tables_config', 'layout_config')
        }),
        ('Programación', {
            'fields': ('is_scheduled', 'schedule_cron', 'schedule_timezone')
        }),
        ('Distribución', {
            'fields': ('email_recipients', 'auto_generate', 'retention_days')
        }),
        ('Acceso', {
            'fields': ('is_public', 'tags')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ReportInstance)
class ReportInstanceAdmin(admin.ModelAdmin):
    """Admin interface for ReportInstance model"""
    
    list_display = [
        'template', 'status', 'requested_by', 'requested_at', 'completed_at'
    ]
    
    list_filter = [
        'status', 'template', 'requested_at'
    ]
    
    search_fields = [
        'template__name', 'requested_by__username'
    ]
    
    readonly_fields = ['requested_at', 'started_at', 'completed_at']
    
    fieldsets = (
        ('Instancia', {
            'fields': ('template', 'status')
        }),
        ('Configuración', {
            'fields': ('custom_filters', 'custom_config')
        }),
        ('Datos', {
            'fields': ('report_data', 'metadata')
        }),
        ('Archivo', {
            'fields': ('file_path', 'file_size', 'file_hash')
        }),
        ('Fechas', {
            'fields': ('requested_at', 'started_at', 'completed_at', 'expires_at')
        }),
        ('Usuarios', {
            'fields': ('requested_by', 'generated_by')
        }),
        ('Errores', {
            'fields': ('error_message', 'error_details')
        }),
    )


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    """Admin interface for ReportSchedule model"""
    
    list_display = [
        'name', 'template', 'status', 'cron_expression', 'last_executed', 'next_execution'
    ]
    
    list_filter = [
        'status', 'template', 'last_executed'
    ]
    
    search_fields = [
        'name', 'description', 'template__name'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'last_executed', 'next_execution']
    
    fieldsets = (
        ('Programación', {
            'fields': ('template', 'name', 'description', 'status')
        }),
        ('Configuración de Programación', {
            'fields': ('cron_expression', 'timezone')
        }),
        ('Configuración de Ejecución', {
            'fields': ('auto_execute', 'max_retries', 'retry_delay')
        }),
        ('Distribución', {
            'fields': ('email_recipients', 'webhook_url')
        }),
        ('Fechas', {
            'fields': ('last_executed', 'next_execution', 'created_at', 'updated_at')
        }),
        ('Metadatos', {
            'fields': ('created_by',)
        }),
    )


@admin.register(ReportDashboard)
class ReportDashboardAdmin(admin.ModelAdmin):
    """Admin interface for ReportDashboard model"""
    
    list_display = [
        'name', 'is_public', 'auto_refresh', 'refresh_interval', 'created_by'
    ]
    
    list_filter = [
        'is_public', 'auto_refresh', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Dashboard', {
            'fields': ('name', 'description')
        }),
        ('Configuración', {
            'fields': ('layout_config', 'widgets_config', 'filters_config')
        }),
        ('Actualización', {
            'fields': ('auto_refresh', 'refresh_interval')
        }),
        ('Acceso', {
            'fields': ('is_public', 'allowed_users', 'allowed_groups', 'tags')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ReportWidget)
class ReportWidgetAdmin(admin.ModelAdmin):
    """Admin interface for ReportWidget model"""
    
    list_display = [
        'name', 'dashboard', 'widget_type', 'chart_type', 'is_active', 'order'
    ]
    
    list_filter = [
        'widget_type', 'chart_type', 'is_active', 'dashboard'
    ]
    
    search_fields = [
        'name', 'description', 'dashboard__name'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Widget', {
            'fields': ('dashboard', 'name', 'description', 'widget_type')
        }),
        ('Posición y Tamaño', {
            'fields': ('position', 'size', 'order')
        }),
        ('Configuración', {
            'fields': ('config',)
        }),
        ('Datos', {
            'fields': ('data_source', 'filters', 'aggregation')
        }),
        ('Visualización', {
            'fields': ('chart_type', 'colors', 'labels')
        }),
        ('Actualización', {
            'fields': ('auto_refresh', 'refresh_interval')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    """Admin interface for ReportExport model"""
    
    list_display = [
        'instance', 'export_format', 'status', 'requested_by', 'requested_at', 'completed_at'
    ]
    
    list_filter = [
        'export_format', 'status', 'requested_at'
    ]
    
    search_fields = [
        'instance__template__name', 'requested_by__username'
    ]
    
    readonly_fields = ['requested_at', 'completed_at']
    
    fieldsets = (
        ('Exportación', {
            'fields': ('instance', 'export_format', 'status')
        }),
        ('Configuración', {
            'fields': ('export_config',)
        }),
        ('Archivo', {
            'fields': ('file_path', 'file_size', 'file_hash')
        }),
        ('Fechas', {
            'fields': ('requested_at', 'completed_at')
        }),
        ('Usuario', {
            'fields': ('requested_by',)
        }),
        ('Errores', {
            'fields': ('error_message', 'error_details')
        }),
    )
