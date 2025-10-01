"""
Vistas para trazabilidad documental completa
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
import logging

from .models import VisitReport, LabReport, SupplierReport
from .serializers import (
    VisitReportSerializer, VisitReportCreateSerializer, VisitReportListSerializer,
    LabReportSerializer, LabReportCreateSerializer,
    SupplierReportSerializer, SupplierReportCreateSerializer,
    DocumentWorkflowSerializer
)

logger = logging.getLogger(__name__)

# ==================== REPORTES DE VISITA ====================

class VisitReportListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea reportes de visita
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = []
    search_fields = ['report_number', 'project_name', 'client_name', 'order_number']
    ordering_fields = ['visit_date', 'created_at', 'report_number']
    ordering = ['-visit_date']
    
    def get_queryset(self):
        queryset = VisitReport.objects.select_related('related_incident', 'created_by').all()
        
        # Filtrar por incidencia relacionada
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(related_incident_id=incident_id)
        
        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VisitReportCreateSerializer
        return VisitReportListSerializer
    
    def perform_create(self, serializer):
        # Validar que no exista ya un reporte de visita para esta incidencia
        related_incident = serializer.validated_data.get('related_incident')
        if related_incident:
            existing_report = VisitReport.objects.filter(related_incident=related_incident).first()
            if existing_report:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'related_incident': f'Ya existe un reporte de visita para la incidencia {related_incident.code}. '
                                      f'Reporte existente: {existing_report.report_number}'
                })
        
        # Crear el reporte
        report = serializer.save(created_by=self.request.user)
        
        # Generar PDF automáticamente después de crear el reporte
        try:
            from .services.professional_pdf_generator import ProfessionalPDFGenerator
            from django.conf import settings
            import os
            
            # Preparar datos para el PDF
            pdf_data = {
                'order_number': report.order_number,
                'client_name': report.client_name,
                'project_name': report.project_name,
                'address': report.address,
                'commune': getattr(report, 'commune', ''),
                'city': getattr(report, 'city', ''),
                'visit_date': report.visit_date.strftime('%d/%m/%Y') if report.visit_date else '',
                'salesperson': report.salesperson,
                'technician': report.technician,
                'product_category': getattr(report, 'product_category', ''),
                'product_subcategory': getattr(report, 'product_subcategory', ''),
                'product_sku': getattr(report, 'product_sku', ''),
                'product_lot': getattr(report, 'product_lot', ''),
                'product_provider': getattr(report, 'product_provider', ''),
                'visit_reason': report.visit_reason,
                'general_observations': report.general_observations,
                'wall_observations': report.wall_observations,
                'matrix_observations': report.matrix_observations,
                'slab_observations': report.slab_observations,
                'storage_observations': report.storage_observations,
                'pre_assembled_observations': report.pre_assembled_observations,
                'exterior_observations': report.exterior_observations,
                'machine_data': report.machine_data
            }
            
            # Generar PDF
            pdf_generator = ProfessionalPDFGenerator()
            
            # Guardar PDF en carpeta compartida
            shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None)
            if shared_path:
                incident_folder = os.path.join(shared_path, 'visit_reports', f'incident_{report.related_incident.id}')
                os.makedirs(incident_folder, exist_ok=True)
                
                pdf_path = os.path.join(incident_folder, f"{report.order_number}.pdf")
                pdf_content = pdf_generator.generate_visit_report_pdf(pdf_data, pdf_path)
                
                if pdf_content:
                    logger.info(f"PDF generado automáticamente: {pdf_path}")
                else:
                    logger.error("Error generando PDF profesional")
            
        except Exception as e:
            logger.error(f"Error generando PDF automáticamente: {str(e)}", exc_info=True)
            # No fallar la creación del reporte si hay error en el PDF

class VisitReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtiene, actualiza o elimina un reporte de visita específico
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VisitReport.objects.select_related('related_incident', 'created_by').all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VisitReportCreateSerializer
        return VisitReportSerializer

# ==================== INFORMES DE LABORATORIO ====================

class LabReportListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea informes de laboratorio
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = []
    search_fields = ['report_number', 'client', 'applicant']
    ordering_fields = ['request_date', 'created_at', 'report_number']
    ordering = ['-request_date']
    
    def get_queryset(self):
        queryset = LabReport.objects.select_related(
            'related_incident', 'related_visit_report', 'created_by'
        ).all()
        
        # Filtrar por incidencia relacionada
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(related_incident_id=incident_id)
        
        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LabReportCreateSerializer
        return LabReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class LabReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtiene, actualiza o elimina un informe de laboratorio específico
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LabReport.objects.select_related(
            'related_incident', 'related_visit_report', 'created_by'
        ).all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return LabReportCreateSerializer
        return LabReportSerializer

# ==================== INFORMES PARA PROVEEDORES ====================

class SupplierReportListCreateView(generics.ListCreateAPIView):
    """
    Lista y crea informes para proveedores
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = []
    search_fields = ['report_number', 'supplier_name', 'subject']
    ordering_fields = ['report_date', 'created_at', 'report_number']
    ordering = ['-report_date']
    
    def get_queryset(self):
        queryset = SupplierReport.objects.select_related(
            'related_incident', 'related_lab_report', 'created_by'
        ).all()
        
        # Filtrar por incidencia relacionada
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(related_incident_id=incident_id)
        
        # Filtrar por estado
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SupplierReportCreateSerializer
        return SupplierReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class SupplierReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Obtiene, actualiza o elimina un informe para proveedor específico
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SupplierReport.objects.select_related(
            'related_incident', 'related_lab_report', 'created_by'
        ).all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SupplierReportCreateSerializer
        return SupplierReportSerializer

# ==================== WORKFLOW Y TRAZABILIDAD ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def incident_workflow(request, incident_id):
    """
    Obtiene el workflow completo de un incidente
    """
    try:
        from apps.incidents.models import Incident
        incident = get_object_or_404(Incident, id=incident_id)
        
        visit_reports = VisitReport.objects.filter(related_incident=incident)
        lab_reports = LabReport.objects.filter(related_incident=incident)
        supplier_reports = SupplierReport.objects.filter(related_incident=incident)
        
        workflow_data = {
            'incident': incident,
            'visit_reports': visit_reports,
            'lab_reports': lab_reports,
            'supplier_reports': supplier_reports
        }
        
        serializer = DocumentWorkflowSerializer(workflow_data)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting incident workflow: {e}")
        return Response(
            {'error': 'Error al obtener el workflow del incidente'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_incidents(request):
    """
    Obtiene las incidencias disponibles para vincular con documentos
    """
    try:
        from apps.incidents.models import Incident
        from apps.incidents.serializers import IncidentListSerializer
        
        # Obtener incidencias abiertas o en proceso
        incidents = Incident.objects.filter(
            Q(status='open') | Q(status='in_progress')
        ).order_by('-created_at')
        
        serializer = IncidentListSerializer(incidents, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error getting available incidents: {e}")
        return Response(
            {'error': 'Error al obtener las incidencias disponibles'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_statistics(request):
    """
    Obtiene estadísticas de documentos
    """
    try:
        stats = {
            'visit_reports': {
                'total': VisitReport.objects.count(),
                'draft': VisitReport.objects.filter(status='draft').count(),
                'approved': VisitReport.objects.filter(status='approved').count(),
                'sent': VisitReport.objects.filter(status='sent').count(),
            },
            'lab_reports': {
                'total': LabReport.objects.count(),
                'draft': LabReport.objects.filter(status='draft').count(),
                'approved': LabReport.objects.filter(status='approved').count(),
                'sent': LabReport.objects.filter(status='sent').count(),
            },
            'supplier_reports': {
                'total': SupplierReport.objects.count(),
                'draft': SupplierReport.objects.filter(status='draft').count(),
                'approved': SupplierReport.objects.filter(status='approved').count(),
                'sent': SupplierReport.objects.filter(status='sent').count(),
            }
        }
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error getting document statistics: {e}")
        return Response(
            {'error': 'Error al obtener estadísticas de documentos'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
