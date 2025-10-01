from django.contrib import admin
from .models import AIProvider, AIAnalysis, AIUsageLog


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    """Admin interface for AI Provider model"""
    
    list_display = [
        'name', 'enabled', 'priority', 'tokens_used_today',
        'daily_quota_tokens', 'calls_made_today', 'daily_quota_calls',
        'last_reset_date'
    ]
    
    list_filter = [
        'enabled', 'allow_external_uploads', 'created_at'
    ]
    
    search_fields = ['name']
    
    readonly_fields = [
        'tokens_used_today', 'calls_made_today', 'last_reset_date',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Configuración Básica', {
            'fields': ('name', 'enabled', 'priority')
        }),
        ('API Key', {
            'fields': ('api_key_encrypted',),
            'description': 'API Key encriptada para el proveedor'
        }),
        ('Gestión de Cuotas', {
            'fields': (
                'daily_quota_tokens', 'daily_quota_calls', 'quota_reset_time',
                'tokens_used_today', 'calls_made_today', 'last_reset_date'
            )
        }),
        ('Configuración', {
            'fields': ('allow_external_uploads',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['reset_quotas']
    
    def reset_quotas(self, request, queryset):
        """Reset quotas for selected providers"""
        for provider in queryset:
            provider.reset_quota()
        self.message_user(request, f"Cuotas reseteadas para {queryset.count()} proveedores")
    
    reset_quotas.short_description = "Resetear cuotas seleccionadas"


@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    """Admin interface for AI Analysis model"""
    
    list_display = [
        'analysis_type', 'provider_used', 'confidence_score',
        'tokens_used', 'processing_time', 'created_at'
    ]
    
    list_filter = [
        'analysis_type', 'provider_used', 'created_at'
    ]
    
    search_fields = [
        'analysis_type', 'provider_used__name'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Análisis', {
            'fields': ('analysis_type', 'provider_used')
        }),
        ('Datos', {
            'fields': ('input_data', 'output_data')
        }),
        ('Métricas', {
            'fields': ('confidence_score', 'tokens_used', 'processing_time')
        }),
        ('Error', {
            'fields': ('error_message',)
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    """Admin interface for AI Usage Log model"""
    
    list_display = [
        'provider', 'analysis_type', 'tokens_used', 'cost_estimate',
        'success', 'created_at'
    ]
    
    list_filter = [
        'provider', 'analysis_type', 'success', 'created_at'
    ]
    
    search_fields = [
        'provider__name', 'analysis_type'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Uso', {
            'fields': ('provider', 'analysis_type', 'tokens_used', 'cost_estimate')
        }),
        ('Resultado', {
            'fields': ('success', 'error_message')
        }),
        ('Fechas', {
            'fields': ('created_at',)
        }),
    )
