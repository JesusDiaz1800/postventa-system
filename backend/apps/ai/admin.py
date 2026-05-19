from django.contrib import admin
from .models import AIAnalysis, AIProvider

@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'priority', 'requests_per_minute', 'cost_per_token']
    list_filter = ['is_active', 'priority']
    search_fields = ['name']
    ordering = ['priority', 'name']

@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'analysis_type', 'status', 'confidence_score', 'created_at']
    list_filter = ['analysis_type', 'status', 'ai_provider', 'created_at']
    search_fields = ['user__username', 'input_description', 'processed_analysis']
    readonly_fields = ['created_at', 'updated_at', 'processing_time', 'tokens_used', 'cost']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'analysis_type', 'status')
        }),
        ('Datos de Entrada', {
            'fields': ('input_file_path', 'input_description')
        }),
        ('Configuración IA', {
            'fields': ('ai_provider', 'model_used')
        }),
        ('Resultados', {
            'fields': ('processed_analysis', 'confidence_score', 'generated_report', 'report_file_path')
        }),
        ('Métricas', {
            'fields': ('processing_time', 'tokens_used', 'cost'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
