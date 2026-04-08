"""
Serializers para reportes de calidad
"""
from rest_framework import serializers
from .models import QualityReport
from apps.incidents.serializers import IncidentNestedSerializer
# from apps.users.serializers import UserSerializer

class QualityReportSerializer(serializers.ModelSerializer):
    """
    Serializer para reportes de calidad con datos de incidencia expandidos
    """
    # Campos del creador
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    # Datos de incidencia expandidos para las tablas del frontend
    related_incident_code = serializers.CharField(source='related_incident.code', read_only=True)
    incident_code = serializers.CharField(source='related_incident.code', read_only=True)
    cliente = serializers.CharField(source='related_incident.cliente', read_only=True)
    provider = serializers.CharField(source='related_incident.provider', read_only=True)
    obra = serializers.CharField(source='related_incident.obra', read_only=True)
    categoria = serializers.SerializerMethodField()
    subcategoria = serializers.CharField(source='related_incident.subcategoria', read_only=True)
    incident_status = serializers.CharField(source='related_incident.estado', read_only=True)
    incident_id = serializers.IntegerField(source='related_incident.id', read_only=True)
    
    # Campo anidado completo para modales (requiere expand=incident)
    incident = IncidentNestedSerializer(source='related_incident', read_only=True)
    
    # URLs de descarga de archivos
    download_url = serializers.SerializerMethodField()
    has_document = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    
    def get_categoria(self, obj):
        """Obtiene el nombre de la categoría de la incidencia"""
        if obj.related_incident and obj.related_incident.categoria:
            return str(obj.related_incident.categoria)
        return None
    
    def get_filename(self, obj):
        """Obtiene el nombre del archivo"""
        if obj.pdf_path:
            import os
            return os.path.basename(obj.pdf_path)
        elif obj.docx_path:
            import os
            return os.path.basename(obj.docx_path)
        return None
    
    def get_download_url(self, obj):
        """Genera URL de descarga para el archivo del reporte"""
        # Usar la vista dedicada con fallback robusto
        return f'/api/documents/quality-reports/{obj.id}/download/'
    
    def get_has_document(self, obj):
        """Indica si el reporte tiene un documento adjunto"""
        return bool(obj.pdf_path or obj.docx_path)
    
    class Meta:
        model = QualityReport
        fields = [
            'id', 'report_type', 'report_number', 'related_incident', 'related_incident_code',
            # Campos de incidencia expandidos
            'incident_id', 'incident_code', 'incident', 'cliente', 'provider', 'obra', 
            'categoria', 'subcategoria', 'incident_status',
            # Campos del reporte
            'title', 'date_created', 'created_by', 'created_by_username',
            'executive_summary', 'problem_description', 'root_cause_analysis',
            'corrective_actions', 'preventive_measures', 'recommendations',
            'technical_details', 'internal_notes', 'status',
            'pdf_path', 'docx_path', 'created_at', 'updated_at',
            'download_url', 'has_document', 'filename'
        ]
        read_only_fields = ['id', 'report_number', 'created_at', 'updated_at']

class QualityReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear reportes de calidad
    """
    related_incident_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = QualityReport
        fields = [
            'id', 'report_type', 'related_incident_id', 'title',
            'executive_summary', 'problem_description', 'root_cause_analysis',
            'corrective_actions', 'preventive_measures', 'recommendations',
            'technical_details', 'internal_notes', 'status'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        incident_id = validated_data.pop('related_incident_id')
        from apps.incidents.models import Incident
        
        try:
            incident = Incident.objects.get(id=incident_id)
        except Incident.DoesNotExist:
            raise serializers.ValidationError("Incidencia no encontrada")
        
        validated_data['related_incident'] = incident
        validated_data['created_by'] = self.context['request'].user
        
        return super().create(validated_data)

class QualityReportUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar reportes de calidad
    """
    
    class Meta:
        model = QualityReport
        fields = [
            'title', 'executive_summary', 'problem_description', 
            'root_cause_analysis', 'corrective_actions', 'preventive_measures',
            'recommendations', 'technical_details', 'internal_notes', 'status'
        ]
