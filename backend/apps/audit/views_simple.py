"""
Vistas simples para el sistema de auditoría
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_logs_list_simple(request):
    """Lista simple de logs de auditoría"""
    try:
        # Por ahora, devolver datos de prueba
        sample_logs = [
            {
                'id': 1,
                'user': 'admin',
                'action': 'login',
                'resource_type': 'system',
                'resource_id': '1',
                'details': 'Usuario inició sesión en el sistema',
                'ip_address': '127.0.0.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'created_at': '2025-09-29T13:30:00Z'
            },
            {
                'id': 2,
                'user': 'admin',
                'action': 'create',
                'resource_type': 'incident',
                'resource_id': '1',
                'details': 'Creó nueva incidencia INC-2025-0001',
                'ip_address': '127.0.0.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'created_at': '2025-09-29T13:31:00Z'
            },
            {
                'id': 3,
                'user': 'admin',
                'action': 'upload',
                'resource_type': 'document',
                'resource_id': '1',
                'details': 'Subió documento de reporte de visita',
                'ip_address': '127.0.0.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'created_at': '2025-09-29T13:32:00Z'
            }
        ]
        
        return Response({
            'success': True,
            'results': sample_logs,
            'count': len(sample_logs),
            'page': 1,
            'page_size': 50,
            'total_pages': 1
        })
        
    except Exception as e:
        logger.error(f"Error en audit_logs_list_simple: {e}")
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
