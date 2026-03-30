from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AuditLogManager:
    @staticmethod
    def log_action(user, action, description=None, ip_address=None, details=None):
        """Registrar una acción en el log de auditoría - versión simplificada"""
        try:
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                description=description or f'Acción {action} realizada',
                ip_address=ip_address,
                details=details or {},
                timestamp=timezone.now()
            )
            return audit_log
        except Exception as e:
            print(f'Error al registrar auditoría: {e}')
            return None


class AuditLog(models.Model):
    """Registro de auditoría simplificado para todas las acciones del sistema"""
    
    # Tipos de acción - Solo las acciones actuales permitidas
    ACTION_CHOICES = [
        # Autenticación
        ('user_login', 'Iniciar Sesión'),
        ('user_logout', 'Cerrar Sesión'),
        
        # Incidentes
        ('incident_created', 'Incidente Creado'),
        ('incident_closed', 'Incidente Cerrado'),
        ('escalation_triggered', 'Incidente Escalado'),
        
        # Reportes
        ('report_attached', 'Reporte Adjuntado'),
        ('report_created', 'Reporte Creado'),
        ('report_updated', 'Reporte Editado'),
        
        # Operaciones Genéricas
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('item_restored', 'Elemento Restaurado'),
        
        # Integración SAP
        ('sap_sync_error', 'Fallo Sincronización SAP'),
        
        # Errores de Sistema
        ('pdf_error', 'Error en Generación de PDF'),
        ('api_error', 'Error de Integración API'),
    ]
    
    # Campos principales
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuario', db_index=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='Acción', db_index=True)
    description = models.TextField(verbose_name='Descripción')
    details = models.JSONField(default=dict, blank=True, verbose_name='Detalles Adicionales')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP', db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora', db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'action']),
            models.Index(fields=['user', 'action']),
        ]
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
    
    def __str__(self):
        username = self.user.username if self.user else 'Sistema'
        return f"{self.get_action_display()} - {username} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def formatted_timestamp(self):
        """Timestamp formateado en español"""
        # Ajustar timezone si es necesario, pero settings.py ya tiene Santiago.
        return self.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    
    @property
    def action_icon(self):
        """Icono para la acción"""
        icon_map = {
            'user_login': '🔑',
            'user_logout': '🚪',
            
            'incident_created': '➕',
            'incident_closed': '✅',
            'escalation_triggered': '🔥',
            
            'report_attached': '📎',
            
            'create': '➕',
            'delete': '🗑️',
            'item_restored': '♻️',
            'sap_sync_error': '❌',
            'pdf_error': '📄',
            'api_error': '🤖',
        }
        return icon_map.get(self.action, '📝')
    
    @property
    def action_color(self):
        """Color para la acción"""
        color_map = {
            'user_login': 'text-green-600',
            'user_logout': 'text-gray-500',
            
            'incident_created': 'text-blue-700',
            'incident_closed': 'text-green-700 font-bold',
            'escalation_triggered': 'text-red-600 font-bold',
            
            'report_attached': 'text-purple-600',
            
            'create': 'text-blue-600',
            'delete': 'text-red-700',
            'item_restored': 'text-teal-600',
            'sap_sync_error': 'text-red-600 font-bold animate-pulse',
            'pdf_error': 'text-orange-600',
            'api_error': 'text-red-500 font-semibold',
        }
        return color_map.get(self.action, 'text-gray-600')


class DeletedItem(models.Model):
    """
    Modelo para almacenar elementos eliminados (Papelera de Reciclaje)
    Retención por 3 días para restauración.
    """
    original_id = models.CharField(max_length=255, help_text="ID original del objeto")
    model_name = models.CharField(max_length=100, help_text="Nombre del modelo (ej. Incident)")
    app_label = models.CharField(max_length=100, help_text="App del modelo (ej. incidents)")
    
    # Datos completos serializados para restauración
    serialized_data = models.JSONField(help_text="Datos completos del objeto en formato JSON")
    
    deleted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    deleted_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='deleted_items'
    )
    
    # Fecha límite para restaurar (se calcula al crear)
    restore_deadline = models.DateTimeField(db_index=True)
    
    # Representación legible del objeto (ej: "Incidencia #123 - Fuga de agua")
    object_repr = models.CharField(max_length=255, default="Elemento eliminado", help_text="Representación legible del objeto")
    
    # Razón de eliminación
    deletion_reason = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.restore_deadline:
            # 3 días de retención por defecto
            self.restore_deadline = timezone.now() + timezone.timedelta(days=3)
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Elemento Eliminado'
        verbose_name_plural = 'Elementos Eliminados (Papelera)'
        ordering = ['-deleted_at']
        indexes = [
            models.Index(fields=['app_label', 'model_name']),
            models.Index(fields=['deleted_at']),
        ]
        
    def __str__(self):
        return f"{self.model_name} #{self.original_id} - Eliminado el {self.deleted_at.strftime('%d/%m/%Y')}"
