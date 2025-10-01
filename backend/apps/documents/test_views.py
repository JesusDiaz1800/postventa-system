"""
Vistas de prueba para debuggear problemas de autenticación
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .document_generator import document_generator
from .models import Document
from apps.users.models import User

@api_view(['POST'])
@permission_classes([AllowAny])  # Sin autenticación para pruebas
def test_generate_polifusion_lab_report(request):
    """Vista de prueba para generar informe de laboratorio sin autenticación"""
    try:
        # Validate required fields
        required_fields = ['solicitante', 'cliente', 'proyecto', 'experto_nombre']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare incident data for document generation
        incident_data = {
            # Información del solicitante
            'solicitante': request.data.get('solicitante', 'POLIFUSION'),
            'fecha_solicitud': request.data.get('fecha_solicitud', ''),
            'cliente': request.data.get('cliente', 'POLIFUSION'),
            
            # Información técnica
            'diametro': request.data.get('diametro', '160'),
            'proyecto': request.data.get('proyecto', ''),
            'ubicacion': request.data.get('ubicacion', ''),
            'presion': request.data.get('presion', ''),
            'temperatura': request.data.get('temperatura', 'No registrada'),
            'informante': request.data.get('informante', ''),
            
            # Ensayos
            'ensayos_adicionales': request.data.get('ensayos_adicionales', ''),
            
            # Comentarios detallados
            'comentarios_detallados': request.data.get('comentarios_detallados', ''),
            
            # Conclusiones
            'conclusiones_detalladas': request.data.get('conclusiones_detalladas', ''),
            
            # Experto
            'experto_nombre': request.data.get('experto_nombre', ''),
            
            # Análisis detallado
            'analisis_detallado': request.data.get('analisis_detallado', ''),
        }
        
        # Generate document using Polifusión template
        result = document_generator.generate_polifusion_lab_report(incident_data)
        
        if not result['success']:
            return Response({
                'error': f'Error al generar el documento: {result["error"]}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create document record in database
        try:
            # Get or create a default user for test documents
            user, created = User.objects.get_or_create(
                username='system',
                defaults={
                    'email': 'system@polifusion.cl',
                    'first_name': 'Sistema',
                    'last_name': 'Polifusión',
                    'role': 'admin'
                }
            )
            
            document = Document.objects.create(
                title=f"Informe de Laboratorio - {incident_data.get('cliente', 'Cliente')} - {incident_data.get('proyecto', 'Proyecto')}",
                document_type='polifusion_lab_report',
                content_html=f"<p>Informe de laboratorio generado para {incident_data.get('cliente')}</p>",
                docx_path=result['docx_path'],
                pdf_path=result.get('pdf_path'),
                is_final=True,
                created_by=user
            )
            
            return Response({
                'message': 'Informe de laboratorio generado exitosamente',
                'document_id': document.id,
                'filename': result['filename'],
                'docx_path': result['docx_path'],
                'pdf_path': result['pdf_path'],
                'template_used': result['template_used'],
                'debug_info': {
                    'data_received': request.data,
                    'processed_data': incident_data
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as db_error:
            return Response({
                'message': 'Documento generado pero no se pudo guardar en la base de datos',
                'filename': result['filename'],
                'docx_path': result['docx_path'],
                'pdf_path': result['pdf_path'],
                'template_used': result['template_used'],
                'db_error': str(db_error),
                'debug_info': {
                    'data_received': request.data,
                    'processed_data': incident_data
                }
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])  # Sin autenticación para pruebas
def test_generate_polifusion_incident_report(request):
    """Vista de prueba para generar informe de incidencia sin autenticación"""
    try:
        # Validate required fields
        required_fields = ['proveedor', 'obra', 'cliente', 'descripcion_problema']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare incident data for document generation
        incident_data = {
            'proveedor': request.data.get('proveedor', ''),
            'obra': request.data.get('obra', ''),
            'cliente': request.data.get('cliente', ''),
            'fecha_deteccion': request.data.get('fecha_deteccion', ''),
            'descripcion_problema': request.data.get('descripcion_problema', ''),
            'acciones_inmediatas': request.data.get('acciones_inmediatas', ''),
            'evolucion_acciones': request.data.get('evolucion_acciones', ''),
            'observaciones': request.data.get('observaciones', ''),
        }
        
        # Generate document using Polifusión template
        result = document_generator.generate_polifusion_incident_report(incident_data)
        
        if not result['success']:
            return Response({
                'error': f'Error al generar el documento: {result["error"]}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Create document record in database
        try:
            # Get or create a default user for test documents
            user, created = User.objects.get_or_create(
                username='system',
                defaults={
                    'email': 'system@polifusion.cl',
                    'first_name': 'Sistema',
                    'last_name': 'Polifusión',
                    'role': 'admin'
                }
            )
            
            document = Document.objects.create(
                title=f"Informe de Incidencia - {incident_data.get('cliente', 'Cliente')} - {incident_data.get('obra', 'Obra')}",
                document_type='polifusion_incident_report',
                content_html=f"<p>Informe de incidencia generado para {incident_data.get('cliente')}</p>",
                docx_path=result['docx_path'],
                pdf_path=result.get('pdf_path'),
                is_final=True,
                created_by=user
            )
            
            return Response({
                'message': 'Informe de incidencia generado exitosamente',
                'document_id': document.id,
                'filename': result['filename'],
                'docx_path': result['docx_path'],
                'pdf_path': result['pdf_path'],
                'template_used': result['template_used'],
                'debug_info': {
                    'data_received': request.data,
                    'processed_data': incident_data
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as db_error:
            return Response({
                'message': 'Documento generado pero no se pudo guardar en la base de datos',
                'filename': result['filename'],
                'docx_path': result['docx_path'],
                'pdf_path': result['pdf_path'],
                'template_used': result['template_used'],
                'db_error': str(db_error),
                'debug_info': {
                    'data_received': request.data,
                    'processed_data': incident_data
                }
            }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
