from django.contrib import admin
from .models import DocumentTemplate, Document, DocumentVersion, DocumentConversion


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    """Admin interface for Document Template model"""
    
    list_display = [
        'name', 'template_type', 'is_active', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'template_type', 'is_active', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'template_type', 'description')
        }),
        ('Archivo', {
            'fields': ('docx_template_path',)
        }),
        ('Configuración', {
            'fields': ('placeholders_json', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model"""
    
    list_display = [
        'title', 'document_type', 'version', 'is_final', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'document_type', 'is_final', 'created_at'
    ]
    
    search_fields = [
        'title', 'notes', 'incident__code'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'document_type', 'version', 'is_final')
        }),
        ('Relaciones', {
            'fields': ('incident', 'template')
        }),
        ('Archivos', {
            'fields': ('docx_path', 'pdf_path')
        }),
        ('Contenido', {
            'fields': ('content_html', 'placeholders_data', 'notes')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    """Admin interface for Document Version model"""
    
    list_display = [
        'document', 'version_number', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'created_at'
    ]
    
    search_fields = [
        'document__title', 'change_description'
    ]
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Versión', {
            'fields': ('document', 'version')
        }),
        ('Archivos', {
            'fields': ('docx_path', 'pdf_path')
        }),
        ('Contenido', {
            'fields': ('content_html', 'change_description')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at')
        }),
    )


@admin.register(DocumentConversion)
class DocumentConversionAdmin(admin.ModelAdmin):
    """Admin interface for Document Conversion model"""
    
    list_display = [
        'document', 'status', 'source_format', 'target_format', 'created_at', 'completed_at'
    ]
    
    list_filter = [
        'status', 'created_at'
    ]
    
    search_fields = [
        'document__title', 'error_message'
    ]
    
    readonly_fields = ['created_at', 'completed_at']
    
    fieldsets = (
        ('Conversión', {
            'fields': ('document', 'status')
        }),
        ('Archivos', {
            'fields': ('source_path', 'target_path')
        }),
        ('Procesamiento', {
            'fields': ('processing_time', 'error_message')
        }),
        ('Fechas', {
            'fields': ('created_at', 'completed_at')
        }),
    )
