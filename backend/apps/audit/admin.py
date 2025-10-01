from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for Audit Log model"""
    
    list_display = [
        'user', 'action', 'resource_type', 'resource_id', 'details',
        'ip_address', 'created_at'
    ]
    
    list_filter = [
        'action', 'resource_type', 'created_at'
    ]
    
    search_fields = [
        'user__username', 'details', 'resource_id', 'ip_address'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Acción', {
            'fields': ('user', 'action', 'details')
        }),
        ('Recurso', {
            'fields': ('resource_type', 'resource_id', 'content_type', 'object_id')
        }),
        ('Detalles', {
            'fields': ('metadata',)
        }),
        ('Información de Red', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )
    
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False  # Audit logs should not be manually created
    
    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should not be modified
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can delete audit logs
