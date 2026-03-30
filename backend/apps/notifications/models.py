from django.db import models
from django.conf import settings
from django.utils import timezone

# Postgres-specific fields may import psycopg/psycopg2 at import time.
# Make ArrayField optional so the app can run on SQL Server without psycopg.
try:
    from django.contrib.postgres.fields import ArrayField  # type: ignore
    POSTGRES_ARRAY_AVAILABLE = True
except Exception:
    # Fallback: use JSONField to store array-like data on non-Postgres DBs
    ArrayField = models.JSONField  # type: ignore
    POSTGRES_ARRAY_AVAILABLE = False

# Re-export NotificationPreferences if defined in a submodule for backwards compatibility.
# The preferences module historically lived under `models/preferences.py` (a subpackage).
# A naive relative import of `.preferences` fails because this file is `models.py`.
# Try the subpackage path first, then an absolute import as a fallback, and finally
# continue silently if not present (older layouts may not have it).
try:
    # Prefer the submodule under the models package
    from .models.preferences import NotificationPreferences  # type: ignore
except Exception:
    try:
        # Fallback to absolute import (package-style)
        from apps.notifications.models.preferences import NotificationPreferences  # type: ignore
    except Exception:
        # preferences module may not exist in older layouts; ignore and continue
        pass


class NotificationCategory(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo para categorías de notificaciones"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_categories'
        verbose_name = 'Categoría de notificación'
        verbose_name_plural = 'Categorías de notificaciones'

    def __str__(self):
        return self.name


class NotificationBase(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, evita campos no soportados y usa ForeignKey/ManyToMany donde sea necesario.
    """Modelo base abstracto para notificaciones"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)
    category = models.ForeignKey(
        NotificationCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_notifications'
    )
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])


class Notification(NotificationBase):
    """Modelo principal de notificaciones"""
    NOTIFICATION_TYPES = [
        ('incident_created', 'Incidencia Creada'),
        ('incident_updated', 'Incidencia Actualizada'),
        ('incident_escalated', 'Incidencia Escalada'),
        ('incident_closed', 'Incidencia Cerrada'),
        ('document_uploaded', 'Documento Subido'),
        ('document_approved', 'Documento Aprobado'),
        ('document_rejected', 'Documento Rechazado'),
        ('workflow_step_completed', 'Paso de Workflow Completado'),
        ('workflow_approval_required', 'Aprobación de Workflow Requerida'),
        ('system_alert', 'Alerta del Sistema'),
        ('user_assigned', 'Usuario Asignado'),
        ('deadline_approaching', 'Fecha Límite Próxima'),
        ('deadline_exceeded', 'Fecha Límite Excedida'),
        ('quality_report_submitted', 'Reporte de Calidad Enviado'),
        ('quality_report_approved', 'Reporte de Calidad Aprobado'),
        ('quality_report_rejected', 'Reporte de Calidad Rechazado'),
        ('visit_report_submitted', 'Reporte de Visita Enviado'),
        ('visit_report_approved', 'Reporte de Visita Aprobado'),
        ('visit_report_rejected', 'Reporte de Visita Rechazado')
    ]
    
    # Campos específicos
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    related_url = models.URLField(max_length=500, blank=True, null=True)
    related_incident_id = models.PositiveIntegerField(null=True, blank=True)
    related_document_id = models.PositiveIntegerField(null=True, blank=True)
    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='related_notifications'
    )
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'is_important']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['category'])
        ]
    
    def __str__(self):
        return f'{self.title} ({self.user.username})'
    
    @classmethod
    def create_notification(cls, user, title, message, notification_type, 
                        category=None, is_important=False, is_system=False,
                        related_incident=None, related_document=None, 
                        related_user=None, metadata=None, related_url=None):
        """Método helper para crear notificaciones"""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            is_important=is_important,
            is_system=is_system,
            related_incident_id=related_incident.id if related_incident else None,
            related_document_id=related_document.id if related_document else None,
            related_user=related_user,
            metadata=metadata or {},
            related_url=related_url
        )
    
    @classmethod
    def get_unread_count(cls, user):
        """Obtener conteo de notificaciones no leídas"""
        return cls.objects.filter(user=user, is_read=False).count()
    
    @classmethod
    def mark_all_as_read(cls, user):
        """Marcar todas las notificaciones como leídas"""
        now = timezone.now()
        cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=now,
            updated_at=now
        )



class NotificationPreference(models.Model):
    # ADVERTENCIA: Para compatibilidad con SQL Server, usa TextField para listas y considera migrar a ManyToMany en el futuro.
    class Meta:
        app_label = 'notifications'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    web_enabled = models.BooleanField(default=True)
    
    # Notification type preferences
    incident_created = models.BooleanField(default=True)
    incident_updated = models.BooleanField(default=True)
    incident_escalated = models.BooleanField(default=True)
    incident_closed = models.BooleanField(default=True)
    document_uploaded = models.BooleanField(default=True)
    document_approved = models.BooleanField(default=True)
    document_rejected = models.BooleanField(default=True)
    workflow_step_completed = models.BooleanField(default=True)
    workflow_approval_required = models.BooleanField(default=True)
    system_alert = models.BooleanField(default=True)
    user_assigned = models.BooleanField(default=True)
    deadline_approaching = models.BooleanField(default=True)
    deadline_exceeded = models.BooleanField(default=True)

    # Priority thresholds
    priority_threshold = models.CharField(max_length=20, choices=[
        ('all', 'Todas'),
        ('medium_up', 'Media y superior'),
        ('high_up', 'Alta y superior'),
        ('urgent_only', 'Solo urgentes')
    ], default='all')

    # Daily notification windows
    notification_start_time = models.TimeField(default='09:00')
    notification_end_time = models.TimeField(default='18:00')
    quiet_hours = models.BooleanField(default=True)

    # Weekend preferences
    weekend_notifications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def should_notify(self, notification_type, importance=False):
        """
        Determina si se debe notificar al usuario basado en sus preferencias.
        """
        if not self.web_enabled and not self.email_enabled:
            return False
            
        type_enabled = getattr(self, notification_type, True)
        if not type_enabled:
            return False
            
        if self.priority_threshold == 'urgent_only' and not importance:
            return False
        if self.priority_threshold == 'high_up' and not importance:
            return False
            
        return True


# Backwards compatibility: some parts of the project expect the plural name
# `NotificationPreferences`. Provide an alias so imports like
# `from .models import NotificationPreferences` continue to work.
try:
    NotificationPreferences = NotificationPreference
except NameError:
    # If for some reason the singular class isn't defined, skip aliasing.
    pass
