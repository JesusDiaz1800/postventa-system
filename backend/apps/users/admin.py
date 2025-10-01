from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_active', 'last_login', 'created_at'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser',
        'created_at', 'last_login'
    ]
    
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    ordering = ['-created_at']
    
    # Remove filter_horizontal for groups and user_permissions
    filter_horizontal = []
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'department')
        }),
        ('Permisos', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
