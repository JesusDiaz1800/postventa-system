from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer, 
    NotificationPreferenceSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener notificaciones del usuario autenticado"""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Obtener conteo de notificaciones no leídas"""
        count = Notification.get_unread_count(request.user)
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marcar todas las notificaciones como leídas"""
        Notification.mark_all_as_read(request.user)
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marcar una notificación como leída"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'success'})
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Obtener notificaciones recientes (últimas 10)"""
        notifications = self.get_queryset()[:10]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def important(self, request):
        """Obtener notificaciones importantes"""
        notifications = self.get_queryset().filter(is_important=True)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Obtener notificaciones por tipo"""
        notification_type = request.query_params.get('type')
        if notification_type:
            notifications = self.get_queryset().filter(notification_type=notification_type)
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        return Response({'error': 'Tipo de notificación requerido'}, status=400)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener preferencias del usuario autenticado"""
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Obtener o crear preferencias del usuario"""
        preferences, created = NotificationPreference.get_or_create_preferences(self.request.user)
        return preferences
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Obtener preferencias del usuario actual"""
        preferences = self.get_object()
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)



# Funciones helper para crear notificaciones
def create_incident_notification(incident, action, user=None):
    """Crear notificación para eventos de incidencia"""
    if action == 'created':
        title = f"Nueva Incidencia: {incident.title}"
        message = f"Se ha creado una nueva incidencia {incident.code}: {incident.title}"
        notification_type = 'incident_created'
    elif action == 'updated':
        title = f"Incidencia Actualizada: {incident.title}"
        message = f"La incidencia {incident.code} ha sido actualizada"
        notification_type = 'incident_updated'
    elif action == 'escalated':
        title = f"Incidencia Escalada: {incident.title}"
        message = f"La incidencia {incident.code} ha sido escalada a {incident.escalation_status}"
        notification_type = 'incident_escalated'
    elif action == 'closed':
        title = f"Incidencia Cerrada: {incident.title}"
        message = f"La incidencia {incident.code} ha sido cerrada"
        notification_type = 'incident_closed'
    else:
        return None
    
    # Notificar al usuario asignado
    if incident.assigned_to:
        Notification.create_notification(
            user=incident.assigned_to,
            title=title,
            message=message,
            notification_type=notification_type,
            related_incident=incident,
            is_important=(incident.prioridad == 'Alta')
        )
    
    # Notificar al usuario que realizó la acción (si es diferente)
    if user and user != incident.assigned_to:
        Notification.create_notification(
            user=user,
            title=f"Acción realizada en {incident.code}",
            message=f"Has {action} la incidencia {incident.code}",
            notification_type=notification_type,
            related_incident=incident
        )


def create_document_notification(document, action, user=None):
    """Crear notificación para eventos de documento"""
    if action == 'uploaded':
        title = f"Documento Subido: {document.title}"
        message = f"Se ha subido un nuevo documento: {document.title}"
        notification_type = 'document_uploaded'
    elif action == 'approved':
        title = f"Documento Aprobado: {document.title}"
        message = f"El documento {document.title} ha sido aprobado"
        notification_type = 'document_approved'
    elif action == 'rejected':
        title = f"Documento Rechazado: {document.title}"
        message = f"El documento {document.title} ha sido rechazado"
        notification_type = 'document_rejected'
    else:
        return None
    
    # Notificar al creador del documento
    if document.created_by:
        Notification.create_notification(
            user=document.created_by,
            title=title,
            message=message,
            notification_type=notification_type,
            related_document=document
        )
    
    # Notificar al usuario que realizó la acción (si es diferente)
    if user and user != document.created_by:
        Notification.create_notification(
            user=user,
            title=f"Acción realizada en {document.title}",
            message=f"Has {action} el documento {document.title}",
            notification_type=notification_type,
            related_document=document
        )


def create_system_notification(users, title, message, is_important=False):
    """Crear notificación del sistema para múltiples usuarios"""
    notifications = []
    for user in users:
        notifications.append(Notification(
            user=user,
            title=title,
            message=message,
            notification_type='system_alert',
            is_important=is_important
        ))
    
    # Optimization: Use bulk_create
    if notifications:
        Notification.objects.bulk_create(notifications)
    
    return notifications


def send_email_notification(notification):
    """Enviar notificación por email"""
    try:
        # Verificar si el usuario tiene email habilitado
        preferences = NotificationPreference.get_or_create_preferences(notification.user)
        if not preferences.email_enabled:
            return False
        
        # Verificar tipo de notificación
        if notification.notification_type.startswith('incident') and not preferences.email_incidents:
            return False
        elif notification.notification_type.startswith('document') and not preferences.email_documents:
            return False
        elif notification.notification_type.startswith('workflow') and not preferences.email_workflow:
            return False
        elif notification.notification_type == 'system_alert' and not preferences.email_system:
            return False
        
        # Enviar email
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=True
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False


def send_sms_notification(notification):
    """Enviar notificación por SMS"""
    try:
        # Verificar si el usuario tiene SMS habilitado
        preferences = NotificationPreference.get_or_create_preferences(notification.user)
        if not preferences.sms_enabled or not preferences.sms_phone:
            return False
        
        # Solo enviar SMS para notificaciones críticas
        if preferences.sms_critical_only and not notification.is_important:
            return False
        
        # Aquí se integraría con un servicio de SMS como Twilio
        # Por ahora solo logueamos
        print(f"SMS enviado a {preferences.sms_phone}: {notification.title}")
        return True
    except Exception as e:
        print(f"Error enviando SMS: {e}")
        return False
