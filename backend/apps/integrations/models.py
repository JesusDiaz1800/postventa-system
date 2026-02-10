from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from apps.users.models import User
import json


class ExternalSystem(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    # ADVERTENCIA: Revisa los tipos de datos y relaciones para compatibilidad total con SQL Server. Evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para sistemas externos"""
    
    SYSTEM_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('erp', 'ERP'),
        ('crm', 'CRM'),
        ('api', 'API'),
        ('webhook', 'Webhook'),
        ('database', 'Base de Datos'),
        ('file', 'Archivo'),
        ('ftp', 'FTP'),
        ('sftp', 'SFTP'),
        ('rest', 'REST API'),
        ('soap', 'SOAP'),
        ('graphql', 'GraphQL'),
        ('mqtt', 'MQTT'),
        ('websocket', 'WebSocket'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('error', 'Error'),
        ('maintenance', 'Mantenimiento'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    system_type = models.CharField(max_length=20, choices=SYSTEM_TYPES, verbose_name='Tipo de Sistema')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    
    # Configuración de conexión
    endpoint_url = models.URLField(blank=True, verbose_name='URL del Endpoint')
    base_url = models.URLField(blank=True, verbose_name='URL Base')
    api_key = models.CharField(max_length=255, blank=True, verbose_name='API Key')
    username = models.CharField(max_length=100, blank=True, verbose_name='Usuario')
    password = models.CharField(max_length=255, blank=True, verbose_name='Contraseña')
    token = models.TextField(blank=True, verbose_name='Token')
    
    # Configuración adicional
    timeout = models.PositiveIntegerField(default=30, verbose_name='Timeout (segundos)')
    retry_attempts = models.PositiveIntegerField(default=3, verbose_name='Intentos de Reintento')
    retry_delay = models.PositiveIntegerField(default=5, verbose_name='Delay entre Reintentos (segundos)')
    
    # Headers y parámetros
    headers = models.JSONField(default=dict, blank=True, verbose_name='Headers')
    default_params = models.JSONField(default=dict, blank=True, verbose_name='Parámetros por Defecto')
    
    # Configuración de autenticación
    auth_type = models.CharField(max_length=20, blank=True, verbose_name='Tipo de Autenticación')
    auth_config = models.JSONField(default=dict, blank=True, verbose_name='Configuración de Autenticación')
    
    # Configuración de SSL/TLS
    verify_ssl = models.BooleanField(default=True, verbose_name='Verificar SSL')
    ssl_cert_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del Certificado SSL')
    ssl_key_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta de la Clave SSL')
    
    # Configuración de proxy
    use_proxy = models.BooleanField(default=False, verbose_name='Usar Proxy')
    proxy_url = models.URLField(blank=True, verbose_name='URL del Proxy')
    proxy_username = models.CharField(max_length=100, blank=True, verbose_name='Usuario del Proxy')
    proxy_password = models.CharField(max_length=255, blank=True, verbose_name='Contraseña del Proxy')
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_external_systems', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        app_label = 'integrations'
        verbose_name = 'Sistema Externo'
        verbose_name_plural = 'Sistemas Externos'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class IntegrationTemplate(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para plantillas de integración"""
    
    TEMPLATE_TYPES = [
        ('incident_sync', 'Sincronización de Incidentes'),
        ('document_sync', 'Sincronización de Documentos'),
        ('user_sync', 'Sincronización de Usuarios'),
        ('notification', 'Notificación'),
        ('report', 'Reporte'),
        ('backup', 'Respaldo'),
        ('import', 'Importación'),
        ('export', 'Exportación'),
        ('webhook', 'Webhook'),
        ('api_call', 'Llamada API'),
        ('data_transform', 'Transformación de Datos'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES, verbose_name='Tipo de Plantilla')
    
    # Configuración de la plantilla
    source_system = models.ForeignKey(ExternalSystem, on_delete=models.CASCADE, related_name='source_templates', verbose_name='Sistema Origen')
    target_system = models.ForeignKey(ExternalSystem, on_delete=models.CASCADE, related_name='target_templates', verbose_name='Sistema Destino')
    
    # Mapeo de campos
    field_mapping = models.JSONField(default=dict, verbose_name='Mapeo de Campos')
    data_transformation = models.JSONField(default=dict, blank=True, verbose_name='Transformación de Datos')
    
    # Configuración de sincronización
    sync_frequency = models.CharField(max_length=20, blank=True, verbose_name='Frecuencia de Sincronización')
    sync_direction = models.CharField(max_length=20, choices=[('one_way', 'Unidireccional'), ('two_way', 'Bidireccional')], default='one_way', verbose_name='Dirección de Sincronización')
    conflict_resolution = models.CharField(max_length=20, choices=[('source_wins', 'Origen Gana'), ('target_wins', 'Destino Gana'), ('manual', 'Manual')], default='source_wins', verbose_name='Resolución de Conflictos')
    
    # Filtros y condiciones
    filter_conditions = models.JSONField(default=dict, blank=True, verbose_name='Condiciones de Filtro')
    sync_conditions = models.JSONField(default=dict, blank=True, verbose_name='Condiciones de Sincronización')
    
    # Configuración de errores
    error_handling = models.JSONField(default=dict, blank=True, verbose_name='Manejo de Errores')
    retry_config = models.JSONField(default=dict, blank=True, verbose_name='Configuración de Reintento')
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_integration_templates', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        app_label = 'integrations'
        verbose_name = 'Plantilla de Integración'
        verbose_name_plural = 'Plantillas de Integración'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class IntegrationInstance(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para instancias de integración"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutándose'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
        ('paused', 'Pausado'),
    ]
    
    template = models.ForeignKey(IntegrationTemplate, on_delete=models.CASCADE, related_name='instances', verbose_name='Plantilla')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Objetos relacionados
    related_incident = models.ForeignKey('incidents.Incident', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Incidencia Relacionada')
    related_document = models.ForeignKey('documents.Document', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Documento Relacionado')
    related_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Usuario Relacionado')
    
    # Datos de entrada y salida
    input_data = models.JSONField(default=dict, blank=True, verbose_name='Datos de Entrada')
    output_data = models.JSONField(default=dict, blank=True, verbose_name='Datos de Salida')
    error_data = models.JSONField(default=dict, blank=True, verbose_name='Datos de Error')
    
    # Configuración específica de la instancia
    custom_config = models.JSONField(default=dict, blank=True, verbose_name='Configuración Personalizada')
    
    # Fechas y tiempos
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='Iniciado en')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Completado en')
    scheduled_at = models.DateTimeField(blank=True, null=True, verbose_name='Programado para')
    
    # Usuarios
    started_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='started_integrations', verbose_name='Iniciado por')
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='completed_integrations', verbose_name='Completado por')
    
    # Metadatos
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadatos')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        app_label = 'integrations'
        verbose_name = 'Instancia de Integración'
        verbose_name_plural = 'Instancias de Integración'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.get_status_display()}"


class IntegrationLog(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para logs de integración"""
    
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Crítico'),
    ]
    
    instance = models.ForeignKey(IntegrationInstance, on_delete=models.CASCADE, related_name='logs', verbose_name='Instancia')
    level = models.CharField(max_length=20, choices=LOG_LEVELS, verbose_name='Nivel')
    message = models.TextField(verbose_name='Mensaje')
    details = models.JSONField(default=dict, blank=True, verbose_name='Detalles')
    
    # Contexto
    step = models.CharField(max_length=100, blank=True, verbose_name='Paso')
    duration = models.DurationField(blank=True, null=True, verbose_name='Duración')
    
    # Metadatos
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    
    class Meta:
        app_label = 'integrations'
        verbose_name = 'Log de Integración'
        verbose_name_plural = 'Logs de Integración'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.instance.template.name} - {self.get_level_display()} - {self.timestamp}"


class WebhookEndpoint(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para endpoints de webhook"""
    
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    url_path = models.CharField(max_length=200, unique=True, verbose_name='Ruta URL')
    http_method = models.CharField(max_length=10, choices=HTTP_METHODS, default='POST', verbose_name='Método HTTP')
    
    # Configuración de autenticación
    requires_auth = models.BooleanField(default=True, verbose_name='Requiere Autenticación')
    auth_token = models.CharField(max_length=255, blank=True, verbose_name='Token de Autenticación')
    
    # Configuración de validación
    validate_signature = models.BooleanField(default=False, verbose_name='Validar Firma')
    signature_header = models.CharField(max_length=100, blank=True, verbose_name='Header de Firma')
    signature_secret = models.CharField(max_length=255, blank=True, verbose_name='Secreto de Firma')
    
    # Configuración de procesamiento
    auto_process = models.BooleanField(default=True, verbose_name='Procesamiento Automático')
    processing_script = models.TextField(blank=True, verbose_name='Script de Procesamiento')
    
    # Filtros y condiciones
    filter_conditions = models.JSONField(default=dict, blank=True, verbose_name='Condiciones de Filtro')
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_webhook_endpoints', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        app_label = 'integrations'
        verbose_name = 'Endpoint de Webhook'
        verbose_name_plural = 'Endpoints de Webhook'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.http_method} {self.url_path})"


class WebhookLog(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para logs de webhook"""
    
    STATUS_CHOICES = [
        ('received', 'Recibido'),
        ('processing', 'Procesando'),
        ('processed', 'Procesado'),
        ('failed', 'Fallido'),
        ('ignored', 'Ignorado'),
    ]
    
    endpoint = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='logs', verbose_name='Endpoint')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Estado')
    
    # Datos de la petición
    request_method = models.CharField(max_length=10, verbose_name='Método de Petición')
    request_headers = models.JSONField(default=dict, verbose_name='Headers de Petición')
    request_body = models.TextField(blank=True, verbose_name='Cuerpo de Petición')
    request_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP de Petición')
    
    # Datos de la respuesta
    response_status = models.PositiveIntegerField(blank=True, null=True, verbose_name='Estado de Respuesta')
    response_headers = models.JSONField(default=dict, verbose_name='Headers de Respuesta')
    response_body = models.TextField(blank=True, verbose_name='Cuerpo de Respuesta')
    
    # Procesamiento
    processing_time = models.DurationField(blank=True, null=True, verbose_name='Tiempo de Procesamiento')
    error_message = models.TextField(blank=True, verbose_name='Mensaje de Error')
    error_details = models.JSONField(default=dict, blank=True, verbose_name='Detalles del Error')
    
    # Metadatos
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    
    class Meta:
        app_label = 'integrations'
        verbose_name = 'Log de Webhook'
        verbose_name_plural = 'Logs de Webhook'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.endpoint.name} - {self.get_status_display()} - {self.timestamp}"

