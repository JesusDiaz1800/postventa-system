"""
PDF Views for generating PDF documents
"""

import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from .pdf_service import PDFDocumentService
from .models import Document
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_polifusion_lab_report_pdf(request):
    """Generate Polifusión lab report as PDF"""
    try:
        # Validate required fields
        required_fields = ['solicitante', 'cliente', 'proyecto', 'experto_nombre']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare data for PDF generation
        pdf_data = {
            'solicitante': request.data.get('solicitante', ''),
            'fecha_solicitud': request.data.get('fecha_solicitud', ''),
            'cliente': request.data.get('cliente', ''),
            'diametro': request.data.get('diametro', ''),
            'proyecto': request.data.get('proyecto', ''),
            'ubicacion': request.data.get('ubicacion', ''),
            'presion': request.data.get('presion', ''),
            'temperatura': request.data.get('temperatura', ''),
            'informante': request.data.get('informante', ''),
            'ensayos_adicionales': request.data.get('ensayos_adicionales', ''),
            'comentarios_detallados': request.data.get('comentarios_detallados', ''),
            'conclusiones_detalladas': request.data.get('conclusiones_detalladas', ''),
            'experto_nombre': request.data.get('experto_nombre', ''),
            'analisis_detallado': request.data.get('analisis_detallado', ''),
            'incident_code': request.data.get('incident_code', ''),  # Add incident code
        }
        
        # Generate PDF
        pdf_service = PDFDocumentService()
        result = pdf_service.generate_polifusion_lab_report_pdf(pdf_data)
        
        if result['success']:
            # Create document record in database
            try:
                document = Document.objects.create(
                    title=f"Informe de Laboratorio PDF - {pdf_data.get('cliente', 'Cliente')} - {pdf_data.get('proyecto', 'Proyecto')}",
                    document_type='polifusion_lab_report_pdf',
                    content_html=f"<p>Informe de laboratorio PDF generado para {pdf_data.get('cliente')}</p>",
                    pdf_path=result['file_path'],
                    is_final=True,
                    created_by=request.user
                )
                
                return Response({
                    'success': True,
                    'message': 'Informe de laboratorio PDF generado exitosamente',
                    'document_id': document.id,
                    'file_path': result['file_path'],
                    'filename': result['filename'],
                    'file_type': 'pdf'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as db_error:
                return Response({
                    'success': True,
                    'message': 'PDF generado pero no se pudo guardar en la base de datos',
                    'file_path': result['file_path'],
                    'filename': result['filename'],
                    'file_type': 'pdf',
                    'db_error': str(db_error)
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': result.get('error', 'Error desconocido al generar el PDF')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_polifusion_lab_report_pdf: {e}")
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_polifusion_incident_report_pdf(request):
    """Generate Polifusión incident report as PDF"""
    try:
        # Validate required fields
        required_fields = ['proveedor', 'obra', 'cliente', 'descripcion_problema']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare data for PDF generation
        pdf_data = {
            'proveedor': request.data.get('proveedor', ''),
            'obra': request.data.get('obra', ''),
            'cliente': request.data.get('cliente', ''),
            'fecha_deteccion': request.data.get('fecha_deteccion', ''),
            'descripcion_problema': request.data.get('descripcion_problema', ''),
            'acciones_inmediatas': request.data.get('acciones_inmediatas', ''),
            'evolucion_acciones': request.data.get('evolucion_acciones', ''),
            'observaciones': request.data.get('observaciones', ''),
            'incident_code': request.data.get('incident_code', ''),  # Add incident code
        }
        
        # Generate PDF
        pdf_service = PDFDocumentService()
        result = pdf_service.generate_polifusion_incident_report_pdf(pdf_data)
        
        if result['success']:
            # Create document record in database
            try:
                document = Document.objects.create(
                    title=f"Informe de Incidencia PDF - {pdf_data.get('cliente', 'Cliente')} - {pdf_data.get('obra', 'Obra')}",
                    document_type='polifusion_incident_report_pdf',
                    content_html=f"<p>Informe de incidencia PDF generado para {pdf_data.get('cliente')}</p>",
                    pdf_path=result['file_path'],
                    is_final=True,
                    created_by=request.user
                )
                
                return Response({
                    'success': True,
                    'message': 'Informe de incidencia PDF generado exitosamente',
                    'document_id': document.id,
                    'file_path': result['file_path'],
                    'filename': result['filename'],
                    'file_type': 'pdf'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as db_error:
                return Response({
                    'success': True,
                    'message': 'PDF generado pero no se pudo guardar en la base de datos',
                    'file_path': result['file_path'],
                    'filename': result['filename'],
                    'file_type': 'pdf',
                    'db_error': str(db_error)
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': result.get('error', 'Error desconocido al generar el PDF')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_polifusion_incident_report_pdf: {e}")
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_polifusion_visit_report_pdf(request):
    """Generate Polifusión visit report as PDF"""
    try:
        # Validate required fields
        required_fields = ['cliente', 'fecha_visita', 'tecnico_responsable']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare data for PDF generation
        pdf_data = {
            'cliente': request.data.get('cliente', ''),
            'fecha_visita': request.data.get('fecha_visita', ''),
            'tecnico_responsable': request.data.get('tecnico_responsable', ''),
            'tipo_visita': request.data.get('tipo_visita', ''),
            'detalles_visita': request.data.get('detalles_visita', ''),
            'hallazgos': request.data.get('hallazgos', ''),
            'recomendaciones': request.data.get('recomendaciones', ''),
            'proximos_pasos': request.data.get('proximos_pasos', ''),
            'incident_code': request.data.get('incident_code', ''),  # Add incident code
        }
        
        # Generate PDF
        pdf_service = PDFDocumentService()
        result = pdf_service.generate_polifusion_visit_report_pdf(pdf_data)
        
        if result['success']:
            # Create document record in database
            try:
                document = Document.objects.create(
                    title=f"Reporte de Visita PDF - {pdf_data.get('cliente', 'Cliente')} - {pdf_data.get('fecha_visita', '')}",
                    document_type='polifusion_visit_report_pdf',
                    content_html=f"<p>Reporte de visita PDF generado para {pdf_data.get('cliente')}</p>",
                    pdf_path=result['file_path'],
                    is_final=True,
                    created_by=request.user
                )
                
                return Response({
                    'success': True,
                    'message': 'Reporte de visita PDF generado exitosamente',
                    'document_id': document.id,
                    'file_path': result['file_path'],
                    'filename': result['filename'],
                    'file_type': 'pdf'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as db_error:
                return Response({
                    'success': True,
                    'message': 'PDF generado pero no se pudo guardar en la base de datos',
                    'file_path': result['file_path'],
                    'filename': result['filename'],
                    'file_type': 'pdf',
                    'db_error': str(db_error)
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': result.get('error', 'Error desconocido al generar el PDF')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_polifusion_visit_report_pdf: {e}")
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_pdf_document(request, document_id):
    """Serve PDF document for viewing"""
    try:
        document = Document.objects.get(id=document_id, created_by=request.user)
        
        if not document.pdf_path or not os.path.exists(document.pdf_path):
            return Response({
                'error': 'PDF no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(
            open(document.pdf_path, 'rb'),
            content_type='application/pdf',
            as_attachment=False,
            filename=document.title + '.pdf'
        )
        
    except Document.DoesNotExist:
        return Response({
            'error': 'Documento no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error serving PDF document {document_id}: {e}")
        return Response({
            'error': f'Error al servir el PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
