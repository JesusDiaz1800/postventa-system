"""
Modelos para el sistema de auditoría
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json

User = get_user_model()

class AuditLog(models.Model):
    """
    Modelo para registrar todas las acciones del sistema
    """
    ACTION_CHOICES = [
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('view', 'Ver'),
        ('export', 'Exportar'),
        ('import', 'Importar'),
        ('approve', 'Aprobar'),
        ('reject', 'Rechazar'),
        ('assign', 'Asignar'),
        ('unassign', 'Desasignar'),
        ('close', 'Cerrar'),
        ('reopen', 'Reabrir'),
        ('generate', 'Generar'),
        ('download', 'Descargar'),
        ('upload', 'Subir'),
    ]
    
    RESOURCE_TYPE_CHOICES = [
        ('incident', 'Incidencia'),
        ('user', 'Usuario'),
        ('document', 'Documento'),
        ('workflow', 'Workflow'),
        ('report', 'Reporte'),
        ('attachment', 'Adjunto'),
        ('image', 'Imagen'),
        ('lab_report', 'Informe de Laboratorio'),
        ('visit_report', 'Reporte de Visita'),
        ('supplier_report', 'Informe para Proveedor'),
        ('audit_log', 'Log de Auditoría'),
        ('system', 'Sistema'),
    ]
    
    # Información básica
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='Usuario que realizó la acción'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='Tipo de acción realizada'
    )
    
    resource_type = models.CharField(
        max_length=30,
        choices=RESOURCE_TYPE_CHOICES,
        help_text='Tipo de recurso afectado'
    )
    
    resource_id = models.CharField(
        max_length=100,
        help_text='ID del recurso afectado'
    )
    
    # Información del recurso (opcional, para referencias más específicas)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Tipo de contenido del recurso'
    )
    
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID del objeto específico'
    )
    
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Detalles de la acción
    details = models.TextField(
        help_text='Descripción detallada de la acción'
    )
    
    # Información técnica
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Dirección IP del usuario'
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text='User Agent del navegador'
    )
    
    # Metadatos adicionales
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Metadatos adicionales en formato JSON'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora de la acción'
    )
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['resource_type', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user or 'Sistema'} - {self.get_action_display()} - {self.resource_type} #{self.resource_id}"
    
    @property
    def action_display(self):
        """Retorna el nombre legible de la acción"""
        return dict(self.ACTION_CHOICES).get(self.action, self.action)
    
    @property
    def resource_type_display(self):
        """Retorna el nombre legible del tipo de recurso"""
        return dict(self.RESOURCE_TYPE_CHOICES).get(self.resource_type, self.resource_type)
    
    @property
    def user_display(self):
        """Retorna el nombre del usuario o 'Sistema' si es None"""
        return self.user.username if self.user else 'Sistema'
    
    @property
    def created_at_display(self):
        """Retorna la fecha formateada"""
        return self.created_at.strftime('%d/%m/%Y %H:%M:%S')


class AuditLogManager:
    """
    Manager para facilitar la creación de logs de auditoría
    """
    
    @staticmethod
    def log_action(user, action, resource_type, resource_id, details, 
                   ip_address=None, user_agent=None, metadata=None, 
                   content_object=None):
        """
        Crear un log de auditoría
        
        Args:
            user: Usuario que realizó la acción
            action: Tipo de acción (create, update, delete, etc.)
            resource_type: Tipo de recurso afectado
            resource_id: ID del recurso
            details: Descripción de la acción
            ip_address: IP del usuario (opcional)
            user_agent: User Agent (opcional)
            metadata: Metadatos adicionales (opcional)
            content_object: Objeto específico afectado (opcional)
        """
        try:
            # Determinar content_type y object_id si se proporciona content_object
            content_type = None
            object_id = None
            if content_object:
                content_type = ContentType.objects.get_for_model(content_object)
                object_id = content_object.pk
            
            # Crear el log
            audit_log = AuditLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id),
                content_type=content_type,
                object_id=object_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata or {}
            )
            
            return audit_log
            
        except Exception as e:
            # En caso de error, intentar crear un log básico
            try:
                return AuditLog.objects.create(
                    user=user,
                    action=action,
                    resource_type=resource_type,
                    resource_id=str(resource_id),
                    details=f"{details} (Error al crear log completo: {str(e)})",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    metadata={'error': str(e)}
                )
            except Exception:
                # Si falla completamente, no hacer nada para evitar errores en cascada
                pass
    
    @staticmethod
    def log_user_action(user, action, details, request=None):
        """
        Log específico para acciones de usuario
        
        Args:
            user: Usuario
            action: Acción realizada
            details: Detalles de la acción
            request: Request object (opcional, para extraer IP y User Agent)
        """
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT')
        
        return AuditLogManager.log_action(
            user=user,
            action=action,
            resource_type='user',
            resource_id=str(user.id) if user else '0',
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_incident_action(user, action, incident, details, request=None):
        """
        Log específico para acciones de incidencias
        
        Args:
            user: Usuario
            action: Acción realizada
            incident: Objeto de incidencia
            details: Detalles de la acción
            request: Request object (opcional)
        """
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT')
        
        return AuditLogManager.log_action(
            user=user,
            action=action,
            resource_type='incident',
            resource_id=str(incident.id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            content_object=incident
        )
    
    @staticmethod
    def log_document_action(user, action, document, details, request=None):
        """
        Log específico para acciones de documentos
        
        Args:
            user: Usuario
            action: Acción realizada
            document: Objeto de documento
            details: Detalles de la acción
            request: Request object (opcional)
        """
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT')
        
        return AuditLogManager.log_action(
            user=user,
            action=action,
            resource_type='document',
            resource_id=str(document.id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            content_object=document
        )