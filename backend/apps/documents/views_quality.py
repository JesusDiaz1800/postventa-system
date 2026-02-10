"""
Vistas para reportes de calidad
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
import logging

from .models import QualityReport, SupplierReport, DocumentStatus
from .serializers_quality import (
    QualityReportSerializer, 
    QualityReportCreateSerializer, 
    QualityReportUpdateSerializer
)
from apps.incidents.models import Incident

logger = logging.getLogger(__name__)

class QualityReportListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear reportes de calidad
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QualityReportCreateSerializer
        return QualityReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = QualityReport.objects.select_related(
            'related_incident', 
            'created_by',
            'related_incident__categoria',
            'related_incident__responsable',
            'related_incident__created_by'
        )
        
        # Filtrar por tipo de reporte si se especifica
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        # Filtrar por incidencia si se especifica
        incident_id = self.request.query_params.get('incident_id')
        if incident_id:
            queryset = queryset.filter(related_incident_id=incident_id)
        
        # Filtrar por estado si se especifica
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Búsqueda general (100% funcional)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(report_number__icontains=search_query) |
                Q(report_type__icontains=search_query) |
                Q(related_incident__code__icontains=search_query) |
                Q(related_incident__cliente__icontains=search_query) |
                Q(related_incident__obra__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        from .models import DocumentAttachment
        report = serializer.save(created_by=self.request.user)
        
        # Procesar imágenes por sección específica
        sections = ['product', 'site_conditions', 'test_protocol', 'lab_tests', 'conclusions']
        for section in sections:
            img = self.request.FILES.get(f'image_{section}')
            if img:
                DocumentAttachment.objects.create(
                    document_type='quality_report',
                    document_id=report.id,
                    file=img,
                    filename=img.name,
                    file_type=img.content_type,
                    file_size=img.size,
                    section=section,
                    description=f"Imagen técnica para sección {section}",
                    uploaded_by=self.request.user
                )
        
        # Procesar imágenes generales (galería)
        general_images = self.request.FILES.getlist('images')
        for img in general_images:
            DocumentAttachment.objects.create(
                document_type='quality_report',
                document_id=report.id,
                file=img,
                filename=img.name,
                file_type=img.content_type,
                file_size=img.size,
                section='general',
                description="Imagen de galería",
                uploaded_by=self.request.user
            )

class QualityReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar un reporte de calidad específico
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return QualityReportUpdateSerializer
        return QualityReportSerializer
    
    def get_queryset(self):
        return QualityReport.objects.select_related(
            'related_incident', 
            'created_by',
            'related_incident__categoria',
            'related_incident__responsable',
            'related_incident__created_by'
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quality_reports_by_incident(request, incident_id):
    """
    Obtener todos los reportes de calidad de una incidencia específica
    """
    try:
        incident = get_object_or_404(Incident, id=incident_id)
        reports = QualityReport.objects.filter(
            related_incident=incident
        ).select_related(
            'created_by',
            'related_incident',
            'related_incident__categoria',
            'related_incident__responsable',
            'related_incident__created_by'
        ).order_by('-created_at')
        
        serializer = QualityReportSerializer(reports, many=True)
        
        return Response({
            'success': True,
            'incident': {
                'id': incident.id,
                'code': incident.code,
                'cliente': incident.cliente,
                'sku': incident.sku
            },
            'reports': serializer.data,
            'total': reports.count()
        })
        
    except Exception as e:
        logger.error(f"Error al obtener reportes de calidad: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quality_reports_summary(request):
    """
    Obtener resumen de reportes de calidad
    """
    try:
        # Estadísticas generales
        total_reports = QualityReport.objects.count()
        cliente_reports = QualityReport.objects.filter(report_type='cliente').count()
        interno_reports = QualityReport.objects.filter(report_type='interno').count()
        
        # Reportes por estado
        status_stats = {}
        for status_choice in QualityReport._meta.get_field('status').choices:
            status_key = status_choice[0]
            status_count = QualityReport.objects.filter(status=status_key).count()
            status_stats[status_key] = status_count
        
        # Reportes recientes
        recent_reports = QualityReport.objects.select_related(
            'related_incident', 
            'created_by',
            'related_incident__categoria',
            'related_incident__responsable',
            'related_incident__created_by'
        ).order_by('-created_at')[:5]
        
        recent_serializer = QualityReportSerializer(recent_reports, many=True)
        
        return Response({
            'success': True,
            'summary': {
                'total_reports': total_reports,
                'cliente_reports': cliente_reports,
                'interno_reports': interno_reports,
                'status_stats': status_stats
            },
            'recent_reports': recent_serializer.data
        })
        
    except Exception as e:
        logger.error(f"Error al obtener resumen de reportes: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quality_report_document(request, report_id):
    """
    Generar documento PDF para un reporte de calidad
    """
    try:
        from django.conf import settings
        from .services.professional_pdf_generator import ProfessionalPDFGenerator
        import os
        
        report = get_object_or_404(QualityReport, id=report_id)
        incident = report.related_incident
        
        # Preparar datos completos para el PDF
        pdf_data = {
            # Información del reporte
            'report_id': report.id,
            'report_number': report.report_number,
            'report_type': report.get_report_type_display(),
            'title': report.title,
            'date_created': report.date_created.strftime('%d/%m/%Y') if report.date_created else '',
            'status': report.status,
            'created_by': str(report.created_by) if report.created_by else 'Sistema',
            
            # Información de la incidencia
            'incident_code': incident.code if incident else '',
            'cliente': incident.cliente if incident else '',
            'provider': incident.provider if incident else '',
            'obra': incident.obra if incident else '',
            'sku': incident.sku if incident else '',
            'categoria': str(incident.categoria) if incident and incident.categoria else '',
            'subcategoria': incident.subcategoria if incident else '',
            'descripcion_incidencia': incident.descripcion if incident else '',
            
            # Contenido del reporte de calidad
            'executive_summary': report.executive_summary,
            'problem_description': report.problem_description,
            'root_cause_analysis': report.root_cause_analysis,
            'corrective_actions': report.corrective_actions,
            'preventive_measures': report.preventive_measures,
            'recommendations': report.recommendations,
            'technical_details': report.technical_details,
            'internal_notes': report.internal_notes if report.report_type == 'interno' else '',
        }
        
        # Generar PDF
        pdf_generator = ProfessionalPDFGenerator()
        
        # Determinar ruta de guardado
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None) or getattr(settings, 'MEDIA_ROOT', '')
        report_type_folder = 'quality_reports_cliente' if report.report_type == 'cliente' else 'quality_reports_interno'
        incident_folder = os.path.join(shared_path, report_type_folder, f'incident_{incident.id}' if incident else 'general')
        os.makedirs(incident_folder, exist_ok=True)
        
        pdf_filename = f"{report.report_number}.pdf"
        pdf_path = os.path.join(incident_folder, pdf_filename)
        
        # Generar el PDF
        success = pdf_generator.generate_quality_report(pdf_data, pdf_path)
        
        if success:
            # Actualizar ruta en el reporte
            report.pdf_path = pdf_path
            report.save(update_fields=['pdf_path'])
            
            return Response({
                'success': True,
                'message': f'Documento PDF generado exitosamente',
                'report_id': report.id,
                'report_number': report.report_number,
                'pdf_path': pdf_path,
                'filename': pdf_filename
            })
        else:
            return Response({
                'success': False,
                'error': 'Error al generar el documento PDF'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error al generar documento de calidad: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_quality_report_document(request):
    """
    Subir documento adjunto para un reporte de calidad
    """
    try:
        from django.conf import settings
        import os
        
        incident_id = request.data.get('incident_id')
        # Obtener report_type de request.data (DRF unifica POST y FILES)
        report_type = request.data.get('report_type', 'cliente')
        
        logger.info(f"Upload Quality Report Request - Type: {report_type} - Incident: {incident_id} - Data keys: {list(request.data.keys())}")
        uploaded_file = request.FILES.get('file')
        
        if not incident_id:
            return Response({'error': 'ID de incidencia requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not uploaded_file:
            return Response({'error': 'Archivo requerido'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener incidencia
        incident = get_object_or_404(Incident, id=incident_id)
        
        # Verificar si ya existe un reporte de calidad para esta incidencia y tipo
        existing_report = QualityReport.objects.filter(
            related_incident=incident,
            report_type=report_type
        ).first()
        
        # Determinar ruta de guardado
        shared_path = getattr(settings, 'SHARED_DOCUMENTS_PATH', None) or getattr(settings, 'MEDIA_ROOT', '')
        report_type_folder = 'quality_reports_cliente' if report_type == 'cliente' else 'quality_reports_interno'
        incident_folder = os.path.join(shared_path, report_type_folder, f'incident_{incident.id}')
        os.makedirs(incident_folder, exist_ok=True)
        
        # Guardar archivo
        file_name = uploaded_file.name
        file_path = os.path.join(incident_folder, file_name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Crear o actualizar reporte de calidad
        if existing_report:
            existing_report.pdf_path = file_path
            existing_report.save(update_fields=['pdf_path'])
            report = existing_report
        else:
            # Crear nuevo reporte con datos mínimos
            report = QualityReport.objects.create(
                related_incident=incident,
                report_type=report_type,
                title=f'Reporte de Calidad - {incident.code}',
                executive_summary='Documento adjuntado manualmente',
                problem_description=incident.descripcion or 'Ver documento adjunto',
                root_cause_analysis='Ver documento adjunto',
                corrective_actions='Ver documento adjunto',
                preventive_measures='Ver documento adjunto',
                recommendations='Ver documento adjunto',
                pdf_path=file_path,
                created_by=request.user,
                status='approved'
            )
        
        logger.info(f"Documento de calidad subido: {file_path}")
        
        return Response({
            'success': True,
            'message': 'Documento adjuntado exitosamente',
            'report_id': report.id,
            'report_number': report.report_number,
            'file_path': file_path
        })
        
    except Exception as e:
        logger.error(f"Error subiendo documento de calidad: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error al subir documento: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def internal_quality_reports(request):
    """
    Obtiene reportes de calidad internos con datos de incidencia completos
    """
    try:
        # Filtrar reportes de calidad internos
        # Filtrar reportes de calidad internos que han sido escalados explícitamente a calidad interna
        reports = QualityReport.objects.filter(
            report_type='interno',
            related_incident__escalated_to_internal_quality=True
        ).select_related(
            'related_incident', 
            'created_by',
            'related_incident__categoria',
            'related_incident__responsable',
            'related_incident__created_by'
        ).order_by('-created_at')
        
        # Búsqueda general (100% funcional)
        search_query = request.query_params.get('search')
        if search_query:
            reports = reports.filter(
                Q(report_number__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(related_incident__code__icontains=search_query) |
                Q(related_incident__cliente__icontains=search_query) |
                Q(related_incident__obra__icontains=search_query)
            )
        
        # Serializar datos usando el serializer estándar que incluye download_url y filename
        serializer = QualityReportSerializer(reports, many=True)
        
        return Response({
            'success': True,
            'reports': serializer.data,
            'count': reports.count()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo reportes de calidad internos: {str(e)}")
        return Response(
            {'error': f'Error obteniendo reportes: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def escalate_to_supplier(request, pk):
    """
    Escalar un reporte de calidad a proveedor (Solo cambia estado, NO crea reporte automático)
    """
    try:
        report = get_object_or_404(QualityReport, pk=pk)
        incident = report.related_incident
        
        # 1. Actualizar Reporte de Calidad
        report.status = 'escalated'
        report.save()
        
        # 2. Actualizar Incidencia
        incident.escalated_to_supplier = True
        incident.escalation_date = timezone.now()
        incident.escalation_reason = f"Escalado desde Reporte de Calidad {report.report_number}"
        incident.save(update_fields=['escalated_to_supplier', 'escalation_date', 'escalation_reason'])
        
        return Response({
            'success': True,
            'message': 'Reporte escalado a proveedor exitosamente (Estado actualizado)',
            'report_id': report.id
        })
        
    except Exception as e:
        logger.error(f"Error escalando a proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_quality_report_email(request, pk):
    """
    Registrar envío de reporte de calidad (Log Only - Outlook Workflow)
    """
    try:
        report = get_object_or_404(QualityReport, pk=pk)
        
        # 1. Obtener email del cliente (solo para validación)
        to_email = request.data.get('to')
        
        if not to_email:
            return Response(
                {'error': 'No hay correo del cliente definido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Registrar acción (sin enviar correo real)
        logger.info(f"Registrando envío manual de reporte de calidad {pk} a {to_email}")
        
        # 3. Actualizar solo el estado (QualityReport no tiene client_email ni sent_date)
        if report.status != 'completed' and report.status != 'closed':
            report.status = 'sent'
            report.save(update_fields=['status'])
        
        return Response({
            'success': True,
            'message': 'Estado actualizado. El correo debe ser enviado manualmente desde Outlook.',
            'logged_to': to_email
        })
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Error registrando envío de reporte de calidad: {e}\n{tb}", exc_info=True)
        return Response(
            {'error': f'Error interno al registrar estado: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_quality_report(request, pk):
    """
    Descargar el archivo para un reporte de calidad (inline)
    """
    import os
    from django.http import FileResponse
    
    try:
        report = get_object_or_404(QualityReport, pk=pk)
        
        if not report.pdf_path:
            return Response(
                {'error': 'Este reporte no tiene un PDF generado o adjunto'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        if not os.path.exists(report.pdf_path):
            return Response(
                {'error': 'El archivo físico no se encuentra en el servidor'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Abrir y servir el archivo
        file_handle = open(report.pdf_path, 'rb')
        response = FileResponse(
            file_handle,
            content_type='application/pdf',
            as_attachment=False
        )
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(report.pdf_path)}"'
        return response
        
    except Exception as e:
        logger.error(f"Error descargando reporte de calidad: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error interno descargando archivo: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
