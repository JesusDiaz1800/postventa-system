"""
Serializers para reportes de calidad
"""
from rest_framework import serializers
from .models import QualityReport
# from apps.incidents.serializers import IncidentListSerializer
# from apps.users.serializers import UserSerializer

class QualityReportSerializer(serializers.ModelSerializer):
    """
    Serializer para reportes de calidad
    """
    # related_incident = IncidentListSerializer(read_only=True)
    # created_by = UserSerializer(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    related_incident_code = serializers.CharField(source='related_incident.code', read_only=True)
    
    # URLs de descarga de archivos
    download_url = serializers.SerializerMethodField()
    has_document = serializers.SerializerMethodField()
    
    def get_download_url(self, obj):
        """Genera URL de descarga para el archivo del reporte"""
        if obj.pdf_path:
            # Extraer nombre del archivo de la ruta
            import os
            filename = os.path.basename(obj.pdf_path)
            return f'/api/documents/open/quality-report/{obj.related_incident.id}/{filename}'
        elif obj.docx_path:
            # Extraer nombre del archivo de la ruta
            import os
            filename = os.path.basename(obj.docx_path)
            return f'/api/documents/open/quality-report/{obj.related_incident.id}/{filename}'
        return None
    
    def get_has_document(self, obj):
        """Indica si el reporte tiene un documento adjunto"""
        return bool(obj.pdf_path or obj.docx_path)
    
    class Meta:
        model = QualityReport
        fields = [
            'id', 'report_type', 'report_number', 'related_incident', 'related_incident_code',
            'title', 'date_created', 'created_by', 'created_by_username',
            'executive_summary', 'problem_description', 'root_cause_analysis',
            'corrective_actions', 'preventive_measures', 'recommendations',
            'technical_details', 'internal_notes', 'status',
            'pdf_path', 'docx_path', 'created_at', 'updated_at',
            'download_url', 'has_document'
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
            'report_type', 'related_incident_id', 'title',
            'executive_summary', 'problem_description', 'root_cause_analysis',
            'corrective_actions', 'preventive_measures', 'recommendations',
            'technical_details', 'internal_notes', 'status'
        ]
    
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
