"""
Serializers para gestión de documentos con trazabilidad
"""
from rest_framework import serializers
from .models import (
    DocumentTemplate, Document, DocumentVersion, DocumentConversion,
    VisitReport, LabReport, SupplierReport, DocumentAttachment
)
from apps.incidents.serializers import IncidentListSerializer
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
    incident = IncidentListSerializer(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'document_type_display', 'version',
            'is_final', 'created_by_name', 'incident', 'created_at', 'updated_at'
        ]

class DocumentDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    incident = IncidentListSerializer(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'document_type', 'document_type_display', 'version',
            'docx_path', 'pdf_path', 'content_html', 'placeholders_data',
            'notes', 'is_final', 'created_by_name', 'incident',
            'created_at', 'updated_at'
        ]

class DocumentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'incident', 'content_html',
            'placeholders_data', 'notes', 'is_final'
        ]

class DocumentGenerateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    incident_id = serializers.IntegerField(required=False, allow_null=True)
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
    
    class Meta:
        model = DocumentAttachment
        fields = [
            'id', 'document_type', 'document_id', 'file', 'filename', 
            'file_type', 'file_size', 'description', 'uploaded_by_name', 
            'uploaded_at'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at']

class VisitReportSerializer(serializers.ModelSerializer):
    related_incident = IncidentListSerializer(read_only=True)
    related_incident_id = serializers.IntegerField(write_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)
    visit_reason_display = serializers.SerializerMethodField()
    def get_visit_reason_display(self, obj):
        if not obj.visit_reason:
            return ""
        return MasterDataService.get_problem_type_name(obj.visit_reason)
    
    class Meta:
        model = VisitReport
        fields = [
            'id', 'report_number', 'order_number', 'visit_date',
            'related_incident', 'related_incident_id', 'project_name', 
            'project_id', 'client_name', 'client_rut', 'address',
            'construction_company', 'salesperson', 'technician', 'technician_id',
            'installer', 'installer_phone', 'commune', 'city',
            'visit_reason', 'machine_data', 'wall_observations',
            'matrix_observations', 'slab_observations', 'storage_observations',
            'pre_assembled_observations', 'exterior_observations', 
            'general_observations', 'status', 'created_by_name',
            'created_at', 'updated_at', 'technician_signature',
            'installer_signature', 'attachments', 'sap_call_id', 'visit_reason_display'
        ]
        read_only_fields = ['report_number', 'created_by', 'created_at', 'updated_at']

class VisitReportListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para la lista de reportes de visita"""
    related_incident = IncidentListSerializer(read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    # Campos de la incidencia para mostrar en la tabla
    incident_code = serializers.CharField(source='related_incident.code', read_only=True)
    provider = serializers.CharField(source='related_incident.provider', read_only=True)
    categoria = serializers.CharField(source='related_incident.categoria.name', read_only=True)
    subcategoria = serializers.CharField(source='related_incident.subcategoria', read_only=True)
    escalated_to_quality = serializers.BooleanField(source='related_incident.escalated_to_quality', read_only=True)
    
    # URLs de descarga de archivos
    download_url = serializers.SerializerMethodField()
    has_document = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    visit_reason_display = serializers.SerializerMethodField()

    def get_visit_reason_display(self, obj):
        return MasterDataService.get_problem_type_name(obj.visit_reason)
    
    def get_download_url(self, obj):
        """Genera URL de descarga para el archivo del reporte"""
        if obj.pdf_file:  # FileField - PDF generado por signal
            return f'/api/documents/visit-reports/{obj.id}/download/'
        elif obj.pdf_path:  # CharField - PDF legacy/manual
            # Extraer nombre del archivo de la ruta
            import os
            filename = os.path.basename(obj.pdf_path)
            return f'/api/documents/open/visit-report/{obj.related_incident.id}/{filename}'
        elif obj.docx_path:
            # Extraer nombre del archivo de la ruta
            import os
            filename = os.path.basename(obj.docx_path)
            return f'/api/documents/open/visit-report/{obj.related_incident.id}/{filename}'
        return None
    
    def get_has_document(self, obj):
        """Indica si el reporte tiene un documento adjunto"""
        return bool(obj.pdf_file or obj.pdf_path or obj.docx_path)

    
    def get_attachment_count(self, obj):
        """Cuenta las imágenes/archivos adjuntos al reporte"""
        try:
            from .models import DocumentAttachment
            return DocumentAttachment.objects.filter(
                document_id=obj.id,
                document_type='visit_report'
            ).count()
        except:
            return 0
    
    class Meta:
        model = VisitReport
        fields = [
            'id', 'report_number', 'order_number', 'visit_date',
            'related_incident', 'project_name', 'client_name', 'address',
            'salesperson', 'status', 'created_by_name', 'created_at',
            'incident_code', 'provider', 'categoria', 'subcategoria',
            'download_url', 'has_document', 'pdf_path', 'escalated_to_quality',
            'attachment_count', 'visit_reason_display'
        ]

class VisitReportCreateSerializer(serializers.ModelSerializer):
    related_incident_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    order_number = serializers.CharField(required=False, allow_blank=True)
    report_number = serializers.CharField(required=False, allow_blank=True)  # Permitir pre-asignación
    
    class Meta:
        model = VisitReport
        fields = [
            'id', 'report_number', 'order_number', 'visit_date', 'related_incident_id', 'project_name',
            'project_id', 'client_name', 'client_rut', 'address',
            'construction_company', 'salesperson', 'technician', 'technician_id',
            'installer', 'installer_phone', 'commune', 'city',
            'visit_reason', 'machine_data', 'materials_data', 'wall_observations',
            'matrix_observations', 'slab_observations', 'storage_observations',
            'pre_assembled_observations', 'exterior_observations',
            'general_observations', 'status', 'sap_call_id'
        ]
        extra_kwargs = {
            'visit_date': {'required': False, 'allow_null': True},
            'status': {'required': False, 'allow_blank': True},
            'project_name': {'required': False, 'allow_blank': True},
            'project_id': {'required': False, 'allow_blank': True, 'allow_null': True},
            'client_name': {'required': False, 'allow_blank': True},
            'client_rut': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'construction_company': {'required': False, 'allow_blank': True},
            'salesperson': {'required': False, 'allow_blank': True},
            'sap_call_id': {'required': False, 'allow_null': True},
            'technician': {'required': False, 'allow_blank': True},
            'technician_id': {'required': False, 'allow_null': True},
            'installer': {'required': False, 'allow_blank': True},
            'installer_phone': {'required': False, 'allow_blank': True},
            'commune': {'required': False, 'allow_blank': True},
            'city': {'required': False, 'allow_blank': True},
            'visit_reason': {'required': False, 'allow_blank': True},
            'machine_data': {'required': False, 'allow_null': True},
            'materials_data': {'required': False, 'allow_null': True},
            'wall_observations': {'required': False, 'allow_blank': True},
            'matrix_observations': {'required': False, 'allow_blank': True},
            'slab_observations': {'required': False, 'allow_blank': True},
            'storage_observations': {'required': False, 'allow_blank': True},
            'pre_assembled_observations': {'required': False, 'allow_blank': True},
            'exterior_observations': {'required': False, 'allow_blank': True},
            'general_observations': {'required': False, 'allow_blank': True},
        }

    def validate_machine_data(self, value):
        import json
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {} # Return empty dict on error
        return value

    def validate_materials_data(self, value):
        import json
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [] # Return empty list on error
        return value


class LabReportSerializer(serializers.ModelSerializer):
    related_incident = IncidentListSerializer(read_only=True)
    related_incident_id = serializers.IntegerField(write_only=True)
    related_visit_report = VisitReportSerializer(read_only=True)
    related_visit_report_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = LabReport
        fields = [
            'id', 'report_number', 'form_number', 'request_date',
            'related_incident', 'related_incident_id', 'related_visit_report',
            'related_visit_report_id', 'applicant', 'client', 'description',
            'project_background', 'tests_performed', 'comments', 'conclusions',
            'recommendations', 'status', 'created_by_name', 'created_at',
            'updated_at', 'technical_expert_signature', 'technical_expert_name',
            'attachments'
        ]
        read_only_fields = ['report_number', 'created_by', 'created_at', 'updated_at']

class LabReportCreateSerializer(serializers.ModelSerializer):
    related_incident_id = serializers.IntegerField(write_only=True)
    tests_performed = serializers.JSONField(required=False, default=dict)
    
    class Meta:
        model = LabReport
        fields = [
            'form_number', 'request_date', 'related_incident_id', 'related_visit_report',
            'applicant', 'client', 'description', 'project_background',
            'tests_performed', 'comments', 'conclusions', 'recommendations', 'status'
        ]
        extra_kwargs = {
            'applicant': {'required': False, 'allow_blank': True},
            'client': {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
            'project_background': {'required': False, 'allow_blank': True},
            'comments': {'required': False, 'allow_blank': True},
            'conclusions': {'required': False, 'allow_blank': True},
            'recommendations': {'required': False, 'allow_blank': True},
        }
    
    def validate_tests_performed(self, value):
        """Validar que tests_performed sea un diccionario válido"""
        if value is None:
            return {}
        if not isinstance(value, dict):
            return {}
        return value

class SupplierReportSerializer(serializers.ModelSerializer):
    related_incident = IncidentListSerializer(read_only=True)
    related_incident_id = serializers.IntegerField(write_only=True)
    related_lab_report = LabReportSerializer(read_only=True)
    related_lab_report_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupplierReport
        fields = [
            'id', 'report_number', 'report_date', 'related_incident',
            'related_incident_id', 'related_lab_report', 'related_lab_report_id',
            'supplier_name', 'supplier_contact', 'supplier_email', 'subject',
            'introduction', 'problem_description', 'technical_analysis',
            'recommendations', 'expected_improvements', 'status', 'sent_date',
            'created_by_name', 'created_at', 'updated_at', 'attachments'
        ]
        read_only_fields = ['report_number', 'created_by', 'created_at', 'updated_at']

class SupplierReportCreateSerializer(serializers.ModelSerializer):
    related_incident_id = serializers.IntegerField(write_only=True)
    related_lab_report_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    technical_details = serializers.JSONField(write_only=True, required=False) # Campo virtual para recibir JSON estructurado
    
    class Meta:
        model = SupplierReport
        fields = [
            'report_date', 'related_incident_id', 'related_lab_report_id',
            'supplier_name', 'supplier_contact', 'supplier_email', 'subject',
            'introduction', 'problem_description', 'technical_analysis',
            'recommendations', 'expected_improvements', 'status',
            'technical_details' # Incluir el campo virtual
        ]
        extra_kwargs = {
            'report_date': {'required': False},
            'status': {'required': False, 'allow_blank': True},
            'supplier_name': {'required': False, 'allow_blank': True},
            'supplier_contact': {'required': False, 'allow_blank': True},
            'supplier_email': {'required': False, 'allow_blank': True},
            'subject': {'required': False, 'allow_blank': True},
            'introduction': {'required': False, 'allow_blank': True},
            'problem_description': {'required': False, 'allow_blank': True},
            'technical_analysis': {'required': False, 'allow_blank': True},
            'recommendations': {'required': False, 'allow_blank': True},
            'expected_improvements': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):
        technical_details = validated_data.pop('technical_details', None)
        # Si viene JSON estructurado, guardarlo como string en technical_analysis
        if technical_details:
            import json
            validated_data['technical_analysis'] = json.dumps(technical_details)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        technical_details = validated_data.pop('technical_details', None)
        if technical_details:
            import json
            validated_data['technical_analysis'] = json.dumps(technical_details)
        return super().update(instance, validated_data)

class SupplierReportListSerializer(serializers.ModelSerializer):
    """
    Serializer optimizado para lista de reportes de proveedor con datos de incidencia expandidos
    """
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    # Datos de incidencia expandidos para acceso directo en frontend
    incident_id = serializers.IntegerField(source='related_incident.id', read_only=True)
    incident_code = serializers.CharField(source='related_incident.code', read_only=True)
    cliente = serializers.CharField(source='related_incident.cliente', read_only=True)
    provider = serializers.CharField(source='related_incident.provider', read_only=True)
    obra = serializers.CharField(source='related_incident.obra', read_only=True)
    sku = serializers.CharField(source='related_incident.sku', read_only=True)
    categoria = serializers.SerializerMethodField()
    subcategoria = serializers.CharField(source='related_incident.subcategoria', read_only=True)
    incident_status = serializers.CharField(source='related_incident.estado', read_only=True)
    
    # URLs y estado de documentos
    download_url = serializers.SerializerMethodField()
    has_document = serializers.SerializerMethodField()
    
    def get_categoria(self, obj):
        if obj.related_incident and obj.related_incident.categoria:
            return str(obj.related_incident.categoria)
        return None
    
    def get_download_url(self, obj):
        # Usar la vista específica que tiene lógica de fallback robusta
        return f'/api/documents/supplier-reports/{obj.id}/download/'
    
    def get_has_document(self, obj):
        return bool(obj.pdf_path)
    
    # Include attachments
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupplierReport
        fields = [
            'id', 'report_number', 'report_date', 'related_incident',
            # Campos de incidencia expandidos
            'incident_id', 'incident_code', 'cliente', 'provider', 'obra', 
            'sku', 'categoria', 'subcategoria', 'incident_status',
            # Campos del reporte
            'supplier_name', 'supplier_contact', 'supplier_email', 'subject',
            'introduction', 'problem_description', 'technical_analysis',
            'recommendations', 'expected_improvements', 'status', 'sent_date',
            'created_by_name', 'created_at', 'updated_at',
            'pdf_path', 'download_url', 'has_document',
            'attachments'
        ]

class DocumentWorkflowSerializer(serializers.Serializer):
    """
    Serializer para mostrar el workflow completo de un incidente
    """
    incident = IncidentListSerializer(read_only=True)
    visit_reports = VisitReportSerializer(many=True, read_only=True)
    lab_reports = LabReportSerializer(many=True, read_only=True)
    supplier_reports = SupplierReportSerializer(many=True, read_only=True)
    
    workflow_status = serializers.SerializerMethodField()
    
    def get_workflow_status(self, obj):
        incident = obj['incident']
        visit_reports = obj['visit_reports']
        lab_reports = obj['lab_reports']
        supplier_reports = obj['supplier_reports']
        
        status = {
            'incident_created': bool(incident),
            'visit_report_created': len(visit_reports) > 0,
            'lab_report_created': len(lab_reports) > 0,
            'supplier_report_created': len(supplier_reports) > 0,
            'workflow_complete': len(visit_reports) > 0 and len(lab_reports) > 0
        }
        
        return status