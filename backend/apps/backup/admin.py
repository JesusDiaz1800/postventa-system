from django.contrib import admin
from .models import (
    BackupJob, BackupInstance, RestoreJob, BackupSchedule, 
    BackupStorage, BackupLog, BackupPolicy
)


@admin.register(BackupJob)
class BackupJobAdmin(admin.ModelAdmin):
    """Admin interface for BackupJob model"""
    
    list_display = [
        'name', 'backup_type', 'status', 'is_scheduled', 'created_by', 'created_at'
    ]
    list_filter = [
        'backup_type', 'status', 'is_scheduled', 'created_at'
    ]
    search_fields = [
        'name', 'description', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'backup_type')
        }),
        ('Configuración', {
            'fields': ('status', 'is_scheduled', 'schedule_config', 'options')
        }),
        ('Almacenamiento', {
            'fields': ('storage',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(BackupInstance)
class BackupInstanceAdmin(admin.ModelAdmin):
    """Admin interface for BackupInstance model"""
    
    list_display = [
        'id', 'job', 'status', 'started_by', 'started_at', 'duration'
    ]
    list_filter = [
        'status', 'job__backup_type', 'started_at'
    ]
    search_fields = [
        'job__name', 'started_by__username'
    ]
    readonly_fields = ['started_at', 'completed_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Instancia', {
            'fields': ('job', 'status', 'backup_path', 'backup_size')
        }),
        ('Usuarios', {
            'fields': ('started_by', 'completed_by')
        }),
        ('Fechas', {
            'fields': ('started_at', 'completed_at', 'duration')
        }),
        ('Opciones y Errores', {
            'fields': ('options', 'error_message')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(RestoreJob)
class RestoreJobAdmin(admin.ModelAdmin):
    """Admin interface for RestoreJob model"""
    
    list_display = [
        'id', 'backup_instance', 'status', 'created_by', 'created_at'
    ]
    list_filter = [
        'status', 'created_at'
    ]
    search_fields = [
        'backup_instance__job__name', 'created_by__username'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Restauración', {
            'fields': ('backup_instance', 'status', 'restore_path')
        }),
        ('Usuarios', {
            'fields': ('created_by', 'started_by', 'completed_by')
        }),
        ('Fechas', {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration')
        }),
        ('Opciones y Errores', {
            'fields': ('options', 'error_message')
        }),
        ('Metadatos', {
            'fields': ('updated_at',)
        }),
    )


@admin.register(BackupSchedule)
class BackupScheduleAdmin(admin.ModelAdmin):
    """Admin interface for BackupSchedule model"""
    
    list_display = [
        'name', 'job', 'schedule_type', 'status', 'last_execution', 'created_by'
    ]
    list_filter = [
        'schedule_type', 'status', 'last_execution'
    ]
    search_fields = [
        'name', 'description', 'job__name'
    ]
    readonly_fields = ['last_execution', 'created_at', 'updated_at']
    fieldsets = (
        ('Programación', {
            'fields': ('name', 'description', 'job', 'schedule_type')
        }),
        ('Configuración', {
            'fields': ('schedule_config', 'status')
        }),
        ('Ejecución', {
            'fields': ('last_execution', 'next_execution')
        }),
        ('Opciones', {
            'fields': ('options',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(BackupStorage)
class BackupStorageAdmin(admin.ModelAdmin):
    """Admin interface for BackupStorage model"""
    
    list_display = [
        'name', 'storage_type', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = [
        'storage_type', 'is_active', 'created_at'
    ]
    search_fields = [
        'name', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Almacenamiento', {
            'fields': ('name', 'description', 'storage_type')
        }),
        ('Configuración', {
            'fields': ('config', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    """Admin interface for BackupLog model"""
    
    list_display = [
        'id', 'job', 'instance', 'level', 'step', 'timestamp'
    ]
    list_filter = [
        'level', 'step', 'timestamp'
    ]
    search_fields = [
        'job__name', 'message'
    ]
    readonly_fields = ['timestamp']
    fieldsets = (
        ('Log', {
            'fields': ('job', 'instance', 'level', 'step', 'message')
        }),
        ('Metadatos', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(BackupPolicy)
class BackupPolicyAdmin(admin.ModelAdmin):
    """Admin interface for BackupPolicy model"""
    
    list_display = [
        'name', 'policy_type', 'is_active', 'priority', 'created_by'
    ]
    list_filter = [
        'policy_type', 'is_active', 'priority'
    ]
    search_fields = [
        'name', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Política', {
            'fields': ('name', 'description', 'policy_type')
        }),
        ('Configuración', {
            'fields': ('backup_types', 'config', 'is_active', 'priority')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
