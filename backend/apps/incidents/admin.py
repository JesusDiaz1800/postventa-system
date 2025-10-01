from django.contrib import admin
from .models import Incident, IncidentImage, LabReport, IncidentTimeline


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """Admin interface for Incident model"""
    
    list_display = [
        'code', 'cliente', 'provider', 'sku', 'lote', 'estado',
        'prioridad', 'assigned_to', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'estado', 'prioridad', 'categoria', 'responsable',
        'created_at', 'fecha_deteccion'
    ]
    
    search_fields = [
        'code', 'cliente', 'provider', 'obra', 'sku', 'lote',
        'descripcion', 'factura_num', 'pedido_num'
    ]
    
    readonly_fields = ['code', 'created_at', 'updated_at', 'closed_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'created_by', 'provider', 'obra')
        }),
        ('Cliente', {
            'fields': ('cliente', 'cliente_rut', 'direccion_cliente')
        }),
        ('Producto', {
            'fields': ('sku', 'lote', 'factura_num', 'pedido_num', 'categoria', 'subcategoria')
        }),
        ('Detalles del Incidente', {
            'fields': ('fecha_reporte', 'fecha_deteccion', 'hora_deteccion', 'descripcion', 'acciones_inmediatas')
        }),
        ('Clasificación', {
            'fields': ('prioridad', 'estado', 'responsable', 'assigned_to')
        }),
        ('Seguimiento', {
            'fields': ('closed_by', 'closed_at')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    ordering = ['-created_at']


@admin.register(IncidentImage)
class IncidentImageAdmin(admin.ModelAdmin):
    """Admin interface for IncidentImage model"""
    
    list_display = [
        'incident', 'filename', 'file_size', 'ai_provider_used',
        'ai_confidence', 'uploaded_by', 'created_at'
    ]
    
    list_filter = [
        'ai_provider_used', 'mime_type', 'created_at'
    ]
    
    search_fields = [
        'incident__code', 'filename', 'caption_ai'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Archivo', {
            'fields': ('incident', 'filename', 'path', 'file_size', 'mime_type')
        }),
        ('Datos EXIF', {
            'fields': ('exif_json',)
        }),
        ('Análisis de IA', {
            'fields': ('caption_ai', 'analysis_json', 'ai_provider_used', 'ai_confidence')
        }),
        ('Metadatos', {
            'fields': ('uploaded_by', 'created_at')
        }),
    )


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    """Admin interface for LabReport model"""
    
    list_display = [
        'incident', 'expert_name', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'created_at'
    ]
    
    search_fields = [
        'incident__code', 'expert_name', 'sample_description'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Incidencia', {
            'fields': ('incident',)
        }),
        ('Muestra', {
            'fields': ('sample_description', 'tests_performed')
        }),
        ('Resultados', {
            'fields': ('observations', 'conclusions')
        }),
        ('Experto', {
            'fields': ('expert_name', 'expert_signature_path')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at')
        }),
    )


@admin.register(IncidentTimeline)
class IncidentTimelineAdmin(admin.ModelAdmin):
    """Admin interface for IncidentTimeline model"""
    
    list_display = [
        'incident', 'action', 'user', 'created_at'
    ]
    
    list_filter = [
        'action', 'created_at'
    ]
    
    search_fields = [
        'incident__code', 'description', 'user__username'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Incidencia', {
            'fields': ('incident',)
        }),
        ('Acción', {
            'fields': ('action', 'description')
        }),
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Metadatos', {
            'fields': ('metadata', 'created_at')
        }),
    )
