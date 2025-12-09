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
    
    # Tipos de acción en español
    ACTION_CHOICES = [
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('crear', 'Crear'),
        ('actualizar', 'Actualizar'),
        ('eliminar', 'Eliminar'),
        ('ver', 'Ver'),
        ('subir', 'Subir Archivo'),
        ('descargar', 'Descargar Archivo'),
        ('escalar', 'Escalar'),
        ('cerrar', 'Cerrar'),
        ('aprobar', 'Aprobar'),
        ('rechazar', 'Rechazar'),
        ('exportar', 'Exportar'),
        ('buscar', 'Buscar'),
        ('filtrar', 'Filtrar'),
        ('error', 'Error'),
    ]
    
    # Campos principales
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Usuario')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='Acción')
    description = models.TextField(verbose_name='Descripción')
    details = models.JSONField(default=dict, blank=True, verbose_name='Detalles Adicionales')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora')
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
    
    def __str__(self):
        username = self.user.username if self.user else 'Sistema'
        return f"{self.get_action_display()} - {username} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def formatted_timestamp(self):
        """Timestamp formateado en español"""
        return self.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    
    @property
    def user_display(self):
        """Usuario formateado"""
        if self.user:
            return f"{self.user.username} ({self.user.get_full_name() or self.user.email})"
        return 'Sistema'
    
    @property
    def action_icon(self):
        """Icono para la acción"""
        icon_map = {
            'login': '🔑',
            'logout': '🚪',
            'crear': '➕',
            'actualizar': '✏️',
            'eliminar': '🗑️',
            'ver': '👁️',
            'subir': '📤',
            'descargar': '📥',
            'escalar': '⬆️',
            'cerrar': '✅',
            'aprobar': '👍',
            'rechazar': '👎',
            'exportar': '📊',
            'buscar': '🔍',
            'filtrar': '🔽',
            'error': '❌',
        }
        return icon_map.get(self.action, '📝')
    
    @property
    def action_color(self):
        """Color para la acción"""
        color_map = {
            'login': 'text-green-600',
            'logout': 'text-gray-600',
            'crear': 'text-blue-600',
            'actualizar': 'text-yellow-600',
            'eliminar': 'text-red-600',
            'ver': 'text-gray-600',
            'subir': 'text-blue-600',
            'descargar': 'text-green-600',
            'escalar': 'text-orange-600',
            'cerrar': 'text-green-600',
            'aprobar': 'text-green-600',
            'rechazar': 'text-red-600',
            'exportar': 'text-purple-600',
            'buscar': 'text-blue-600',
            'filtrar': 'text-gray-600',
            'error': 'text-red-600',
        }
        return color_map.get(self.action, 'text-gray-600')
