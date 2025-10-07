from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, NotificationPreference
from apps.incidents.models import Incident
from apps.documents.models import Document

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para información básica de usuario"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer para información básica de incidencia.

    Note: the Incident model does not have fields named `title`, `status` or
    `priority` in this project. Map to actual model fields to avoid DRF model
    introspection errors.
    """
    class Meta:
        model = Incident
        fields = ['id', 'code', 'cliente', 'estado', 'prioridad']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer para información básica de documento.

    The Document model does not expose a `status` field; expose document_type
    and a small set of stable fields instead.
    """
    class Meta:
        model = Document
        fields = ['id', 'title', 'document_type', 'is_final']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    user = UserSerializer(read_only=True)
    related_user = UserSerializer(read_only=True)
    # Notification stores related_incident_id and related_document_id as integers.
    # Use SerializerMethodField to avoid DRF trying to resolve a non-existent FK.
    related_incident = serializers.SerializerMethodField()
    related_document = serializers.SerializerMethodField()

    # Campos calculados
    time_ago = serializers.SerializerMethodField()
    notification_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'notification_type_display',
            'is_read', 'is_important', 'created_at', 'read_at', 'time_ago',
            'user', 'related_user', 'related_incident', 'related_document', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']
    
    def get_time_ago(self, obj):
        """Calcular tiempo transcurrido desde la creación"""
        from django.utils import timezone
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"{diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "Ahora"
    
    def get_notification_type_display(self, obj):
        """Obtener display del tipo de notificación"""
        return dict(Notification.NOTIFICATION_TYPES).get(obj.notification_type, obj.notification_type)

    def get_related_incident(self, obj):
        """Return nested incident data if related_incident_id is present."""
        try:
            if obj.related_incident_id:
                incident = Incident.objects.filter(id=obj.related_incident_id).first()
                if incident:
                    return IncidentSerializer(incident).data
        except Exception:
            pass
        return None

    def get_related_document(self, obj):
        try:
            if obj.related_document_id:
                document = Document.objects.filter(id=obj.related_document_id).first()
                if document:
                    return DocumentSerializer(document).data
        except Exception:
            pass
        return None


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones"""
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'is_important',
            'related_incident_id', 'related_document_id', 'related_user', 'metadata'
        ]
    
    def create(self, validated_data):
        """Crear notificación para el usuario autenticado"""
        validated_data['user'] = self.context['request'].user
        # Map incoming keys to underlying model fields if callers use "related_incident"/"related_document".
        if 'related_incident' in validated_data:
            validated_data['related_incident_id'] = validated_data.pop('related_incident')
        if 'related_document' in validated_data:
            validated_data['related_document_id'] = validated_data.pop('related_document')
        return super().create(validated_data)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer para preferencias de notificación"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = NotificationPreference
        # Align fields with the NotificationPreference model actual attributes.
        fields = [
            'id', 'user', 'email_enabled', 'push_enabled', 'web_enabled',
            'incident_created', 'incident_updated', 'incident_escalated', 'incident_closed',
            'document_uploaded', 'document_approved', 'document_rejected',
            'workflow_step_completed', 'workflow_approval_required', 'system_alert',
            'user_assigned', 'deadline_approaching', 'deadline_exceeded',
            'priority_threshold', 'notification_start_time', 'notification_end_time',
            'quiet_hours', 'weekend_notifications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']



class NotificationStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de notificaciones"""
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    important_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    notifications_today = serializers.IntegerField()
    notifications_this_week = serializers.IntegerField()


class NotificationDigestSerializer(serializers.Serializer):
    """Serializer para resumen de notificaciones"""
    period = serializers.CharField()
    total_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    important_count = serializers.IntegerField()
    notifications = NotificationSerializer(many=True)
    summary = serializers.DictField()


class NotificationBulkActionSerializer(serializers.Serializer):
    """Serializer para acciones masivas en notificaciones"""
    action = serializers.ChoiceField(choices=['mark_read', 'mark_unread', 'delete'])
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    def validate_notification_ids(self, value):
        """Validar que las notificaciones pertenezcan al usuario"""
        user = self.context['request'].user
        valid_ids = Notification.objects.filter(
            id__in=value, 
            user=user
        ).values_list('id', flat=True)
        
        if len(valid_ids) != len(value):
            raise serializers.ValidationError(
                "Algunas notificaciones no pertenecen al usuario actual"
            )
        
        return value


class NotificationSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de notificaciones"""
    query = serializers.CharField(required=False, allow_blank=True)
    notification_type = serializers.CharField(required=False, allow_blank=True)
    is_read = serializers.BooleanField(required=False)
    is_important = serializers.BooleanField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    ordering = serializers.ChoiceField(
        choices=['created_at', '-created_at', 'title', '-title'],
        required=False,
        default='-created_at'
    )
