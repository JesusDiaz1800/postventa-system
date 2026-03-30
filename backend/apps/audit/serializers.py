from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AuditLog, DeletedItem
from django.utils import timezone


class UserSerializer(serializers.Serializer):
    """Serializer para información básica de usuario (Manual para evitar crash de introspección)"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para registros de auditoría"""
    user = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    formatted_timestamp = serializers.ReadOnlyField()
    action_icon = serializers.ReadOnlyField()
    action_color = serializers.ReadOnlyField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'action_display', 'description', 
            'user', 'ip_address', 'details', 
            'timestamp', # Use default ISO format for machine readability
            'formatted_timestamp', # Keep for legacy/display if needed, but frontend should use timestamp
            'action_icon', 'action_color'
        ]
        read_only_fields = ['id', 'timestamp']


class DeletedItemSerializer(serializers.ModelSerializer):
    """Serializer para elementos eliminados"""
    deleted_by_username = serializers.CharField(source='deleted_by.username', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = DeletedItem
        fields = [
            'id', 'original_id', 'model_name', 'app_label', 
            'object_repr', 'deleted_at', 'deleted_by', 'deleted_by_username',
            'restore_deadline', 'days_remaining'
        ]
        read_only_fields = fields
        
    def get_days_remaining(self, obj):
        now = timezone.now()
        if obj.restore_deadline > now:
            delta = obj.restore_deadline - now
            return delta.days
        return 0

class DeletedItemRestoreSerializer(serializers.Serializer):
    """Serializer para la acción de restaurar"""
    restore_relations = serializers.BooleanField(default=False, help_text="Intentar restaurar relaciones anidadas (experimental)")
    
    def restore(self, deleted_item):
        """Lógica de restauración optimizada"""
        try:
            from django.apps import apps
            import json
            from django.core import serializers
            
            # 1. Obtener modelo
            try:
                ModelClass = apps.get_model(deleted_item.app_label, deleted_item.model_name)
            except LookupError:
                raise serializers.ValidationError(f"El modelo {deleted_item.app_label}.{deleted_item.model_name} ya no existe.")
            
            # 2. Verificar si ya existe un objeto con ese ID
            existing_obj = ModelClass.objects.filter(pk=deleted_item.original_id).first()
            if existing_obj:
                # Caso especial: Soft Delete (Incidencia Cancelada)
                # Si el objeto existe y es una incidencia cancelada, simplemente la restauramos
                if deleted_item.model_name == 'incident' and hasattr(existing_obj, 'estado') and existing_obj.estado == 'cancelada':
                    existing_obj.estado = 'abierta'
                    # Limpiamos campos de cierre si existen
                    if hasattr(existing_obj, 'closure_summary'):
                        existing_obj.closure_summary = ""
                    if hasattr(existing_obj, 'closed_at'):
                        existing_obj.closed_at = None
                    if hasattr(existing_obj, 'closed_by'):
                        existing_obj.closed_by = None
                    
                    existing_obj.save()
                    
                    # Registrar en timeline
                    try:
                        from apps.incidents.models import IncidentTimeline
                        IncidentTimeline.objects.create(
                            incident=existing_obj,
                            user=None, # O el usuario del request si estuviera disponible, pero aquí usamos None o sistema
                            action='restored',
                            description="Incidencia restaurada desde la papelera de reciclaje."
                        )
                    except:
                        pass
                        
                    # Eliminar backup tras restaurar
                    deleted_item.delete()
                    return existing_obj
                
                raise serializers.ValidationError(f"Ya existe un objeto {deleted_item.model_name} con ID {deleted_item.original_id}. No se puede restaurar.")
                
            # 3. Deserializar
            serialized_data = deleted_item.serialized_data
            
            # Manejar si serialized_data es string o dict/list
            if isinstance(serialized_data, str):
                json_str = serialized_data
            else:
                json_str = json.dumps(serialized_data)
                
            # Método alternativo más seguro: usar deserializer de Django
            # Django serializer devuelve una lista de DeserializedObject
            # Si serialized_data es una lista de objetos serializados (formato django default):
            if isinstance(serialized_data, list) and len(serialized_data) > 0:
                 json_str = json.dumps(serialized_data)
            # Si es un dict (quizas custom), hay que ver. Asumimos formato standard Django serializers.serialize('json', [obj])
            
            # Intentar deserializar
            deserialized_objects = list(serializers.deserialize('json', json_str))
            
            if not deserialized_objects:
                raise serializers.ValidationError("No se pudo interpretar la data de respaldo.")
                
            obj = deserialized_objects[0].object
            obj.save(force_insert=True) # Forzar insert con el ID original
            
            # Eliminar backup tras restaurar
            deleted_item.delete()
            
            return obj
                 
        except Exception as e:
            # Re-raise validation errors or wrap others
            if isinstance(e, serializers.ValidationError):
                raise e
            raise serializers.ValidationError(f"Error técnico al restaurar: {str(e)}")