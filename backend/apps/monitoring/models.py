from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class MonitoringRule(models.Model):
    """Reglas de monitoreo para diferentes métricas"""
    
    METRIC_TYPES = [
        ('system', 'Sistema'),
        ('database', 'Base de Datos'),
        ('api', 'API'),
        ('user', 'Usuario'),
        ('incident', 'Incidente'),
        ('document', 'Documento'),
        ('backup', 'Backup'),
        ('custom', 'Personalizado'),
    ]
    
    COMPARISON_OPERATORS = [
        ('gt', 'Mayor que'),
        ('gte', 'Mayor o igual que'),
        ('lt', 'Menor que'),
        ('lte', 'Menor o igual que'),
        ('eq', 'Igual a'),
        ('ne', 'Diferente de'),
        ('contains', 'Contiene'),
        ('regex', 'Expresión regular'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, verbose_name='Tipo de Métrica')
    metric_name = models.CharField(max_length=100, verbose_name='Nombre de Métrica')
    comparison_operator = models.CharField(max_length=20, choices=COMPARISON_OPERATORS, verbose_name='Operador de Comparación')
    threshold_value = models.FloatField(verbose_name='Valor Umbral')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name='Severidad')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    check_interval = models.IntegerField(default=300, verbose_name='Intervalo de Verificación (segundos)')
    notification_channels = models.JSONField(default=list, verbose_name='Canales de Notificación')
    tags = models.JSONField(default=list, verbose_name='Etiquetas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Regla de Monitoreo'
        verbose_name_plural = 'Reglas de Monitoreo'
        ordering = ['-severity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.metric_name})"


class Alert(models.Model):
    """Alertas generadas por las reglas de monitoreo"""
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('acknowledged', 'Reconocida'),
        ('resolved', 'Resuelta'),
        ('suppressed', 'Suprimida'),
    ]
    
    rule = models.ForeignKey(MonitoringRule, on_delete=models.CASCADE, verbose_name='Regla')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    severity = models.CharField(max_length=20, choices=MonitoringRule.SEVERITY_LEVELS, verbose_name='Severidad')
    title = models.CharField(max_length=200, verbose_name='Título')
    message = models.TextField(verbose_name='Mensaje')
    metric_value = models.FloatField(verbose_name='Valor de Métrica')
    threshold_value = models.FloatField(verbose_name='Valor Umbral')
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name='Activada')
    acknowledged_at = models.DateTimeField(blank=True, null=True, verbose_name='Reconocida')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='Resuelta')
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='acknowledged_alerts', verbose_name='Reconocida por')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='resolved_alerts', verbose_name='Resuelta por')
    metadata = models.JSONField(default=dict, verbose_name='Metadatos')
    tags = models.JSONField(default=list, verbose_name='Etiquetas')
    
    class Meta:
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"{self.title} - {self.severity}"
    
    @property
    def duration(self):
        """Duración de la alerta"""
        if self.resolved_at:
            return self.resolved_at - self.triggered_at
        return timezone.now() - self.triggered_at
    
    @property
    def is_acknowledged(self):
        return self.status == 'acknowledged'
    
    @property
    def is_resolved(self):
        return self.status == 'resolved'


class MetricValue(models.Model):
    """Valores de métricas recopilados"""
    
    rule = models.ForeignKey(MonitoringRule, on_delete=models.CASCADE, verbose_name='Regla')
    value = models.FloatField(verbose_name='Valor')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    metadata = models.JSONField(default=dict, verbose_name='Metadatos')
    
    class Meta:
        verbose_name = 'Valor de Métrica'
        verbose_name_plural = 'Valores de Métricas'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['rule', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.rule.metric_name}: {self.value}"


class HealthCheck(models.Model):
    """Verificaciones de salud del sistema"""
    
    CHECK_TYPES = [
        ('database', 'Base de Datos'),
        ('redis', 'Redis'),
        ('storage', 'Almacenamiento'),
        ('api', 'API'),
        ('external', 'Servicio Externo'),
        ('custom', 'Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('healthy', 'Saludable'),
        ('degraded', 'Degradado'),
        ('unhealthy', 'No Saludable'),
        ('unknown', 'Desconocido'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    check_type = models.CharField(max_length=20, choices=CHECK_TYPES, verbose_name='Tipo de Verificación')
    endpoint = models.URLField(blank=True, verbose_name='Endpoint')
    check_script = models.TextField(blank=True, verbose_name='Script de Verificación')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown', verbose_name='Estado')
    last_check = models.DateTimeField(blank=True, null=True, verbose_name='Última Verificación')
    check_interval = models.IntegerField(default=60, verbose_name='Intervalo de Verificación (segundos)')
    timeout = models.IntegerField(default=30, verbose_name='Timeout (segundos)')
    retry_count = models.IntegerField(default=3, verbose_name='Número de Reintentos')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    tags = models.JSONField(default=list, verbose_name='Etiquetas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Verificación de Salud'
        verbose_name_plural = 'Verificaciones de Salud'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class HealthCheckResult(models.Model):
    """Resultados de verificaciones de salud"""
    
    health_check = models.ForeignKey(HealthCheck, on_delete=models.CASCADE, verbose_name='Verificación de Salud')
    status = models.CharField(max_length=20, choices=HealthCheck.STATUS_CHOICES, verbose_name='Estado')
    response_time = models.FloatField(verbose_name='Tiempo de Respuesta (ms)')
    message = models.TextField(blank=True, verbose_name='Mensaje')
    metadata = models.JSONField(default=dict, verbose_name='Metadatos')
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='Verificado')
    
    class Meta:
        verbose_name = 'Resultado de Verificación de Salud'
        verbose_name_plural = 'Resultados de Verificaciones de Salud'
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['health_check', 'checked_at']),
            models.Index(fields=['checked_at']),
        ]
    
    def __str__(self):
        return f"{self.health_check.name}: {self.status}"


class SystemMetrics(models.Model):
    """Métricas del sistema"""
    
    METRIC_TYPES = [
        ('cpu', 'CPU'),
        ('memory', 'Memoria'),
        ('disk', 'Disco'),
        ('network', 'Red'),
        ('process', 'Proceso'),
        ('database', 'Base de Datos'),
        ('custom', 'Personalizado'),
    ]
    
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, verbose_name='Tipo de Métrica')
    metric_name = models.CharField(max_length=100, verbose_name='Nombre de Métrica')
    value = models.FloatField(verbose_name='Valor')
    unit = models.CharField(max_length=20, blank=True, verbose_name='Unidad')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    metadata = models.JSONField(default=dict, verbose_name='Metadatos')
    
    class Meta:
        verbose_name = 'Métrica del Sistema'
        verbose_name_plural = 'Métricas del Sistema'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', 'metric_name', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.value} {self.unit}"


class NotificationChannel(models.Model):
    """Canales de notificación para alertas"""
    
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('webhook', 'Webhook'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('custom', 'Personalizado'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES, verbose_name='Tipo de Canal')
    config = models.JSONField(default=dict, verbose_name='Configuración')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Canal de Notificación'
        verbose_name_plural = 'Canales de Notificación'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.channel_type})"


class AlertTemplate(models.Model):
    """Plantillas para alertas"""
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    subject_template = models.CharField(max_length=200, verbose_name='Plantilla de Asunto')
    message_template = models.TextField(verbose_name='Plantilla de Mensaje')
    severity = models.CharField(max_length=20, choices=MonitoringRule.SEVERITY_LEVELS, verbose_name='Severidad')
    is_default = models.BooleanField(default=False, verbose_name='Por Defecto')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Plantilla de Alerta'
        verbose_name_plural = 'Plantillas de Alertas'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MonitoringDashboard(models.Model):
    """Dashboards de monitoreo personalizados"""
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    layout = models.JSONField(default=dict, verbose_name='Diseño')
    widgets = models.JSONField(default=list, verbose_name='Widgets')
    is_public = models.BooleanField(default=False, verbose_name='Público')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Dashboard de Monitoreo'
        verbose_name_plural = 'Dashboards de Monitoreo'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MonitoringWidget(models.Model):
    """Widgets para dashboards de monitoreo"""
    
    WIDGET_TYPES = [
        ('metric', 'Métrica'),
        ('chart', 'Gráfico'),
        ('table', 'Tabla'),
        ('alert', 'Alerta'),
        ('health', 'Salud'),
        ('custom', 'Personalizado'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name='Tipo de Widget')
    config = models.JSONField(default=dict, verbose_name='Configuración')
    position = models.JSONField(default=dict, verbose_name='Posición')
    size = models.JSONField(default=dict, verbose_name='Tamaño')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Widget de Monitoreo'
        verbose_name_plural = 'Widgets de Monitoreo'
        ordering = ['name']
    
    def __str__(self):
        return self.name
