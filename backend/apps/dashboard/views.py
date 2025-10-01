from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.incidents.dashboard_metrics import dashboard_metrics
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_metrics(request):
    """
    Obtener métricas generales del dashboard
    """
    try:
        # Obtener métricas del dashboard
        metrics = dashboard_metrics.get_comprehensive_dashboard()
        
        return Response({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas del dashboard: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error obteniendo métricas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
