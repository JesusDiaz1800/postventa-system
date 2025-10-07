from django.db import models
from django.contrib.auth.models import User


class BackupJob(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    # ADVERTENCIA: Revisa los tipos de datos y relaciones para compatibilidad total con SQL Server. Evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para trabajos de backup"""
    
    BACKUP_TYPES = [
        ('full', 'Completo'),
        ('incremental', 'Incremental'),
        ('differential', 'Diferencial'),
        ('database', 'Base de Datos'),
        ('files', 'Archivos'),
        ('custom', 'Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutándose'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
        ('paused', 'Pausado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, verbose_name='Tipo de Backup')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Configuración del backup
    source_paths = models.JSONField(default=list, verbose_name='Rutas de Origen')
    destination_path = models.CharField(max_length=500, verbose_name='Ruta de Destino')
    compression_enabled = models.BooleanField(default=True, verbose_name='Compresión Habilitada')
    encryption_enabled = models.BooleanField(default=False, verbose_name='Cifrado Habilitado')
    
    # Configuración de filtros
    include_patterns = models.JSONField(default=list, verbose_name='Patrones de Inclusión')
    exclude_patterns = models.JSONField(default=list, verbose_name='Patrones de Exclusión')
    max_file_size = models.BigIntegerField(default=0, verbose_name='Tamaño Máximo de Archivo (bytes)')
    min_file_age = models.PositiveIntegerField(default=0, verbose_name='Edad Mínima de Archivo (días)')
    
    # Configuración de retención
    retention_days = models.PositiveIntegerField(default=30, verbose_name='Días de Retención')
    max_backups = models.PositiveIntegerField(default=10, verbose_name='Máximo de Backups')
    
    # Configuración de programación
    is_scheduled = models.BooleanField(default=False, verbose_name='Programado')
    schedule_cron = models.CharField(max_length=100, blank=True, verbose_name='Expresión Cron')
    schedule_timezone = models.CharField(max_length=50, default='UTC', verbose_name='Zona Horaria')
    
    # Configuración de notificaciones
    notify_on_success = models.BooleanField(default=True, verbose_name='Notificar en Éxito')
    notify_on_failure = models.BooleanField(default=True, verbose_name='Notificar en Fallo')
    email_recipients = models.JSONField(default=list, verbose_name='Destinatarios de Email')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_backup_jobs', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Trabajo de Backup'
        verbose_name_plural = 'Trabajos de Backup'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BackupInstance(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para instancias de backup ejecutadas"""
    
    job = models.ForeignKey(BackupJob, on_delete=models.CASCADE, related_name='instances', verbose_name='Trabajo')
    status = models.CharField(max_length=20, choices=BackupJob.STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Información del backup
    backup_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del Backup')
    backup_size = models.BigIntegerField(default=0, verbose_name='Tamaño del Backup (bytes)')
    files_count = models.PositiveIntegerField(default=0, verbose_name='Número de Archivos')
    directories_count = models.PositiveIntegerField(default=0, verbose_name='Número de Directorios')
    
    # Información de compresión y cifrado
    compression_ratio = models.FloatField(default=0.0, verbose_name='Ratio de Compresión')
    encryption_algorithm = models.CharField(max_length=50, blank=True, verbose_name='Algoritmo de Cifrado')
    
    # Fechas y tiempos
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='Iniciado en')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Completado en')
    duration = models.DurationField(blank=True, null=True, verbose_name='Duración')
    
    # Usuarios
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='started_backups', verbose_name='Iniciado por')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='completed_backups', verbose_name='Completado por')
    
    # Errores y logs
    error_message = models.TextField(blank=True, verbose_name='Mensaje de Error')
    error_details = models.JSONField(default=dict, verbose_name='Detalles del Error')
    log_file_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del Archivo de Log')
    
    # Metadatos
    metadata = models.JSONField(default=dict, verbose_name='Metadatos')
    
    class Meta:
        verbose_name = 'Instancia de Backup'
        verbose_name_plural = 'Instancias de Backup'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.job.name} - {self.get_status_display()}"


class RestoreJob(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para trabajos de restauración"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutándose'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Configuración de restauración
    backup_instance = models.ForeignKey(BackupInstance, on_delete=models.CASCADE, related_name='restore_jobs', verbose_name='Instancia de Backup')
    destination_path = models.CharField(max_length=500, verbose_name='Ruta de Destino')
    overwrite_existing = models.BooleanField(default=False, verbose_name='Sobrescribir Existentes')
    
    # Configuración de filtros
    include_patterns = models.JSONField(default=list, verbose_name='Patrones de Inclusión')
    exclude_patterns = models.JSONField(default=list, verbose_name='Patrones de Exclusión')
    restore_permissions = models.BooleanField(default=True, verbose_name='Restaurar Permisos')
    restore_timestamps = models.BooleanField(default=True, verbose_name='Restaurar Timestamps')
    
    # Fechas y tiempos
    started_at = models.DateTimeField(blank=True, null=True, verbose_name='Iniciado en')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Completado en')
    duration = models.DurationField(blank=True, null=True, verbose_name='Duración')
    
    # Usuarios
    started_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='started_restores', verbose_name='Iniciado por')
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='completed_restores', verbose_name='Completado por')
    
    # Errores y logs
    error_message = models.TextField(blank=True, verbose_name='Mensaje de Error')
    error_details = models.JSONField(default=dict, verbose_name='Detalles del Error')
    log_file_path = models.CharField(max_length=500, blank=True, verbose_name='Ruta del Archivo de Log')
    
    # Metadatos
    metadata = models.JSONField(default=dict, verbose_name='Metadatos')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Trabajo de Restauración'
        verbose_name_plural = 'Trabajos de Restauración'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"


class BackupSchedule(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para programación de backups"""
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('paused', 'Pausado'),
        ('inactive', 'Inactivo'),
    ]
    
    job = models.ForeignKey(BackupJob, on_delete=models.CASCADE, related_name='schedules', verbose_name='Trabajo de Backup')
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
    
    # Configuración de notificaciones
    notify_on_success = models.BooleanField(default=True, verbose_name='Notificar en Éxito')
    notify_on_failure = models.BooleanField(default=True, verbose_name='Notificar en Fallo')
    email_recipients = models.JSONField(default=list, verbose_name='Destinatarios de Email')
    
    # Fechas
    last_executed = models.DateTimeField(blank=True, null=True, verbose_name='Última Ejecución')
    next_execution = models.DateTimeField(blank=True, null=True, verbose_name='Próxima Ejecución')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_backup_schedules', verbose_name='Creado por')
    
    class Meta:
        verbose_name = 'Programación de Backup'
        verbose_name_plural = 'Programaciones de Backup'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.job.name})"


class BackupStorage(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para configuraciones de almacenamiento de backup"""
    
    STORAGE_TYPES = [
        ('local', 'Local'),
        ('ftp', 'FTP'),
        ('sftp', 'SFTP'),
        ('s3', 'Amazon S3'),
        ('azure', 'Azure Blob Storage'),
        ('gcp', 'Google Cloud Storage'),
        ('dropbox', 'Dropbox'),
        ('onedrive', 'OneDrive'),
        ('custom', 'Personalizado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPES, verbose_name='Tipo de Almacenamiento')
    
    # Configuración de conexión
    host = models.CharField(max_length=255, blank=True, verbose_name='Host')
    port = models.PositiveIntegerField(blank=True, null=True, verbose_name='Puerto')
    username = models.CharField(max_length=100, blank=True, verbose_name='Usuario')
    password = models.CharField(max_length=255, blank=True, verbose_name='Contraseña')
    path = models.CharField(max_length=500, blank=True, verbose_name='Ruta')
    
    # Configuración específica por tipo
    config = models.JSONField(default=dict, verbose_name='Configuración')
    
    # Configuración de SSL/TLS
    use_ssl = models.BooleanField(default=False, verbose_name='Usar SSL')
    verify_ssl = models.BooleanField(default=True, verbose_name='Verificar SSL')
    
    # Configuración de proxy
    use_proxy = models.BooleanField(default=False, verbose_name='Usar Proxy')
    proxy_host = models.CharField(max_length=255, blank=True, verbose_name='Host del Proxy')
    proxy_port = models.PositiveIntegerField(blank=True, null=True, verbose_name='Puerto del Proxy')
    proxy_username = models.CharField(max_length=100, blank=True, verbose_name='Usuario del Proxy')
    proxy_password = models.CharField(max_length=255, blank=True, verbose_name='Contraseña del Proxy')
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_backup_storages', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Almacenamiento de Backup'
        verbose_name_plural = 'Almacenamientos de Backup'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_storage_type_display()})"


class BackupLog(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para logs de backup"""
    
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Crítico'),
    ]
    
    job = models.ForeignKey(BackupJob, on_delete=models.CASCADE, related_name='logs', verbose_name='Trabajo de Backup')
    instance = models.ForeignKey(BackupInstance, on_delete=models.CASCADE, related_name='logs', blank=True, null=True, verbose_name='Instancia')
    level = models.CharField(max_length=20, choices=LOG_LEVELS, verbose_name='Nivel')
    message = models.TextField(verbose_name='Mensaje')
    details = models.JSONField(default=dict, verbose_name='Detalles')
    
    # Contexto
    step = models.CharField(max_length=100, blank=True, verbose_name='Paso')
    duration = models.DurationField(blank=True, null=True, verbose_name='Duración')
    
    # Metadatos
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')
    
    class Meta:
        verbose_name = 'Log de Backup'
        verbose_name_plural = 'Logs de Backup'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.job.name} - {self.get_level_display()} - {self.timestamp}"


class BackupPolicy(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para políticas de backup"""
    
    POLICY_TYPES = [
        ('retention', 'Retención'),
        ('compression', 'Compresión'),
        ('encryption', 'Cifrado'),
        ('verification', 'Verificación'),
        ('notification', 'Notificación'),
        ('scheduling', 'Programación'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES, verbose_name='Tipo de Política')
    
    # Configuración de la política
    config = models.JSONField(default=dict, verbose_name='Configuración')
    
    # Aplicación
    applies_to_jobs = models.JSONField(default=list, verbose_name='Se Aplica a Trabajos')
    applies_to_schedules = models.JSONField(default=list, verbose_name='Se Aplica a Programaciones')
    
    # Metadatos
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    priority = models.PositiveIntegerField(default=0, verbose_name='Prioridad')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_backup_policies', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Política de Backup'
        verbose_name_plural = 'Políticas de Backup'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_policy_type_display()})"
