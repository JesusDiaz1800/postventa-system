from django.contrib import admin
from .models import Notification, NotificationPreferences

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'is_important', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_important', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contenido', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Estado', {
            'fields': ('is_read', 'is_important')
        }),
        ('Detalles técnicos', {
            'fields': ('related_url', 'metadata', 'created_at', 'updated_at')
        }),
    )

@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['updated_at']
