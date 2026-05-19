"""
Serializers para gestión de documentos con trazabilidad
"""
from rest_framework import serializers
from .models import (
    DocumentTemplate, Document, DocumentVersion, DocumentConversion,
    DocumentAttachment
)
from apps.visits.models import VisitReport
from apps.users.serializers import UserSerializer
from apps.sap_integration.master_data_service import MasterDataService

# ==================== SERIALIZERS EXISTENTES ====================

class DocumentTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'name', 'template_type', 'description', 'docx_template_path',
            'is_active', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class DocumentListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'document_type_display', 'version',
            'is_final', 'created_by_name', 'created_at', 'updated_at'
        ]

class DocumentAttachmentListSerializer(serializers.ModelSerializer):
    """Serializer para listar adjuntos de incidencia (modelo Document)"""
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'filename', 'title', 'description', 'size', 
            'created_at', 'created_by_name', 'is_public', 'document_type'
        ]

class DocumentDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'document_type_display', 'version',
            'docx_path', 'pdf_path', 'content_html', 'placeholders_data',
            'notes', 'is_final', 'created_by_name',
            'created_at', 'updated_at'
        ]

class DocumentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'content_html',
            'placeholders_data', 'notes', 'is_final'
        ]

class DocumentGenerateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    placeholders_data = serializers.JSONField(default=dict)
    generate_pdf = serializers.BooleanField(default=True)

class DocumentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['content_html', 'notes']

class DocumentConvertSerializer(serializers.Serializer):
    source_format = serializers.CharField(max_length=10)
    target_format = serializers.CharField(max_length=10)

class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'version_number', 'docx_path', 'pdf_path', 'content_html',
            'change_notes', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']

class DocumentConversionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = DocumentConversion
        fields = [
            'id', 'source_format', 'target_format', 'status',
            'source_file_path', 'target_file_path', 'error_message',
            'created_by_name', 'created_at', 'completed_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'completed_at']

# ==================== NUEVOS SERIALIZERS PARA TRAZABILIDAD ====================

class DocumentAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    view_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentAttachment
        fields = [
            'id', 'document_type', 'document_id', 'file', 'filename', 
            'file_type', 'file_size', 'description', 'uploaded_by_name', 
            'uploaded_at', 'view_url'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']

    def get_view_url(self, obj):
        """Construye la URL de visualización para el frontend"""
        # Mapear document_type de vuelta a report_type de la URL
        type_map = {
            'visit_report': 'visit',
            'lab_report': 'lab',
            'supplier_report': 'supplier'
        }
        report_type = type_map.get(obj.document_type, 'visit')
        
        # Devolver ruta relativa que el frontend completará con API_BASE_URL
        return f"/documents/report-attachments/{obj.document_id}/{report_type}/{obj.id}/view/"

# NOTE: VisitReportSerializer and other related serializers are now managed in apps.visits.serializers