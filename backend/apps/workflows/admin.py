from django.contrib import admin
from .models import Workflow, WorkflowState, WorkflowTransition, IncidentWorkflow, WorkflowHistory


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """Admin interface for Workflow model"""
    
    list_display = [
        'name', 'incident_type', 'is_active', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'incident_type', 'is_active', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'incident_type')
        }),
        ('Configuración', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(WorkflowState)
class WorkflowStateAdmin(admin.ModelAdmin):
    """Admin interface for Workflow State model"""
    
    list_display = [
        'workflow', 'display_name', 'is_initial', 'is_final', 'order'
    ]
    
    list_filter = [
        'workflow', 'is_initial', 'is_final'
    ]
    
    search_fields = [
        'name', 'display_name', 'workflow__name'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Estado', {
            'fields': ('workflow', 'name', 'display_name', 'description')
        }),
        ('Configuración', {
            'fields': ('is_initial', 'is_final', 'order')
        }),
        ('Acciones Requeridas', {
            'fields': ('required_actions',)
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    """Admin interface for Workflow Transition model"""
    
    list_display = [
        'workflow', 'from_state', 'to_state', 'display_name', 'is_active'
    ]
    
    list_filter = [
        'workflow', 'is_active'
    ]
    
    search_fields = [
        'name', 'display_name', 'workflow__name'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Transición', {
            'fields': ('workflow', 'from_state', 'to_state', 'name', 'display_name', 'description')
        }),
        ('Configuración', {
            'fields': ('is_active', 'allowed_roles')
        }),
        ('Condiciones y Acciones', {
            'fields': ('required_conditions', 'required_actions')
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )


@admin.register(IncidentWorkflow)
class IncidentWorkflowAdmin(admin.ModelAdmin):
    """Admin interface for Incident Workflow model"""
    
    list_display = [
        'incident', 'workflow', 'current_state', 'started_at'
    ]
    
    list_filter = [
        'workflow', 'current_state', 'started_at'
    ]
    
    search_fields = [
        'incident__code', 'workflow__name'
    ]
    
    readonly_fields = ['started_at', 'updated_at']
    
    fieldsets = (
        ('Workflow', {
            'fields': ('incident', 'workflow', 'current_state')
        }),
        ('Fechas', {
            'fields': ('started_at', 'updated_at')
        }),
    )


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    """Admin interface for Workflow History model"""
    
    list_display = [
        'incident_workflow', 'from_state', 'to_state', 'user', 'created_at'
    ]
    
    list_filter = [
        'created_at'
    ]
    
    search_fields = [
        'incident_workflow__incident__code', 'user__username'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Transición', {
            'fields': ('incident_workflow', 'from_state', 'to_state', 'transition')
        }),
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Detalles', {
            'fields': ('description', 'metadata')
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )
