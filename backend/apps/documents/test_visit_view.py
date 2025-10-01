"""
Vista de prueba para informe de visita
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .document_generator import document_generator

@api_view(['POST'])
@permission_classes([AllowAny])  # Sin autenticación para pruebas
def test_generate_polifusion_visit_report(request):
    """Vista de prueba para generar informe de visita sin autenticación"""
    try:
        # Validate required fields
        required_fields = ['obra', 'cliente', 'vendedor', 'tecnico']
        for field in required_fields:
            if not request.data.get(field):
                return Response({
                    'error': f'El campo {field} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare visit data for document generation
        visit_data = {
            'obra': request.data.get('obra', ''),
            'cliente': request.data.get('cliente', ''),
            'vendedor': request.data.get('vendedor', ''),
            'tecnico': request.data.get('tecnico', ''),
            'fecha_visita': request.data.get('fecha_visita', ''),
            'personal_info': request.data.get('personal_info', ''),
            'roles_contactos': request.data.get('roles_contactos', ''),
            'maquinaria_uso': request.data.get('maquinaria_uso', ''),
            'observaciones_instalacion': request.data.get('observaciones_instalacion', ''),
            'observaciones_material': request.data.get('observaciones_material', ''),
            'observaciones_tecnico': request.data.get('observaciones_tecnico', ''),
            'observaciones_general': request.data.get('observaciones_general', ''),
            'firma_vendedor': request.data.get('firma_vendedor', ''),
            'firma_tecnico': request.data.get('firma_tecnico', ''),
        }
        
        # Generate document using Polifusión template
        result = document_generator.generate_polifusion_visit_report(visit_data)
        
        if not result['success']:
            return Response({
                'error': f'Error al generar el documento: {result["error"]}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': 'Informe de visita generado exitosamente (modo prueba)',
            'filename': result['filename'],
            'docx_path': result['docx_path'],
            'pdf_path': result['pdf_path'],
            'template_used': result['template_used'],
            'debug_info': {
                'data_received': request.data,
                'processed_data': visit_data
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
