from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model - versión simplificada"""
    
    list_display = [
        'action', 'user_display', 'description', 'timestamp', 'ip_address'
    ]
    
    list_filter = [
        'action', 'timestamp'
    ]
    
    search_fields = [
        'description', 'user__username', 'ip_address'    ]
    
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Acción', {
            'fields': ('action', 'description')
        }),
        ('Usuario y Sesión', {
            'fields': ('user', 'ip_address', 'timestamp')
        }),
        ('Detalles', {
            'fields': ('details',)
        }),
    )
    
    def user_display(self, obj):
        """Mostrar información del usuario de forma amigable"""
        if obj.user:
            return f"{obj.user.username} ({obj.user.get_full_name() or obj.user.email})"
        return 'Sistema'
    user_display.short_description = 'Usuario'