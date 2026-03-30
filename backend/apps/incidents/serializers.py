from rest_framework import serializers
from django.utils import timezone
from .models import Incident, IncidentImage, LabReport, IncidentTimeline, IncidentAttachment
from apps.users.serializers import UserSerializer


class IncidentImageSerializer(serializers.ModelSerializer):
    """Serializer for incident images"""
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = IncidentImage
        fields = [
            'id', 'filename', 'path', 'file_size', 'mime_type',
            'exif_json', 'caption_ai', 'analysis_json', 'ai_provider_used',
            'ai_confidence', 'uploaded_by', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class LabReportSerializer(serializers.ModelSerializer):
    """Serializer for lab reports"""
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = LabReport
        fields = [
            'id', 'sample_description', 'tests_performed', 'observations',
            'conclusions', 'expert_name', 'expert_signature_path',
            'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class IncidentTimelineSerializer(serializers.ModelSerializer):
    """Serializer for incident timeline"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = IncidentTimeline
        fields = [
            'id', 'action', 'description', 'user', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class IncidentNestedSerializer(serializers.ModelSerializer):
    """
    Serializer safe for nested use (no annotations required).
    Used in QualityReports to provide incident context.
    """
    created_by = UserSerializer(read_only=True)
    categoria = serializers.SerializerMethodField()
    responsable = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'code', 'created_by', 'provider', 'obra', 'cliente', 'cliente_rut',
            'sku', 'lote', 'fecha_reporte', 'fecha_deteccion', 'hora_deteccion',
            'descripcion', 'categoria', 'subcategoria', 'prioridad', 'estado', 'responsable',
            'escalated_to_quality', 'escalated_to_supplier', 'escalation_date',
            'escalation_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code']
        
    def get_categoria(self, obj):
        return obj.categoria.name if obj.categoria else None
    
    def get_responsable(self, obj):
        """Returns the responsable name, with fallback for edge cases"""
        if obj.responsable:
            if hasattr(obj.responsable, 'name'):
                return obj.responsable.name
            elif isinstance(obj.responsable, int):
                from .models import Responsible
                try:
                    resp = Responsible.objects.get(id=obj.responsable)
                    return resp.name
                except Responsible.DoesNotExist:
                    return f"ID: {obj.responsable}"
        return None



class EscalatedIncidentSerializer(serializers.ModelSerializer):
    """Serializer optimizado para la vista de incidencias escaladas"""
    categoria = serializers.CharField(source='categoria.name', read_only=True)
    description = serializers.CharField(source='descripcion', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'code', 'cliente', 'provider', 'obra', 'categoria',
            'description', 'estado', 'prioridad', 'escalation_date',
            'escalated_to_quality', 'escalated_to_internal_quality',
            'escalated_to_supplier', 'created_at', 'updated_at'
        ]

class IncidentListSerializer(serializers.ModelSerializer):
    """Serializer for incident list view"""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    closed_by = UserSerializer(read_only=True)
    images_count = serializers.IntegerField(read_only=True)
    documents_count = serializers.IntegerField(read_only=True)
    # Return categoria and responsable as names (strings)
    categoria = serializers.SerializerMethodField()
    responsable = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'code', 'created_by', 'provider', 'obra', 'cliente',
            'comuna', 'ciudad',
            'sku', 'lote', 'fecha_reporte', 'fecha_deteccion', 'hora_deteccion',
            'descripcion', 'categoria', 'subcategoria', 'prioridad', 'estado', 'assigned_to',
            'responsable', 'escalated_to_quality', 'escalated_to_internal_quality', 'escalated_to_supplier', 'escalation_date',
            'escalation_reason', 'closed_by', 'closed_at', 'closed_at_stage', 'closure_summary',
            'sla_due_date', 'sla_breached', 'resolution_time_hours',
            'images_count', 'documents_count', 'created_at', 'updated_at',
            # SAP Fields
            'customer_code', 'project_code', 'salesperson', 'sap_call_id', 'sap_doc_num', 'technician_code'
        ]
        read_only_fields = ['id', 'code', 'created_by', 'created_at', 'updated_at']
    
    def get_categoria(self, obj):
        return obj.categoria.name if obj.categoria else None
    
    def get_responsable(self, obj):
        """Returns the responsable name, with fallback for edge cases"""
        if obj.responsable:
            if hasattr(obj.responsable, 'name'):
                return obj.responsable.name
            elif isinstance(obj.responsable, int):
                from .models import Responsible
                try:
                    resp = Responsible.objects.get(id=obj.responsable)
                    return resp.name
                except Responsible.DoesNotExist:
                    return f"ID: {obj.responsable}"
        return None


class IncidentDetailSerializer(serializers.ModelSerializer):
    """Serializer for incident detail view"""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    closed_by = UserSerializer(read_only=True)
    images = IncidentImageSerializer(many=True, read_only=True)
    lab_reports = LabReportSerializer(many=True, read_only=True)
    timeline = IncidentTimelineSerializer(many=True, read_only=True)
    # Return categoria and responsable as names (strings)
    categoria = serializers.SerializerMethodField()
    responsable = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'code', 'created_by', 'provider', 'obra', 'cliente',
            'cliente_rut', 'direccion_cliente', 'comuna', 'ciudad', 'sku', 'lote', 'factura_num',
            'pedido_num', 'fecha_reporte', 'fecha_deteccion', 'hora_deteccion',
            'descripcion', 'acciones_inmediatas', 'categoria', 'subcategoria',
            'prioridad', 'estado', 'assigned_to', 'responsable', 'escalated_to_quality',
            'escalated_to_internal_quality', 'escalated_to_supplier', 'escalation_date', 'escalation_reason',
            'closed_by', 'closed_at', 'closed_at_stage', 'closure_summary', 'closure_attachment',
            'sla_due_date', 'sla_breached', 'first_response_at', 'resolution_time_hours',
            'images', 'lab_reports', 'timeline', 'created_at', 'updated_at',
            # SAP Fields
            'customer_code', 'project_code', 'salesperson', 'sap_call_id', 'sap_doc_num', 'technician_code'
        ]
        read_only_fields = [
            'id', 'code', 'created_by', 'closed_by', 'closed_at', 'closed_at_stage',
            'resolution_time_hours', 'created_at', 'updated_at'
        ]
    
    def get_categoria(self, obj):
        return obj.categoria.name if obj.categoria else None
    
    def get_responsable(self, obj):
        """Returns the responsable name, with fallback for edge cases"""
        if obj.responsable:
            # Normal case: ForeignKey properly resolved
            if hasattr(obj.responsable, 'name'):
                return obj.responsable.name
            # Edge case: might be an ID somehow
            elif isinstance(obj.responsable, int):
                from .models import Responsible
                try:
                    resp = Responsible.objects.get(id=obj.responsable)
                    return resp.name
                except Responsible.DoesNotExist:
                    return f"ID: {obj.responsable}"
        return None


class IncidentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating incidents"""
    # Allow string values for these ForeignKey fields
    categoria = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    responsable = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'code', # Added to return ID/Code after creation
            'provider', 'obra', 'cliente', 'cliente_rut', 'direccion_cliente', 'comuna', 'ciudad',
            'sku', 'lote', 'factura_num', 'pedido_num', 'fecha_deteccion',
            'hora_deteccion', 'descripcion', 'acciones_inmediatas', 'categoria',
            'subcategoria', 'prioridad', 'estado', 'assigned_to', 'responsable',
            'escalated_to_quality', 'escalated_to_internal_quality', 'escalated_to_supplier',
            # SAP Fields
            'customer_code', 'project_code', 'salesperson', 'salesperson_code', 'technician_code', 'sap_call_id', 'sap_doc_num'
        ]
        read_only_fields = ['id', 'code', 'fecha_reporte', 'sap_doc_num']
        extra_kwargs = {
            'fecha_deteccion': {'required': False},
            'hora_deteccion': {'required': False},
            'sku': {'required': False, 'allow_blank': True}
        }
    
    def validate(self, data):
        """Custom validation"""
        from .models import Category, Responsible
        
        # Handle categoria - look up by name or create
        categoria_value = data.get('categoria')
        if categoria_value and isinstance(categoria_value, str):
            categoria_obj, _ = Category.objects.get_or_create(name=categoria_value)
            data['categoria'] = categoria_obj
        elif categoria_value == '' or categoria_value is None:
            data['categoria'] = None
            
        # Handle responsable - look up by name or create
        responsable_value = data.get('responsable')
        if responsable_value and isinstance(responsable_value, str):
            responsable_obj, _ = Responsible.objects.get_or_create(name=responsable_value)
            data['responsable'] = responsable_obj
        elif responsable_value == '' or responsable_value is None:
            data['responsable'] = None
            
        # Sync technician_code if not explicitly provided but available in responsible object
        if data.get('responsable') and not data.get('technician_code'):
            if hasattr(data['responsable'], 'sap_technician_id') and data['responsable'].sap_technician_id:
                data['technician_code'] = data['responsable'].sap_technician_id
        
        # Convert empty strings to None for optional fields
        for field in ['cliente_rut', 'direccion_cliente', 'comuna', 'ciudad', 'sku', 'lote', 'factura_num', 
                     'pedido_num', 'acciones_inmediatas', 'subcategoria', 
                     'fecha_deteccion', 'hora_deteccion']:
            if field in data and data[field] == '':
                data[field] = None
        
        # Convert assigned_to to None if empty string
        if 'assigned_to' in data and data['assigned_to'] == '':
            data['assigned_to'] = None
        
        # Set default values for required fields if not provided
        if 'fecha_deteccion' not in data or data.get('fecha_deteccion') is None:
            data['fecha_deteccion'] = timezone.now().date()
        
        if 'hora_deteccion' not in data or data.get('hora_deteccion') is None:
            data['hora_deteccion'] = timezone.now().time()
            
        return data
    
    def create(self, validated_data):
        # Get user from context if available, otherwise use first admin user
        if 'request' in self.context and hasattr(self.context['request'], 'user'):
            validated_data['created_by'] = self.context['request'].user
        else:
            # Fallback for testing or when context is not available
            from apps.users.models import User
            admin_user = User.objects.filter(role='admin').first()
            if admin_user:
                validated_data['created_by'] = admin_user
            else:
                # Create a default user if none exists
                validated_data['created_by'] = User.objects.first()
        
        # Set fecha_reporte to current time if not provided
        if 'fecha_reporte' not in validated_data:
            validated_data['fecha_reporte'] = timezone.now()
        instance = super().create(validated_data)
        
        # Crear registro en timeline
        from .models import IncidentTimeline
        user = validated_data.get('created_by')
        user_name = user.full_name if user and hasattr(user, 'full_name') else (user.username if user else 'Sistema')
        
        IncidentTimeline.objects.create(
            incident=instance,
            action='created',
            description=f'Incidencia creada por {user_name}',
            user=user
        )
        
        return instance


class IncidentImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading incident images"""
    
    class Meta:
        model = IncidentImage
        fields = ['filename', 'path', 'file_size', 'mime_type', 'exif_json']
    
    def create(self, validated_data):
        validated_data['incident_id'] = self.context['incident_id']
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class LabReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating lab reports"""
    
    class Meta:
        model = LabReport
        fields = [
            'sample_description', 'tests_performed', 'observations',
            'conclusions', 'expert_name', 'expert_signature_path'
        ]
    
    def create(self, validated_data):
        validated_data['incident_id'] = self.context['incident_id']
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class IncidentStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating incident status"""
    estado = serializers.ChoiceField(choices=Incident.STATUS_CHOICES)
    assigned_to = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(required=False, help_text="Descripción del cambio")
    
    def validate_assigned_to(self, value):
        if value is not None:
            from apps.users.models import User
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Usuario no encontrado")
        return value


class IncidentCloseSerializer(serializers.Serializer):
    """Serializer for closing incidents with required summary"""
    stage = serializers.ChoiceField(
        choices=['incidencia', 'reporte_visita', 'calidad', 'proveedor'],
        help_text="Etapa donde se cierra la incidencia"
    )
    closure_summary = serializers.CharField(
        help_text="Resumen obligatorio de acciones, conclusiones y decisiones tomadas",
        min_length=10
    )
    closure_attachment = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Ruta del archivo adjunto con información de cierre (opcional)"
    )
    technician_code = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Código del técnico en SAP para actualizar al cierre (opcional)"
    )


class IncidentAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for incident attachments"""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = IncidentAttachment
        fields = [
            'id', 'file_name', 'file_path', 'file_size',
            'file_type', 'mime_type', 'description', 'uploaded_by_username',
            'uploaded_at', 'is_public'
        ]
        read_only_fields = ['id', 'uploaded_by_username', 'uploaded_at']


class IncidentAttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating incident attachments"""
    
    class Meta:
        model = IncidentAttachment
        fields = [
            'file_name', 'file_path', 'file_size', 'file_type',
            'mime_type', 'description', 'is_public'
        ]
