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


class IncidentListSerializer(serializers.ModelSerializer):
    """Serializer for incident list view"""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    closed_by = UserSerializer(read_only=True)
    images_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'code', 'created_by', 'provider', 'obra', 'cliente',
            'sku', 'lote', 'fecha_reporte', 'fecha_deteccion', 'hora_deteccion',
            'descripcion', 'categoria', 'subcategoria', 'prioridad', 'estado', 'assigned_to',
            'responsable', 'escalated_to_quality', 'escalated_to_supplier', 'escalation_date',
            'escalation_reason', 'closed_by', 'closed_at', 'images_count', 'documents_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_by', 'created_at', 'updated_at']
    
    def get_images_count(self, obj):
        return obj.images.count()
    
    def get_documents_count(self, obj):
        # Contar documentos de todas las tablas de documentos existentes
        try:
            from apps.documents.models import VisitReport, SupplierReport, LabReport
            
            visit_count = 0
            supplier_count = 0
            lab_count = 0
            
            # Intentar filtrar por related_incident, si la columna no existe, devolver 0
            try:
                visit_count = VisitReport.objects.filter(related_incident=obj).count()
            except Exception:
                pass
            
            try:
                supplier_count = SupplierReport.objects.filter(related_incident=obj).count()
            except Exception:
                pass
            
            try:
                lab_count = LabReport.objects.filter(related_incident=obj).count()
            except Exception:
                pass
            
            return visit_count + supplier_count + lab_count
        except Exception:
            return 0


class IncidentDetailSerializer(serializers.ModelSerializer):
    """Serializer for incident detail view"""
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    closed_by = UserSerializer(read_only=True)
    images = IncidentImageSerializer(many=True, read_only=True)
    lab_reports = LabReportSerializer(many=True, read_only=True)
    timeline = IncidentTimelineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'code', 'created_by', 'provider', 'obra', 'cliente',
            'cliente_rut', 'direccion_cliente', 'sku', 'lote', 'factura_num',
            'pedido_num', 'fecha_reporte', 'fecha_deteccion', 'hora_deteccion',
            'descripcion', 'acciones_inmediatas', 'categoria', 'subcategoria',
            'prioridad', 'estado', 'assigned_to', 'responsable', 'escalated_to_quality',
            'escalated_to_supplier', 'escalation_date', 'escalation_reason',
            'closed_by', 'closed_at', 
            'images', 'lab_reports', 'timeline', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'code', 'created_by', 'closed_by', 'closed_at',
            'created_at', 'updated_at'
        ]


class IncidentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating incidents"""
    
    class Meta:
        model = Incident
        fields = [
            'provider', 'obra', 'cliente', 'cliente_rut', 'direccion_cliente',
            'sku', 'lote', 'factura_num', 'pedido_num', 'fecha_deteccion',
            'hora_deteccion', 'descripcion', 'acciones_inmediatas', 'categoria',
            'subcategoria', 'prioridad', 'estado', 'assigned_to', 'responsable',
        ]
        read_only_fields = ['fecha_reporte']
        extra_kwargs = {
            'fecha_deteccion': {'required': False},
            'hora_deteccion': {'required': False},
            'sku': {'required': False, 'allow_blank': True}
        }
    
    def validate(self, data):
        """Custom validation"""
        # Convert empty strings to None for optional fields
        for field in ['cliente_rut', 'direccion_cliente', 'sku', 'lote', 'factura_num', 
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
        return super().create(validated_data)


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
    """Serializer for closing incidents"""
    description = serializers.CharField(help_text="Descripción del cierre")
    actions_taken = serializers.CharField(help_text="Acciones tomadas para resolver la incidencia")


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
