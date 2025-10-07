from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class ReportTemplate(models.Model):
    """Modelo para plantillas de reportes"""
    
    REPORT_TYPES = [
        ('incident_summary', 'Resumen de Incidentes'),
        ('incident_trends', 'Tendencias de Incidentes'),
        ('user_activity', 'Actividad de Usuarios'),
        ('document_usage', 'Uso de Documentos'),
        ('workflow_performance', 'Rendimiento de Workflows'),
        ('integration_status', 'Estado de Integraciones'),
        ('audit_summary', 'Resumen de Auditoría'),
        ('custom', 'Personalizado'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
        ('xml', 'XML'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('archived', 'Archivado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES, verbose_name='Tipo de Reporte')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf', verbose_name='Formato')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Estado')
    
    # Configuración del reporte
    template_config = models.JSONField(default=dict, verbose_name='Configuración de Plantilla')
    data_sources = models.JSONField(default=list, verbose_name='Fuentes de Datos')
    filters = models.JSONField(default=dict, verbose_name='Filtros')
    grouping = models.JSONField(default=dict, verbose_name='Agrupación')
    sorting = models.JSONField(default=dict, verbose_name='Ordenamiento')
    
    # Configuración de visualización
    charts_config = models.JSONField(default=list, verbose_name='Configuración de Gráficos')
    tables_config = models.JSONField(default=list, verbose_name='Configuración de Tablas')
    layout_config = models.JSONField(default=dict, verbose_name='Configuración de Diseño')
    
    # Configuración de programación
    is_scheduled = models.BooleanField(default=False, verbose_name='Programado')
    schedule_cron = models.CharField(max_length=100, blank=True, verbose_name='Expresión Cron')
    schedule_timezone = models.CharField(max_length=50, default='UTC', verbose_name='Zona Horaria')
    
    # Configuración de distribución
    email_recipients = models.JSONField(default=list, verbose_name='Destinatarios de Email')
    auto_generate = models.BooleanField(default=False, verbose_name='Generación Automática')
    retention_days = models.PositiveIntegerField(default=30, verbose_name='Días de Retención')
    
    # Metadatos
    is_public = models.BooleanField(default=False, verbose_name='Público')
    tags = models.JSONField(default=list, verbose_name='Etiquetas')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_templates', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Plantilla de Reporte'
        verbose_name_plural = 'Plantillas de Reportes'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportInstance(models.Model):
    """Modelo para instancias de reportes generados"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('generating', 'Generando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='instances', verbose_name='Plantilla')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Configuración específica de la instancia
    custom_filters = models.JSONField(default=dict, verbose_name='Filtros Personalizados')
    custom_config = models.JSONField(default=dict, verbose_name='Configuración Personalizada')
    
    # Datos del reporte
    report_data = models.JSONField(default=dict, verbose_name='Datos del Reporte')
    metadata = models.JSONField(default=dict, verbose_name='Metadatos')
    
    # Archivo generado
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del Archivo')
    file_size = models.PositiveIntegerField(default=0, verbose_name='Tamaño del Archivo')
    file_hash = models.CharField(max_length=64, blank=True, verbose_name='Hash del Archivo')
    
    # Fechas y tiempos
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Solicitado en')
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='Iniciado en')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Completado en')
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name='Expira en')
    
    # Usuarios
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_reports', verbose_name='Solicitado por')
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='generated_reports', verbose_name='Generado por')
    
    # Errores
    error_message = models.TextField(blank=True, verbose_name='Mensaje de Error')
    error_details = models.JSONField(default=dict, verbose_name='Detalles del Error')
    
    class Meta:
        verbose_name = 'Instancia de Reporte'
        verbose_name_plural = 'Instancias de Reportes'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.template.name} - {self.get_status_display()}"


class ReportSchedule(models.Model):
    """Modelo para programación de reportes"""
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('inactive', 'Inactivo'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='schedules', verbose_name='Plantilla')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    
    # Configuración de programación
    cron_expression = models.CharField(max_length=100, verbose_name='Expresión Cron')
    timezone = models.CharField(max_length=50, default='UTC', verbose_name='Zona Horaria')
    
    # Configuración de ejecución
    auto_execute = models.BooleanField(default=True, verbose_name='Ejecución Automática')
    max_retries = models.PositiveIntegerField(default=3, verbose_name='Máximo de Reintentos')
    retry_delay = models.PositiveIntegerField(default=300, verbose_name='Delay entre Reintentos (segundos)')
    
    # Configuración de distribución
    email_recipients = models.JSONField(default=list, verbose_name='Destinatarios de Email')
    webhook_url = models.URLField(blank=True, verbose_name='URL de Webhook')
    
    # Fechas
    last_executed = models.DateTimeField(blank=True, null=True, verbose_name='Última Ejecución')
    next_execution = models.DateTimeField(blank=True, null=True, verbose_name='Próxima Ejecución')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_schedules', verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Programación de Reporte'
        verbose_name_plural = 'Programaciones de Reportes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.template.name})"


class ReportDashboard(models.Model):
    """Modelo para dashboards de reportes"""
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Configuración del dashboard
    layout_config = models.JSONField(default=dict, verbose_name='Configuración de Diseño')
    widgets_config = models.JSONField(default=list, verbose_name='Configuración de Widgets')
    filters_config = models.JSONField(default=dict, verbose_name='Configuración de Filtros')
    
    # Configuración de actualización
    auto_refresh = models.BooleanField(default=True, verbose_name='Actualización Automática')
    refresh_interval = models.PositiveIntegerField(default=300, verbose_name='Intervalo de Actualización (segundos)')
    
    # Configuración de acceso
    is_public = models.BooleanField(default=False, verbose_name='Público')
    allowed_users = models.JSONField(default=list, verbose_name='Usuarios Permitidos')
    allowed_groups = models.JSONField(default=list, verbose_name='Grupos Permitidos')
    
    # Metadatos
    tags = models.JSONField(default=list, verbose_name='Etiquetas')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_dashboards', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Dashboard de Reportes'
        verbose_name_plural = 'Dashboards de Reportes'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportWidget(models.Model):
    """Modelo para widgets de reportes"""
    
    WIDGET_TYPES = [
        ('chart', 'Gráfico'),
        ('table', 'Tabla'),
        ('metric', 'Métrica'),
        ('gauge', 'Medidor'),
        ('progress', 'Progreso'),
        ('text', 'Texto'),
        ('image', 'Imagen'),
        ('iframe', 'Iframe'),
    ]
    
    CHART_TYPES = [
        ('line', 'Línea'),
        ('bar', 'Barras'),
        ('pie', 'Circular'),
        ('doughnut', 'Dona'),
        ('area', 'Área'),
        ('scatter', 'Dispersión'),
        ('radar', 'Radar'),
        ('polar', 'Polar'),
    ]
    
    dashboard = models.ForeignKey(ReportDashboard, on_delete=models.CASCADE, related_name='widgets', verbose_name='Dashboard')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name='Tipo de Widget')
    
    # Configuración del widget
    position = models.JSONField(default=dict, verbose_name='Posición')
    size = models.JSONField(default=dict, verbose_name='Tamaño')
    config = models.JSONField(default=dict, verbose_name='Configuración')
    
    # Configuración de datos
    data_source = models.JSONField(default=dict, verbose_name='Fuente de Datos')
    filters = models.JSONField(default=dict, verbose_name='Filtros')
    aggregation = models.JSONField(default=dict, verbose_name='Agregación')
    
    # Configuración de visualización
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True, verbose_name='Tipo de Gráfico')
    colors = models.JSONField(default=list, verbose_name='Colores')
    labels = models.JSONField(default=dict, verbose_name='Etiquetas')
    
    # Configuración de actualización
    auto_refresh = models.BooleanField(default=True, verbose_name='Actualización Automática')
    refresh_interval = models.PositiveIntegerField(default=300, verbose_name='Intervalo de Actualización (segundos)')
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Widget de Reporte'
        verbose_name_plural = 'Widgets de Reportes'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.dashboard.name})"


class ReportExport(models.Model):
    """Modelo para exportaciones de reportes"""
    
    EXPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('xml', 'XML'),
        ('html', 'HTML'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    instance = models.ForeignKey(ReportInstance, on_delete=models.CASCADE, related_name='exports', verbose_name='Instancia')
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMATS, verbose_name='Formato de Exportación')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Configuración de exportación
    export_config = models.JSONField(default=dict, verbose_name='Configuración de Exportación')
    
    # Archivo exportado
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del Archivo')
    file_size = models.PositiveIntegerField(default=0, verbose_name='Tamaño del Archivo')
    file_hash = models.CharField(max_length=64, blank=True, verbose_name='Hash del Archivo')
    
    # Fechas
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name='Solicitado en')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Completado en')
    
    # Usuarios
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_exports', verbose_name='Solicitado por')
    
    # Errores
    error_message = models.TextField(blank=True, verbose_name='Mensaje de Error')
    error_details = models.JSONField(default=dict, verbose_name='Detalles del Error')
    
    class Meta:
        verbose_name = 'Exportación de Reporte'
        verbose_name_plural = 'Exportaciones de Reportes'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.instance.template.name} - {self.get_export_format_display()}"
