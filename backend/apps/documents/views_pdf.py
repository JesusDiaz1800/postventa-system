from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
import os
import logging
from .services.professional_pdf_generator import ProfessionalPDFGenerator
from .services.document_validation import DocumentValidationService

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_visit_report_pdf(request):
    """
    Generar PDF profesional para reporte de visita y guardarlo en carpeta compartida
    """
    try:
        # Obtener datos del formulario
        form_data = request.data
        incident_id = form_data.get('related_incident_id')
        
        # Validar que no existe ya un reporte de visita para esta incidencia
        if incident_id:
            can_create, message = DocumentValidationService.can_create_visit_report(incident_id)
            if not can_create:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Obtener imágenes si las hay
        images = []
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')
        
        # Crear generador de PDF ultimate profesional
        pdf_generator = ProfessionalPDFGenerator()
        
        # Generar PDF
        pdf_content = pdf_generator.generate_visit_report_pdf(form_data, "temp_visit_report.pdf")
        
        # Guardar PDF en carpeta compartida
        incident_id = form_data.get('related_incident_id')
        order_number = form_data.get('order_number', 'sin_numero')
        filename = f"{order_number}.pdf"
        
        if incident_id:
            # Importar función de sincronización
            from .views_upload import sync_to_shared_folder
            
            # Crear archivo temporal
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                # Convertir BytesIO a bytes si es necesario
                if hasattr(pdf_content, 'getvalue'):
                    pdf_bytes = pdf_content.getvalue()
                else:
                    pdf_bytes = pdf_content
                temp_file.write(pdf_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Sincronizar a carpeta compartida
                shared_path = sync_to_shared_folder(
                    temp_file_path, 
                    'visit-report', 
                    incident_id, 
                    filename
                )
                
                if shared_path:
                    logger.info(f"PDF guardado en carpeta compartida: {shared_path}")
                else:
                    logger.warning("No se pudo guardar PDF en carpeta compartida")
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        # Crear respuesta HTTP con el PDF
        # Usar los bytes correctos para la respuesta
        if hasattr(pdf_content, 'getvalue'):
            pdf_bytes = pdf_content.getvalue()
        else:
            pdf_bytes = pdf_content
            
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_visita_{order_number}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de visita: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error generando PDF: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_lab_report_client_pdf(request):
    """
    Generar PDF profesional para reporte de laboratorio para cliente
    """
    try:
        form_data = request.data
        incident_id = form_data.get('related_incident_id')
        
        # Validar que no existe ya un reporte de laboratorio para esta incidencia
        if incident_id:
            can_create, message = DocumentValidationService.can_create_lab_report(incident_id)
            if not can_create:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        images = []
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')
        
        pdf_generator = ProfessionalPDFGenerator()
        pdf_content = pdf_generator.generate_lab_report_client_pdf(form_data, "temp_lab_report_client.pdf")
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_laboratorio_cliente_{form_data.get("report_number", "sin_numero")}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de laboratorio para cliente: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error generando PDF: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_lab_report_internal_pdf(request):
    """
    Generar PDF profesional para reporte de laboratorio interno
    """
    try:
        form_data = request.data
        incident_id = form_data.get('related_incident_id')
        
        # Validar que no existe ya un reporte de laboratorio para esta incidencia
        if incident_id:
            can_create, message = DocumentValidationService.can_create_lab_report(incident_id)
            if not can_create:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        images = []
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')
        
        pdf_generator = ProfessionalPDFGenerator()
        pdf_content = pdf_generator.generate_lab_report_internal_pdf(form_data, "temp_lab_report_internal.pdf")
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_laboratorio_interno_{form_data.get("report_number", "sin_numero")}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de laboratorio interno: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error generando PDF: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_supplier_report_pdf(request):
    """
    Generar PDF profesional para reporte de proveedor
    """
    try:
        form_data = request.data
        images = []
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')
        
        pdf_generator = ProfessionalPDFGenerator()
        pdf_content = pdf_generator.generate_supplier_report_pdf(form_data, "temp_supplier_report.pdf")
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_proveedor_{form_data.get("report_number", "sin_numero")}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de proveedor: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error generando PDF: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quality_report_pdf(request):
    """
    Generar PDF profesional para reporte de calidad
    """
    try:
        form_data = request.data
        images = []
        if 'images' in request.FILES:
            images = request.FILES.getlist('images')
        
        pdf_generator = ProfessionalPDFGenerator()
        pdf_content = pdf_generator.generate_quality_report_pdf(form_data, "temp_quality_report.pdf")
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_calidad_{form_data.get("report_number", "sin_numero")}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generando PDF de reporte de calidad: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error generando PDF: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_incident_documents_status(request, incident_id):
    """
    Obtener el estado de todos los documentos de una incidencia
    """
    try:
        status = DocumentValidationService.get_incident_documents_status(incident_id)
        
        if status is None:
            return Response(
                {'error': 'Incidencia no encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status)
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de documentos: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Error obteniendo estado: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )