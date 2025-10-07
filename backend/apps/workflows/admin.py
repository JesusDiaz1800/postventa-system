from django.contrib import admin
from .models import (
    WorkflowTemplate, 
    WorkflowStep, 
    WorkflowInstance, 
    WorkflowApproval, 
    WorkflowHistory,
    WorkflowRule
)


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowTemplate model"""
    
    list_display = [
        'name', 'workflow_type', 'is_active', 'is_default', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'workflow_type', 'is_active', 'is_default', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'workflow_type')
        }),
        ('Configuración', {
            'fields': ('is_active', 'is_default', 'auto_start', 'allow_parallel', 'max_duration')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowStep model"""
    
    list_display = [
        'template', 'name', 'step_type', 'order', 'is_required', 'assigned_to_user'
    ]
    
    list_filter = [
        'template', 'step_type', 'is_required', 'is_parallel'
    ]
    
    search_fields = [
        'name', 'description', 'template__name'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Paso', {
            'fields': ('template', 'name', 'description', 'step_type', 'order')
        }),
        ('Configuración', {
            'fields': ('is_required', 'is_parallel', 'time_limit', 'auto_advance')
        }),
        ('Asignación', {
            'fields': ('assigned_to_role', 'assigned_to_user', 'assigned_to_group')
        }),
        ('Condiciones y Acciones', {
            'fields': ('condition_expression', 'action_script')
        }),
        ('Notificaciones', {
            'fields': ('notify_on_start', 'notify_on_complete', 'notify_on_timeout')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowInstance model"""
    
    list_display = [
        'template', 'status', 'current_step', 'started_by', 'started_at'
    ]
    
    list_filter = [
        'status', 'template', 'started_at'
    ]
    
    search_fields = [
        'template__name', 'started_by__username'
    ]
    
    readonly_fields = ['started_at', 'completed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Instancia', {
            'fields': ('template', 'status', 'current_step')
        }),
        ('Objetos Relacionados', {
            'fields': ('related_incident', 'related_document')
        }),
        ('Usuarios', {
            'fields': ('started_by', 'completed_by')
        }),
        ('Fechas', {
            'fields': ('started_at', 'completed_at', 'due_date')
        }),
        ('Datos', {
            'fields': ('context_data', 'result_data')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WorkflowApproval)
class WorkflowApprovalAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowApproval model"""
    
    list_display = [
        'instance', 'step', 'approver', 'status', 'assigned_at'
    ]
    
    list_filter = [
        'status', 'step', 'assigned_at'
    ]
    
    search_fields = [
        'instance__template__name', 'approver__username'
    ]
    
    readonly_fields = ['assigned_at', 'completed_at']
    
    fieldsets = (
        ('Aprobación', {
            'fields': ('instance', 'step', 'approver', 'status')
        }),
        ('Comentarios', {
            'fields': ('comments', 'justification')
        }),
        ('Delegación', {
            'fields': ('delegated_to',)
        }),
        ('Fechas', {
            'fields': ('assigned_at', 'completed_at', 'due_date')
        }),
        ('Metadatos', {
            'fields': ('metadata',)
        }),
    )


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowHistory model"""
    
    list_display = [
        'instance', 'step', 'action', 'user', 'timestamp'
    ]
    
    list_filter = [
        'action', 'timestamp'
    ]
    
    search_fields = [
        'instance__template__name', 'user__username', 'description'
    ]
    
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Historial', {
            'fields': ('instance', 'step', 'action', 'description')
        }),
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Cambios', {
            'fields': ('old_values', 'new_values')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'timestamp')
        }),
    )


@admin.register(WorkflowRule)
class WorkflowRuleAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowRule model"""
    
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
        ('Condiciones', {
            'fields': ('condition_expression',)
        }),
        ('Acciones', {
            'fields': ('action_script',)
        }),
        ('Configuración', {
            'fields': ('is_active', 'priority')
        }),
        ('Aplicación', {
            'fields': ('workflow_template', 'step')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
