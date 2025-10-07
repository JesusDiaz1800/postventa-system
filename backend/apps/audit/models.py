from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

class AuditLogManager:
    @staticmethod
    def log_action(user, action, resource_type=None, resource_id=None, metadata=None, ip_address=None, description=None):
        """Registrar una acción en el log de auditoría"""
        try:
            # Crear el registro de auditoría
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                module=resource_type,  # Usar resource_type como módulo
                description=description or f'Acción {action} en {resource_type}',
                ip_address=ip_address,
                metadata=metadata or {},
                timestamp=timezone.now(),
                severity='medium',  # Valor por defecto
                category='data_access'  # Valor por defecto
            )
            
            # Si hay un objeto relacionado, intentar configurarlo
            if resource_type and resource_id:
                try:
                    from django.apps import apps
                    model = apps.get_model(resource_type)
                    obj = model.objects.get(id=resource_id)
                    audit_log.content_type = ContentType.objects.get_for_model(obj)
                    audit_log.object_id = obj.id
                    audit_log.save()
                except Exception as e:
                    print(f'Error al configurar objeto relacionado: {e}')
            
            return audit_log
                
        except Exception as e:
            print(f'Error al registrar auditoría: {e}')
            return None


class AuditLog(models.Model):
    # ADVERTENCIA: Revisa los tipos de datos y relaciones para compatibilidad total con SQL Server. Evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Registro de auditoría para todas las acciones del sistema"""
    
    ACTION_TYPES = [
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('view', 'Ver'),
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('approve', 'Aprobar'),
        ('reject', 'Rechazar'),
        ('escalate', 'Escalar'),
        ('assign', 'Asignar'),
        ('upload', 'Subir'),
        ('download', 'Descargar'),
        ('export', 'Exportar'),
        ('import', 'Importar'),
        ('search', 'Buscar'),
        ('filter', 'Filtrar'),
        ('sort', 'Ordenar'),
        ('print', 'Imprimir'),
        ('share', 'Compartir'),
        ('comment', 'Comentar'),
        ('tag', 'Etiquetar'),
        ('archive', 'Archivar'),
        ('restore', 'Restaurar'),
        ('backup', 'Respaldo'),
        ('restore_backup', 'Restaurar Respaldo'),
        ('system_action', 'Acción del Sistema'),
        ('error', 'Error'),
        ('warning', 'Advertencia'),
        ('info', 'Información'),
        ('debug', 'Debug'),
    ]
    
    RESULT_TYPES = [
        ('success', 'Éxito'),
        ('failure', 'Fallo'),
        ('partial', 'Parcial'),
        ('cancelled', 'Cancelado'),
        ('timeout', 'Tiempo Agotado'),
        ('unauthorized', 'No Autorizado'),
        ('forbidden', 'Prohibido'),
        ('not_found', 'No Encontrado'),
        ('error', 'Error'),
    ]
    
    # Información básica
    action = models.CharField(max_length=50, choices=ACTION_TYPES, verbose_name='Acción')
    result = models.CharField(max_length=20, choices=RESULT_TYPES, default='success', verbose_name='Resultado')
    description = models.TextField(verbose_name='Descripción')
    
    # Usuario y sesión
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    session_key = models.CharField(max_length=40, blank=True, verbose_name='Clave de Sesión')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    
    # Objeto relacionado (Generic Foreign Key)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Datos de la acción
    old_values = models.JSONField(default=dict, blank=True, verbose_name='Valores Anteriores')
    new_values = models.JSONField(default=dict, blank=True, verbose_name='Valores Nuevos')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadatos')
    
    # Información de tiempo y ubicación
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    duration = models.DurationField(null=True, blank=True, verbose_name='Duración')
    
    # Información adicional
    module = models.CharField(max_length=100, blank=True, verbose_name='Módulo')
    function = models.CharField(max_length=100, blank=True, verbose_name='Función')
    line_number = models.PositiveIntegerField(null=True, blank=True, verbose_name='Número de Línea')
    
    # Clasificación
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ], default='medium', verbose_name='Severidad')
    
    category = models.CharField(max_length=50, choices=[
        ('authentication', 'Autenticación'),
        ('authorization', 'Autorización'),
        ('data_access', 'Acceso a Datos'),
        ('data_modification', 'Modificación de Datos'),
        ('system_config', 'Configuración del Sistema'),
        ('user_management', 'Gestión de Usuarios'),
        ('security', 'Seguridad'),
        ('performance', 'Rendimiento'),
        ('error', 'Error'),
        ('business_logic', 'Lógica de Negocio'),
        ('integration', 'Integración'),
        ('backup', 'Respaldo'),
        ('audit', 'Auditoría'),
    ], default='data_access', verbose_name='Categoría')
    
    # Información de contexto
    request_id = models.CharField(max_length=100, blank=True, verbose_name='ID de Request')
    correlation_id = models.CharField(max_length=100, blank=True, verbose_name='ID de Correlación')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['result', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.user or 'Sistema'} - {self.timestamp}"
    
    @property
    def is_successful(self):
        """Verificar si la acción fue exitosa"""
        return self.result == 'success'
    
    @property
    def is_failure(self):
        """Verificar si la acción falló"""
        return self.result == 'failure'
    
    @property
    def is_high_severity(self):
        """Verificar si es de alta severidad"""
        return self.severity in ['high', 'critical']
    
    @property
    def formatted_timestamp(self):
        """Timestamp formateado"""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    @property
    def formatted_duration(self):
        """Duración formateada"""
        if not self.duration:
            return 'N/A'
        
        total_seconds = int(self.duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_changes_summary(self):
        """Obtener resumen de cambios"""
        if not self.old_values and not self.new_values:
            return "Sin cambios"
        
        changes = []
        all_keys = set(self.old_values.keys()) | set(self.new_values.keys())
        
        for key in all_keys:
            old_value = self.old_values.get(key)
            new_value = self.new_values.get(key)
            
            if old_value != new_value:
                changes.append(f"{key}: {old_value} → {new_value}")
        
        return "; ".join(changes) if changes else "Sin cambios"


class AuditRule(models.Model):
    """Reglas de auditoría para configurar qué eventos auditar"""
    
    RULE_TYPES = [
        ('include', 'Incluir'),
        ('exclude', 'Excluir'),
        ('alert', 'Alerta'),
        ('block', 'Bloquear'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción', blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, verbose_name='Tipo de Regla')
    
    # Condiciones
    action_filter = models.CharField(max_length=50, blank=True, verbose_name='Filtro de Acción')
    user_filter = models.CharField(max_length=100, blank=True, verbose_name='Filtro de Usuario')
    ip_filter = models.CharField(max_length=100, blank=True, verbose_name='Filtro de IP')
    module_filter = models.CharField(max_length=100, blank=True, verbose_name='Filtro de Módulo')
    severity_filter = models.CharField(max_length=20, blank=True, verbose_name='Filtro de Severidad')
    category_filter = models.CharField(max_length=50, blank=True, verbose_name='Filtro de Categoría')
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    priority = models.PositiveIntegerField(default=0, verbose_name='Prioridad')
    
    # Acciones
    alert_email = models.EmailField(blank=True, verbose_name='Email de Alerta')
    alert_webhook = models.URLField(blank=True, verbose_name='Webhook de Alerta')
    block_action = models.BooleanField(default=False, verbose_name='Bloquear Acción')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_audit_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = 'Regla de Auditoría'
        verbose_name_plural = 'Reglas de Auditoría'
    
    def __str__(self):
        return f"{self.name} - {self.get_rule_type_display()}"


class AuditReport(models.Model):
    """Reportes de auditoría generados"""
    
    REPORT_TYPES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
        ('custom', 'Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('generating', 'Generando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción', blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name='Tipo de Reporte')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Filtros del reporte
    date_from = models.DateTimeField(verbose_name='Fecha Desde')
    date_to = models.DateTimeField(verbose_name='Fecha Hasta')
    user_filter = models.CharField(max_length=100, blank=True, verbose_name='Filtro de Usuario')
    action_filter = models.CharField(max_length=50, blank=True, verbose_name='Filtro de Acción')
    severity_filter = models.CharField(max_length=20, blank=True, verbose_name='Filtro de Severidad')
    category_filter = models.CharField(max_length=50, blank=True, verbose_name='Filtro de Categoría')
    
    # Configuración
    include_details = models.BooleanField(default=True, verbose_name='Incluir Detalles')
    include_changes = models.BooleanField(default=True, verbose_name='Incluir Cambios')
    include_metadata = models.BooleanField(default=False, verbose_name='Incluir Metadatos')
    group_by = models.CharField(max_length=50, blank=True, verbose_name='Agrupar Por')
    
    # Resultados
    total_records = models.PositiveIntegerField(default=0, verbose_name='Total de Registros')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del Archivo')
    file_size = models.PositiveIntegerField(default=0, verbose_name='Tamaño del Archivo')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_audit_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reporte de Auditoría'
        verbose_name_plural = 'Reportes de Auditoría'
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    @property
    def is_completed(self):
        """Verificar si el reporte está completado"""
        return self.status == 'completed'
    
    @property
    def is_generating(self):
        """Verificar si el reporte se está generando"""
        return self.status == 'generating'
    
    @property
    def formatted_file_size(self):
        """Tamaño del archivo formateado"""
        if not self.file_size:
            return 'N/A'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        
        return f"{self.file_size:.1f} TB"


class AuditDashboard(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Configuración del dashboard de auditoría"""
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(verbose_name='Descripción', blank=True)
    
    # Configuración de widgets
    widgets_config = models.JSONField(default=dict, verbose_name='Configuración de Widgets')
    
    # Filtros por defecto
    default_filters = models.JSONField(default=dict, verbose_name='Filtros por Defecto')
    
    # Configuración de actualización
    auto_refresh = models.BooleanField(default=True, verbose_name='Actualización Automática')
    refresh_interval = models.PositiveIntegerField(default=300, verbose_name='Intervalo de Actualización (segundos)')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_audit_dashboards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Dashboard de Auditoría'
        verbose_name_plural = 'Dashboards de Auditoría'
    
    def __str__(self):
        return self.name


class AuditAlert(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Alertas de auditoría"""
    
    SEVERITY_LEVELS = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('acknowledged', 'Reconocido'),
        ('resolved', 'Resuelto'),
        ('dismissed', 'Descartado'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name='Severidad')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    
    # Relación con registro de auditoría
    audit_log = models.ForeignKey(AuditLog, on_delete=models.CASCADE, related_name='alerts')
    
    # Información de resolución
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_audit_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, verbose_name='Notas de Resolución')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alerta de Auditoría'
        verbose_name_plural = 'Alertas de Auditoría'
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"
    
    @property
    def is_active(self):
        """Verificar si la alerta está activa"""
        return self.status == 'active'
    
    @property
    def is_resolved(self):
        """Verificar si la alerta está resuelta"""
        return self.status == 'resolved'
    
    def resolve(self, user, notes=''):
        """Resolver alerta"""
        self.status = 'resolved'
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()
    
    def acknowledge(self, user):
        """Reconocer alerta"""
        self.status = 'acknowledged'
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()
    
    def dismiss(self, user):
        """Descartar alerta"""
        self.status = 'dismissed'
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()