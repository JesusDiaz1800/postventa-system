from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    
    list_display = [
        'title', 'user', 'notification_type', 'is_read', 'is_important', 'created_at'
    ]
    
    list_filter = [
        'notification_type', 'is_read', 'is_important', 'created_at'
    ]
    
    search_fields = [
        'title', 'message', 'user__username'
    ]
    
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Notificación', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Estado', {
            'fields': ('is_read', 'is_important', 'read_at')
        }),
        ('Objetos Relacionados', {
            'fields': ('related_incident', 'related_document', 'related_user')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'created_at')
        }),
    )



@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model"""
    
    list_display = [
        'user', 'email_enabled', 'push_enabled', 'web_enabled'
    ]
    
    list_filter = [
        'email_enabled', 'push_enabled', 'web_enabled'
    ]
    
    search_fields = [
        'user__username'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Canales Activos', {
            'fields': ('email_enabled', 'push_enabled', 'web_enabled')
        }),
        ('Preferencias de Tipo de Notificación', {
            'fields': (
                'incident_created', 'incident_updated', 'incident_escalated', 'incident_closed',
                'document_uploaded', 'document_approved', 'document_rejected',
                'workflow_step_completed', 'workflow_approval_required',
                'system_alert', 'user_assigned', 'deadline_approaching', 'deadline_exceeded'
            )
        }),
        ('Filtros y Horarios', {
            'fields': ('priority_threshold', 'notification_start_time', 'notification_end_time', 'quiet_hours', 'weekend_notifications')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
