from django.contrib import admin
from .models import AuditLog, AuditRule, AuditReport, AuditDashboard, AuditAlert


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model"""
    
    list_display = [
        'action', 'user', 'result', 'severity', 'category', 'timestamp'
    ]
    
    list_filter = [
        'action', 'result', 'severity', 'category', 'timestamp'
    ]
    
    search_fields = [
        'description', 'user__username', 'ip_address', 'module'
    ]
    
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Acción', {
            'fields': ('action', 'result', 'description')
        }),
        ('Usuario y Sesión', {
            'fields': ('user', 'session_key', 'ip_address', 'user_agent')
        }),
        ('Objeto Relacionado', {
            'fields': ('content_type', 'object_id', 'content_object')
        }),
        ('Cambios', {
            'fields': ('old_values', 'new_values')
        }),
        ('Clasificación', {
            'fields': ('severity', 'category')
        }),
        ('Contexto', {
            'fields': ('module', 'function', 'line_number', 'duration')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'request_id', 'correlation_id', 'timestamp')
        }),
    )


@admin.register(AuditRule)
class AuditRuleAdmin(admin.ModelAdmin):
    """Admin interface for AuditRule model"""
    
    list_display = [
        'name', 'rule_type', 'is_active', 'priority', 'created_by'
    ]
    
    list_filter = [
        'rule_type', 'is_active', 'priority'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Regla', {
            'fields': ('name', 'description', 'rule_type')
        }),
        ('Filtros', {
            'fields': ('action_filter', 'user_filter', 'ip_filter', 'module_filter', 'severity_filter', 'category_filter')
        }),
        ('Configuración', {
            'fields': ('is_active', 'priority')
        }),
        ('Acciones', {
            'fields': ('alert_email', 'alert_webhook', 'block_action')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    """Admin interface for AuditReport model"""
    
    list_display = [
        'name', 'report_type', 'status', 'total_records', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'report_type', 'status', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'completed_at']
    
    fieldsets = (
        ('Reporte', {
            'fields': ('name', 'description', 'report_type', 'status')
        }),
        ('Filtros', {
            'fields': ('date_from', 'date_to', 'user_filter', 'action_filter', 'severity_filter', 'category_filter')
        }),
        ('Configuración', {
            'fields': ('include_details', 'include_changes', 'include_metadata', 'group_by')
        }),
        ('Resultados', {
            'fields': ('total_records', 'file_path', 'file_size')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'completed_at')
        }),
    )


@admin.register(AuditDashboard)
class AuditDashboardAdmin(admin.ModelAdmin):
    """Admin interface for AuditDashboard model"""
    
    list_display = [
        'name', 'auto_refresh', 'refresh_interval', 'created_by'
    ]
    
    list_filter = [
        'auto_refresh', 'created_at'
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
            'fields': ('widgets_config', 'default_filters')
        }),
        ('Actualización', {
            'fields': ('auto_refresh', 'refresh_interval')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(AuditAlert)
class AuditAlertAdmin(admin.ModelAdmin):
    """Admin interface for AuditAlert model"""
    
    list_display = [
        'title', 'severity', 'status', 'audit_log', 'created_at'
    ]
    
    list_filter = [
        'severity', 'status', 'created_at'
    ]
    
    search_fields = [
        'title', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Alerta', {
            'fields': ('title', 'description', 'severity', 'status')
        }),
        ('Registro de Auditoría', {
            'fields': ('audit_log',)
        }),
        ('Resolución', {
            'fields': ('resolved_by', 'resolved_at', 'resolution_notes')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at')
        }),
    )