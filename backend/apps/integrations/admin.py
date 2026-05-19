from django.contrib import admin
from .models import (
    ExternalSystem, IntegrationTemplate, IntegrationInstance, 
    IntegrationLog, WebhookEndpoint, WebhookLog
)


@admin.register(ExternalSystem)
class ExternalSystemAdmin(admin.ModelAdmin):
    """Admin interface for ExternalSystem model"""
    
    list_display = [
        'name', 'system_type', 'status', 'is_active', 'created_by', 'created_at'
    ]
    
    list_filter = [
        'system_type', 'status', 'is_active', 'created_at'
    ]
    
    search_fields = [
        'name', 'description', 'endpoint_url', 'base_url'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'system_type', 'status')
        }),
        ('Configuración de Conexión', {
            'fields': ('endpoint_url', 'base_url', 'api_key', 'username', 'password', 'token')
        }),
        ('Configuración de Timeout y Reintentos', {
            'fields': ('timeout', 'retry_attempts', 'retry_delay')
        }),
        ('Headers y Parámetros', {
            'fields': ('headers', 'default_params')
        }),
        ('Autenticación', {
            'fields': ('auth_type', 'auth_config')
        }),
        ('SSL/TLS', {
            'fields': ('verify_ssl', 'ssl_cert_path', 'ssl_key_path')
        }),
        ('Proxy', {
            'fields': ('use_proxy', 'proxy_url', 'proxy_username', 'proxy_password')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(IntegrationTemplate)
class IntegrationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for IntegrationTemplate model"""
    
    list_display = [
        'name', 'template_type', 'source_system', 'target_system', 'is_active', 'created_by'
    ]
    
    list_filter = [
        'template_type', 'sync_direction', 'is_active', 'created_at'
    ]
    
    search_fields = [
        'name', 'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'template_type')
        }),
        ('Sistemas', {
            'fields': ('source_system', 'target_system')
        }),
        ('Mapeo y Transformación', {
            'fields': ('field_mapping', 'data_transformation')
        }),
        ('Configuración de Sincronización', {
            'fields': ('sync_frequency', 'sync_direction', 'conflict_resolution')
        }),
        ('Filtros y Condiciones', {
            'fields': ('filter_conditions', 'sync_conditions')
        }),
        ('Manejo de Errores', {
            'fields': ('error_handling', 'retry_config')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(IntegrationInstance)
class IntegrationInstanceAdmin(admin.ModelAdmin):
    """Admin interface for IntegrationInstance model"""
    
    list_display = [
        'template', 'status', 'started_by', 'started_at', 'completed_at'
    ]
    
    list_filter = [
        'status', 'template', 'started_at'
    ]
    
    search_fields = [
        'template__name', 'started_by__username'
    ]
    
    readonly_fields = ['started_at', 'completed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Instancia', {
            'fields': ('template', 'status')
        }),
        ('Objetos Relacionados', {
            'fields': ('related_incident', 'related_document', 'related_user')
        }),
        ('Datos', {
            'fields': ('input_data', 'output_data', 'error_data')
        }),
        ('Configuración', {
            'fields': ('custom_config',)
        }),
        ('Fechas', {
            'fields': ('started_at', 'completed_at', 'scheduled_at')
        }),
        ('Usuarios', {
            'fields': ('started_by', 'completed_by')
        }),
        ('Metadatos', {
            'fields': ('metadata', 'created_at', 'updated_at')
        }),
    )


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    """Admin interface for IntegrationLog model"""
    
    list_display = [
        'instance', 'level', 'step', 'timestamp'
    ]
    
    list_filter = [
        'level', 'step', 'timestamp'
    ]
    
    search_fields = [
        'message', 'instance__template__name'
    ]
    
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Log', {
            'fields': ('instance', 'level', 'message', 'details')
        }),
        ('Contexto', {
            'fields': ('step', 'duration')
        }),
        ('Metadatos', {
            'fields': ('timestamp',)
        }),
    )


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    """Admin interface for WebhookEndpoint model"""
    
    list_display = [
        'name', 'url_path', 'http_method', 'requires_auth', 'is_active', 'created_by'
    ]
    
    list_filter = [
        'http_method', 'requires_auth', 'validate_signature', 'auto_process', 'is_active'
    ]
    
    search_fields = [
        'name', 'description', 'url_path'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'url_path', 'http_method')
        }),
        ('Autenticación', {
            'fields': ('requires_auth', 'auth_token')
        }),
        ('Validación de Firma', {
            'fields': ('validate_signature', 'signature_header', 'signature_secret')
        }),
        ('Procesamiento', {
            'fields': ('auto_process', 'processing_script')
        }),
        ('Filtros', {
            'fields': ('filter_conditions',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    """Admin interface for WebhookLog model"""
    
    list_display = [
        'endpoint', 'status', 'request_method', 'request_ip', 'timestamp'
    ]
    
    list_filter = [
        'status', 'request_method', 'timestamp'
    ]
    
    search_fields = [
        'endpoint__name', 'request_ip'
    ]
    
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Webhook', {
            'fields': ('endpoint', 'status')
        }),
        ('Petición', {
            'fields': ('request_method', 'request_headers', 'request_body', 'request_ip')
        }),
        ('Respuesta', {
            'fields': ('response_status', 'response_headers', 'response_body')
        }),
        ('Procesamiento', {
            'fields': ('processing_time', 'error_message', 'error_details')
        }),
        ('Metadatos', {
            'fields': ('timestamp',)
        }),
    )
