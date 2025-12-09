"""
Vistas para reportes de calidad
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
import logging

from .models import QualityReport
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
        queryset = QualityReport.objects.select_related('related_incident', 'created_by')
        
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
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
        return QualityReport.objects.select_related('related_incident', 'created_by')

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
        ).select_related('created_by').order_by('-created_at')
        
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
            'related_incident', 'created_by'
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
    Generar documento PDF/DOCX para un reporte de calidad
    """
    try:
        report = get_object_or_404(QualityReport, id=report_id)
        
        # Aquí se implementaría la generación del documento
        # Por ahora, solo retornamos un mensaje de éxito
        
        return Response({
            'success': True,
            'message': f'Documento generado exitosamente para {report.report_number}',
            'report_id': report.id,
            'report_number': report.report_number,
            'report_type': report.get_report_type_display()
        })
        
    except Exception as e:
        logger.error(f"Error al generar documento: {str(e)}")
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
<<<<<<< HEAD
=======

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def internal_quality_reports(request):
    """
    Obtiene reportes de calidad internos
    """
    try:
        # Filtrar reportes de calidad internos
        reports = QualityReport.objects.filter(
            report_type='interno'
        ).select_related('related_incident', 'created_by').order_by('-created_at')
        
        # Serializar datos
        reports_data = []
        for report in reports:
            reports_data.append({
                'id': report.id,
                'report_number': report.report_number,
                'report_type': report.report_type,
                'status': report.status,
                'created_at': report.created_at,
                'created_by': report.created_by.username if report.created_by else None,
                'related_incident': {
                    'id': report.related_incident.id,
                    'code': report.related_incident.code,
                    'cliente': report.related_incident.cliente,
                    'provider': report.related_incident.provider,
                } if report.related_incident else None
            })
        
        return Response({
            'success': True,
            'reports': reports_data,
            'count': len(reports_data)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo reportes de calidad internos: {str(e)}")
        return Response(
            {'error': f'Error obteniendo reportes: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
>>>>>>> 674c244 (tus cambios)
